#!/usr/bin/env python3
"""Read-only, opt-in lab probe for the proposed vSphere RDM topology pack.

The default is offline plan output. A live read requires both --execute and
--allow-read-only-lab. Credentials remain environment-only. Reporting modes
emit fingerprints, never raw inventory values; explicit fixture-export writes
validated identities only to its fixed, ignored, owner-only local handoff.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import hashlib
import json
import logging
import os
import shutil
import socket
import ssl
import stat
import subprocess
import sys
import tempfile
import time
import warnings
from pathlib import Path
from typing import Any, Iterable, Optional


SCHEMA_VERSION = "vcfcf-rdm-lab-probe-v1"
OPS_VM_DISCOVERY_PAGE_SIZE = 1000
OPS_VM_DISCOVERY_MAX_PAGES = 10000


class FieldReadError(RuntimeError):
    """A retrieved VIM object could not expose a requested field safely."""


class PropertyCollectionError(RuntimeError):
    """A PropertyCollector response was incomplete for the requested objects."""


class OperationsShapeError(RuntimeError):
    """A public Operations response did not have its documented read shape."""


class OperationsDiscoveryError(RuntimeError):
    """Operations VM discovery could not establish a complete candidate set."""


class FixtureExportError(RuntimeError):
    """Internal detail/cause is never rendered by the CLI; only allowlisted codes."""

    STAGES = frozenset({"UNCLASSIFIED", "CONFIGURATION", "VCENTER_CONFIGURATION",
        "OPS_CONFIGURATION", "VCENTER_SESSION", "VCENTER_CONNECTION", "VCENTER_AUTHENTICATION",
        "VCENTER_READ", "OPS_CONNECTION", "OPS_AUTHENTICATION", "OPS_AUTHORIZATION", "OPS_READ",
        "VM_IDENTITY_CORRELATION", "RDM_AMBIGUITY", "FIXTURE_SCHEMA_VALIDATION",
        "JAVA_PARSER_SETUP", "JAVA_PARSER_VALIDATION", "OUTPUT_FILE"})
    CODES = frozenset({"FAILED", "MISSING_CONFIGURATION", "SDK_UNAVAILABLE", "JAVA_UNAVAILABLE",
        "PARSER_SOURCE_UNAVAILABLE", "COMPILE_FAILED", "PARSER_REJECTED", "TIMEOUT",
        "TRANSPORT_ERROR", "AUTH_REJECTED", "HTTP_ERROR", "NO_RDM", "MULTIPLE_RDMS",
        "UNSUPPORTED_PROFILE", "RESOURCE_NOT_OBJECT", "RESOURCE_KEY_MISSING", "RESOURCE_KEY_NOT_OBJECT",
        "ADAPTER_KIND_INVALID", "RESOURCE_KIND_INVALID", "RESOURCE_NAME_MISSING", "RESOURCE_NAME_INVALID",
        "IDENTIFIERS_MISSING", "IDENTIFIERS_NOT_ARRAY", "IDENTIFIERS_EMPTY", "IDENTIFIER_NOT_OBJECT",
        "IDENTIFIER_TYPE_MISSING", "IDENTIFIER_TYPE_NOT_OBJECT", "IDENTIFIER_NAME_MISSING",
        "IDENTIFIER_NAME_INVALID", "IDENTIFIER_NAME_DUPLICATE", "IDENTIFIER_VALUE_MISSING",
        "IDENTIFIER_VALUE_NULL", "IDENTIFIER_VALUE_NOT_STRING", "IDENTIFIER_VALUE_EMPTY",
        "IDENTIFIER_UNIQUENESS_MISSING", "IDENTIFIER_UNIQUENESS_NOT_BOOLEAN",
        "VM_DEVICES_NOT_ARRAY", "RDM_LUN_IDENTITY_INVALID", "RDM_DISK_KEY_INVALID",
        "OPS_RESPONSE_JSON_INVALID", "FIXTURE_SERIALIZATION_FAILED"})
    # Structural schema paths only: never interpolate a returned identifier name,
    # value, resource ID, list index, fingerprint or exception text.
    FIELDS = frozenset({"resource", "resource.resourceKey", "resource.resourceKey.adapterKindKey",
        "resource.resourceKey.resourceKindKey", "resource.resourceKey.name",
        "resource.resourceKey.resourceIdentifiers", "resource.resourceKey.resourceIdentifiers[]",
        "resource.resourceKey.resourceIdentifiers[].identifierType",
        "resource.resourceKey.resourceIdentifiers[].identifierType.name",
        "resource.resourceKey.resourceIdentifiers[].identifierType.isPartOfUniqueness",
        "resource.resourceKey.resourceIdentifiers[].value", "vcenter.config.hardware.device",
        "vcenter.rdm.backing.lunUuid", "mapping.virtual_disk_key", "operations.response", "fixture"})

    def __init__(self, message: str, *, stage: str = "UNCLASSIFIED", code: str = "FAILED",
                 field: Optional[str] = None):
        super().__init__(message)
        self.stage = stage if stage in self.STAGES else "UNCLASSIFIED"
        self.code = code if code in self.CODES else "FAILED"
        self.field = field if field in self.FIELDS else None


def _fixture_schema_failure(code: str, field: str) -> None:
    """Reject data unsupported by the fixture contract, not necessarily by Suite API."""
    raise FixtureExportError("Response cannot satisfy the unchanged runtime fixture contract",
                             stage="FIXTURE_SCHEMA_VALIDATION", code=code, field=field)


@contextmanager
def _fixture_stage(stage: str, *, authentication_errors: tuple[type[Exception], ...] = ()):
    """Identify the operation that failed, not an inferred cause from error text."""
    try:
        yield
    except FixtureExportError as exc:
        if exc.stage == "UNCLASSIFIED":
            exc.stage = stage
        raise
    except Exception as exc:
        code = "FAILED"
        if authentication_errors and isinstance(exc, authentication_errors):
            stage, code = "VCENTER_AUTHENTICATION", "AUTH_REJECTED"
        elif isinstance(exc, subprocess.TimeoutExpired):
            code = "TIMEOUT"
        elif stage in {"VCENTER_SESSION", "VCENTER_READ", "OPS_AUTHENTICATION", "OPS_READ"}:
            from requests.exceptions import ConnectionError as RequestConnectionError, Timeout
            if isinstance(exc, (ConnectionError, TimeoutError, socket.gaierror, ssl.SSLError,
                                RequestConnectionError, Timeout)):
                stage = "VCENTER_CONNECTION" if stage.startswith("VCENTER") else "OPS_CONNECTION"
                code = "TIMEOUT" if isinstance(exc, (TimeoutError, Timeout)) else "TRANSPORT_ERROR"
        # Cause stays in process only. CLI never prints it, its type, or repr/str.
        raise FixtureExportError("Fixture operation failed", stage=stage, code=code) from exc


def _fp(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _present(value: Any) -> bool:
    """Presence is distinct from an empty value for JSON-parity decisions."""
    return value is not None


def _env_csv(name: str) -> list[str]:
    return [value.strip() for value in os.environ.get(name, "").split(",") if value.strip()]


def _get(value: Any, name: str, default: Any = None) -> Any:
    method = getattr(value, f"get{name[0].upper()}{name[1:]}", None)
    if callable(method):
        try:
            return method()
        except Exception as exc:
            raise FieldReadError("VIM field accessor failed") from exc
    try:
        return getattr(value, name, default)
    except Exception as exc:
        raise FieldReadError("VIM field accessor failed") from exc


def _fingerprinted_lun(lun: Any) -> dict[str, Any]:
    descriptors = _get(lun, "descriptor", []) or []
    alternates = _get(lun, "alternateName", []) or []
    durable = _get(lun, "durableName")
    return {
        "uuid_fp": _fp(_get(lun, "uuid")),
        "canonical_name_fp": _fp(_get(lun, "canonicalName")),
        "canonical_name_class": (
            "naa" if str(_get(lun, "canonicalName", "")).lower().startswith("naa.")
            else "eui" if str(_get(lun, "canonicalName", "")).lower().startswith("eui.")
            else "other" if _get(lun, "canonicalName") else None
        ),
        "device_name_fp": _fp(_get(lun, "deviceName")),
        "descriptor_quality": sorted(str(_get(item, "quality")) for item in descriptors),
        "descriptor_id_fps": sorted(filter(None, (_fp(_get(item, "id")) for item in descriptors))),
        "durable_name": None if durable is None else {
            "namespace": _get(durable, "namespace"),
            "data_present": bool(_get(durable, "data")),
        },
        "alternate_names": [
            {"namespace": _get(item, "namespace"), "data_present": bool(_get(item, "data"))}
            for item in alternates
        ],
    }


def _validate_property_completeness(requested: set[str], records: dict[str, dict[str, Any]],
                                    missing: dict[str, set[str]]) -> None:
    """Reject partial PropertyCollector results instead of treating them as empty."""
    if requested - set(records) or missing:
        raise PropertyCollectionError("PropertyCollector response incomplete or inaccessible")


def _collect_properties(pc: Any, objects: Iterable[Any], vim_type: Any, paths: list[str]) -> dict[str, dict[str, Any]]:
    """Retrieve explicit objects using paged PropertyCollector requests."""
    from pyVmomi import vmodl  # imported only after explicit live opt-in

    objects = list(objects)
    requested = {item._moId for item in objects}
    object_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=item, skip=False) for item in objects]
    filter_spec = vmodl.query.PropertyCollector.FilterSpec(
        propSet=[vmodl.query.PropertyCollector.PropertySpec(type=vim_type, pathSet=paths, all=False)],
        objectSet=object_specs,
    )
    result = pc.RetrievePropertiesEx(
        specSet=[filter_spec], options=vmodl.query.PropertyCollector.RetrieveOptions(maxObjects=64)
    )
    records: dict[str, dict[str, Any]] = {}
    missing: dict[str, set[str]] = {}
    try:
        while result:
            for content in result.objects or []:
                moid = content.obj._moId
                values = {prop.name: prop.val for prop in content.propSet or []}
                records[moid] = values
                absent = set(paths) - set(values)
                # A missingSet can carry a VIM fault (for example, a privilege
                # failure).  Both plain omissions and faults are incomplete.
                absent.update(str(item.path) for item in (getattr(content, "missingSet", None) or []) if getattr(item, "path", None))
                if absent:
                    missing[moid] = absent
            token = result.token
            if not token:
                break
            result = pc.ContinueRetrievePropertiesEx(token=token)
    except Exception:
        if result and result.token:
            try:
                pc.CancelRetrievePropertiesEx(token=result.token)
            except Exception:
                pass
        raise
    _validate_property_completeness(requested, records, missing)
    return records


def _vcenter_instance_uuid() -> str:
    """Read the owning vCenter's service-instance UUID without emitting it."""
    try:
        from pyVim.connect import Disconnect, SmartConnect
    except ImportError as exc:
        raise RuntimeError("vCenter identity probe requires an already-installed pyVmomi; it will not install it") from exc
    host = os.environ.get("RDM_PROBE_VCENTER_HOST", "")
    user = os.environ.get("RDM_PROBE_VCENTER_USER", "")
    password = os.environ.get("RDM_PROBE_VCENTER_PASSWORD", "")
    if not all((host, user, password)):
        raise RuntimeError("missing RDM_PROBE_VCENTER_HOST/USER/PASSWORD")
    verify = os.environ.get("RDM_PROBE_VCENTER_VERIFY_SSL", "true").lower() not in {"0", "false", "no", "off"}
    service_instance = None
    try:
        service_instance = SmartConnect(host=host, user=user, pwd=password, disableSslCertValidation=not verify)
        instance_uuid = _get(service_instance.RetrieveContent().about, "instanceUuid")
        if not isinstance(instance_uuid, str) or not instance_uuid:
            raise FieldReadError("vCenter service-instance UUID is missing or unreadable")
        return instance_uuid
    finally:
        if service_instance is not None:
            Disconnect(service_instance)


def _lun_visibility(lun_fp: Optional[str], host_views: list[dict[str, Any]], current_host_fp: Optional[str],
                    unstable: bool) -> tuple[str, str, list[dict[str, Any]], list[dict[str, Any]]]:
    """Report vCenter-wide observations separately from current-host visibility."""
    candidates = host_views if lun_fp else []
    current = [item for item in candidates if item["host_moid_fp"] == current_host_fp]
    canonical_fps = {item["canonical_name_fp"] for item in candidates}
    current_canonical_fps = {item["canonical_name_fp"] for item in current}
    global_status = (
        "snapshot_unstable" if unstable else "missing_rdm_lunUuid" if not lun_fp else
        "no_host_lun_match" if not candidates else "canonical_conflict" if len(canonical_fps) > 1 else
        "exact_uuid_multiple_host_views" if len(candidates) > 1 else "exact_uuid_one_host_lun"
    )
    current_status = (
        "snapshot_unstable" if unstable else "missing_rdm_lunUuid" if not lun_fp else
        "not_visible_on_current_host" if not current else
        "current_host_canonical_conflict" if len(current_canonical_fps) > 1 else
        "visible_on_current_host"
    )
    return global_status, current_status, candidates, current


def _soap_probe() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Read selected VMs and their current hosts; no traversal or mutation."""
    try:
        from pyVim.connect import Disconnect, SmartConnect
        from pyVmomi import vim
    except ImportError as exc:
        raise RuntimeError("SOAP probe requires an already-installed pyVmomi; it will not install it") from exc

    host = os.environ.get("RDM_PROBE_VCENTER_HOST", "")
    user = os.environ.get("RDM_PROBE_VCENTER_USER", "")
    password = os.environ.get("RDM_PROBE_VCENTER_PASSWORD", "")
    vm_moids = _env_csv("RDM_PROBE_VCENTER_VM_MOIDS")
    if not all((host, user, password, vm_moids)):
        raise RuntimeError("missing RDM_PROBE_VCENTER_HOST/USER/PASSWORD or RDM_PROBE_VCENTER_VM_MOIDS")
    verify = os.environ.get("RDM_PROBE_VCENTER_VERIFY_SSL", "true").lower() not in {"0", "false", "no", "off"}
    service_instance = None
    try:
        service_instance = SmartConnect(host=host, user=user, pwd=password, disableSslCertValidation=not verify)
        content = service_instance.RetrieveContent()
        vc_instance_uuid = _get(content.about, "instanceUuid")
        if not isinstance(vc_instance_uuid, str) or not vc_instance_uuid:
            raise FieldReadError("vCenter service-instance UUID is missing or unreadable")
        vm_refs = [vim.VirtualMachine(moid, service_instance._stub) for moid in vm_moids]
        vm_records = _collect_properties(
            content.propertyCollector, vm_refs, vim.VirtualMachine,
            ["config.hardware.device", "runtime.host", "config.changeVersion"],
        )
        host_refs = list({record.get("runtime.host") for record in vm_records.values() if record.get("runtime.host")})
        host_records = _collect_properties(
            content.propertyCollector, host_refs, vim.HostSystem, ["config.storageDevice.scsiLun"]
        ) if host_refs else {}
        end_records = _collect_properties(
            content.propertyCollector, vm_refs, vim.VirtualMachine, ["runtime.host", "config.changeVersion"]
        )
        host_luns: dict[str, list[dict[str, Any]]] = {}
        for host_moid, values in host_records.items():
            for lun in values.get("config.storageDevice.scsiLun") or []:
                item = _fingerprinted_lun(lun)
                if item["uuid_fp"]:
                    host_luns.setdefault(item["uuid_fp"], []).append({"host_moid_fp": _fp(host_moid), **item})
        mappings: list[dict[str, Any]] = []
        private_mappings: list[dict[str, Any]] = []
        for vm_moid, values in vm_records.items():
            unstable = (
                _get(values.get("runtime.host"), "_moId") != _get(end_records.get(vm_moid, {}).get("runtime.host"), "_moId")
                or values.get("config.changeVersion") != end_records.get(vm_moid, {}).get("config.changeVersion")
            )
            devices = values["config.hardware.device"]
            controller_bus = {
                str(_get(device, "key")): _get(device, "busNumber")
                for device in devices if isinstance(device, vim.vm.device.VirtualSCSIController)
            }
            current_host_fp = _fp(_get(values["runtime.host"], "_moId"))
            for device in devices:
                if not isinstance(device, vim.vm.device.VirtualDisk):
                    continue
                backing = _get(device, "backing")
                if not isinstance(backing, vim.vm.device.VirtualDisk.RawDiskMappingVer1BackingInfo):
                    continue
                lun_fp = _fp(_get(backing, "lunUuid"))
                status, visibility, candidates, current_host_candidates = _lun_visibility(
                    lun_fp, host_luns.get(lun_fp, []) if lun_fp else [], current_host_fp, unstable
                )
                disk_key = _get(device, "key")
                controller_key = _get(device, "controllerKey")
                unit_number = _get(device, "unitNumber")
                label = _get(_get(device, "deviceInfo"), "label")
                bus = controller_bus.get(str(controller_key))
                file_name = _get(backing, "fileName")
                lun_uuid = _get(backing, "lunUuid")
                mappings.append({
                    "vm_moid_fp": _fp(vm_moid), "disk_key_fp": _fp(disk_key),
                    "controller_key_fp": _fp(controller_key), "unit_number": unit_number,
                    "label_fp": _fp(label), "lun_uuid_fp": lun_fp,
                    "lun_uuid_present": _present(lun_uuid),
                    "device_name_fp": _fp(_get(backing, "deviceName")),
                    "device_name_present": _present(_get(backing, "deviceName")),
                    "file_name_fp": _fp(file_name), "file_name_present": _present(file_name),
                    "compatibility_mode": _get(backing, "compatibilityMode"),
                    "compatibility_mode_present": _present(_get(backing, "compatibilityMode")),
                    "global_uuid_match_status": status, "global_host_lun_views": candidates,
                    "current_host_uuid_match_status": visibility,
                    "current_host_lun_views": current_host_candidates,
                })
                private_mappings.append({
                    "vcenter_instance_uuid": vc_instance_uuid, "vm_moid": vm_moid,
                    "disk_key": disk_key, "label": label, "file_name": file_name,
                    "lun_uuid": lun_uuid, "controller_unit": None if bus is None or unit_number is None else f"scsi{bus}:{unit_number}",
                })
        return ({"vc_instance_fp": _fp(vc_instance_uuid), "vm_requested": len(vm_moids),
                 "vm_read": len(vm_records), "hosts_read": len(host_records), "rdm_mappings": mappings}, private_mappings)
    finally:
        if service_instance is not None:
            Disconnect(service_instance)


def _vim_json_devices(payload: Any) -> tuple[Optional[list[dict[str, Any]]], str]:
    """Recognize the documented config.hardware.device JSON representations."""
    if not isinstance(payload, dict) or not isinstance(payload.get("hardware"), dict):
        return None, "missing_hardware_object"
    devices = payload["hardware"].get("device")
    if isinstance(devices, list):
        return devices, "device_array"
    if isinstance(devices, dict) and isinstance(devices.get("_value"), list):
        return devices["_value"], "boxed_device_array"
    return None, "unrecognized_device_representation"


def _vim_json_probe() -> dict[str, Any]:
    """Read selected VM config JSON with an operator-supplied session header."""
    import requests

    host = os.environ.get("RDM_PROBE_VCENTER_HOST", "")
    release = os.environ.get("RDM_PROBE_VIM_JSON_RELEASE", "")
    authorization = os.environ.get("RDM_PROBE_VIM_JSON_AUTHORIZATION", "")
    vm_moids = _env_csv("RDM_PROBE_VCENTER_VM_MOIDS")
    if not all((host, release, authorization, vm_moids)):
        raise RuntimeError("missing VIM JSON host/release/session header or selected VM MOIDs")
    verify = os.environ.get("RDM_PROBE_VCENTER_VERIFY_SSL", "true").lower() not in {"0", "false", "no", "off"}
    disks = []
    failures = []
    for moid in vm_moids:
        response = requests.get(
            f"https://{host}/sdk/vim25/{release}/VirtualMachine/{moid}/config",
            headers={"Authorization": authorization, "Accept": "application/json"}, timeout=30, verify=verify,
        )
        if response.status_code != 200:
            failures.append({"vm_moid_fp": _fp(moid), "http_status": response.status_code})
            continue
        try:
            payload = response.json()
        except ValueError:
            failures.append({"vm_moid_fp": _fp(moid), "error": "non_json_response"})
            continue
        devices, representation = _vim_json_devices(payload)
        if devices is None:
            failures.append({"vm_moid_fp": _fp(moid), "error": representation})
            continue
        unrecognized_backing = False
        for item in devices:
            if not isinstance(item, dict):
                unrecognized_backing = True
                continue
            backing = item.get("backing")
            if not isinstance(backing, dict):
                continue
            type_name = str(backing.get("_typeName") or backing.get("type") or "")
            if not type_name:
                unrecognized_backing = True
                continue
            if "RawDiskMappingVer1BackingInfo" not in type_name:
                continue
            disks.append({
                "vm_moid_fp": _fp(moid), "disk_key_fp": _fp(item.get("key")), "backing_type": type_name,
                "lun_uuid_fp": _fp(backing.get("lunUuid")), "lun_uuid_present": "lunUuid" in backing,
                "device_name_fp": _fp(backing.get("deviceName")), "device_name_present": "deviceName" in backing,
                "file_name_fp": _fp(backing.get("fileName")), "file_name_present": "fileName" in backing,
                "compatibility_mode": backing.get("compatibilityMode"), "compatibility_mode_present": "compatibilityMode" in backing,
            })
        if unrecognized_backing:
            failures.append({"vm_moid_fp": _fp(moid), "error": "unrecognized_device_or_backing_type"})
    return {"vm_requested": len(vm_moids), "rdm_disks": disks, "failures": failures,
            "status": "unsupported_or_unrecognized" if failures else "ok"}


def _json_parity(soap: dict[str, Any], vim_json: dict[str, Any]) -> dict[str, Any]:
    json_by_key = {(item["vm_moid_fp"], item["disk_key_fp"]): item for item in vim_json["rdm_disks"]}
    checks = []
    for item in soap["rdm_mappings"]:
        peer = json_by_key.get((item["vm_moid_fp"], item["disk_key_fp"]))
        equal = bool(peer) and all(item.get(key) == peer.get(key) for key in
                                  ("lun_uuid_fp", "lun_uuid_present", "device_name_fp", "device_name_present",
                                   "file_name_fp", "file_name_present", "compatibility_mode", "compatibility_mode_present"))
        checks.append({"vm_moid_fp": item["vm_moid_fp"], "disk_key_fp": item["disk_key_fp"],
                       "status": "match" if equal else "mismatch_or_missing"})
    return {"status": "pass" if checks and all(item["status"] == "match" for item in checks) and not vim_json["failures"] else "fail",
            "checks": checks}


def _operations_instances(payload: Any) -> dict[str, set[str]]:
    """Parse only the documented stats-of-resources JSON shape."""
    if not isinstance(payload, dict) or not isinstance(payload.get("values"), list):
        raise OperationsShapeError("stats response missing values array")
    found: dict[str, set[str]] = {}
    for row in payload["values"]:
        stat_list = row.get("stat-list") if isinstance(row, dict) else None
        stats = stat_list.get("stat") if isinstance(stat_list, dict) else None
        if not isinstance(stats, list):
            raise OperationsShapeError("stats response missing stat-list.stat array")
        for entry in stats:
            key = ((entry.get("statKey") or {}).get("key")) if isinstance(entry, dict) else None
            if not isinstance(key, str):
                raise OperationsShapeError("stats response has stat without statKey.key")
            if key.startswith("virtualDisk:") and "|" in key:
                instance, leaf = key.split("|", 1)
                found.setdefault(instance, set()).add(leaf)
    return found


def _operations_properties(payload: Any) -> dict[str, dict[str, Any]]:
    properties = payload.get("property") if isinstance(payload, dict) else None
    if not isinstance(properties, list):
        raise OperationsShapeError("properties response missing property array")
    found: dict[str, dict[str, Any]] = {}
    for entry in properties:
        name = entry.get("name") if isinstance(entry, dict) else None
        if not isinstance(name, str):
            raise OperationsShapeError("properties response has property without name")
        if name.startswith("virtualDisk:") and "|" in name:
            instance, leaf = name.split("|", 1)
            found.setdefault(instance, {})[leaf] = entry.get("value")
    return found


def _operations_vm_identity(identifiers: list[dict[str, Any]]) -> tuple[Optional[str], Optional[str], str]:
    """Return the exact VMWARE composite identity only when both fields are readable."""
    values = {
        (item.get("identifierType") or {}).get("name"): item.get("value")
        for item in identifiers if isinstance(item, dict)
    }
    moid = values.get("VMEntityObjectID")
    vcid = values.get("VMEntityVCID")
    if not isinstance(moid, str) or not moid or not isinstance(vcid, str) or not vcid:
        return None, None, "incomplete_operations_vm_identity"
    return moid, vcid, "complete_operations_vm_identity"


def _mapping_match_methods(instance: str, values: dict[str, Any], mapping: dict[str, Any]) -> list[str]:
    methods = []
    if instance == "virtualDisk:" + str(mapping["disk_key"]):
        methods.append("instance_equals_virtual_disk_key")
    if mapping["controller_unit"] and instance == "virtualDisk:" + mapping["controller_unit"]:
        methods.append("instance_equals_controller_unit")
    if mapping["label"] and instance == "virtualDisk:" + str(mapping["label"]):
        methods.append("instance_equals_label")
    if mapping["file_name"] and instance == "virtualDisk:" + str(mapping["file_name"]):
        methods.append("instance_equals_backing_filename")
    if mapping["lun_uuid"] and instance == "virtualDisk:" + str(mapping["lun_uuid"]):
        methods.append("instance_equals_lun_uuid")
    if mapping["label"] and values.get("label") == mapping["label"]:
        methods.append("property_label")
    if mapping["file_name"] and values.get("fileName") == mapping["file_name"]:
        methods.append("property_file_name")
    if mapping["lun_uuid"] and values.get("lunUuid") == mapping["lun_uuid"]:
        methods.append("property_lun_uuid")
    return methods


def _rdm_instance_correlation_report(instances: dict[str, set[str]], properties: dict[str, dict[str, Any]],
                                     identifiers: list[dict[str, Any]], mappings: list[dict[str, Any]]) -> dict[str, Any]:
    """Correlate only SOAP RDMs belonging to the exact Operations VM identity."""
    if not mappings:
        return {"identity_status": "not_requested", "matched": [], "unmatched_rdm_mappings": [],
                "unmatched_operations_disk_instances": []}
    vm_moid, vcid, identity_status = _operations_vm_identity(identifiers)
    if identity_status != "complete_operations_vm_identity":
        return {"identity_status": identity_status, "matched": [], "unmatched_rdm_mappings": [],
                "unmatched_operations_disk_instances": []}
    candidates = [mapping for mapping in mappings
                  if mapping.get("vm_moid") == vm_moid and mapping.get("vcenter_instance_uuid") == vcid]
    if not candidates:
        return {"identity_status": "no_matching_soap_vm_identity", "matched": [], "unmatched_rdm_mappings": [],
                "unmatched_operations_disk_instances": []}
    if not instances:
        return {
            "identity_status": "complete_exact_soap_vm_identity", "matched": [],
            "unmatched_rdm_mappings": [
                {"disk_key_fp": _fp(mapping["disk_key"]), "status": "missing_instance_data"}
                for mapping in candidates
            ],
            "unmatched_operations_disk_instances": [],
        }
    matched = []
    unmatched_mappings = []
    matched_instances: set[str] = set()
    for mapping in candidates:
        matches = []
        for instance, leaves in instances.items():
            methods = _mapping_match_methods(instance, properties.get(instance, {}), mapping)
            if methods:
                confidence = "high" if "instance_equals_controller_unit" in methods and len(methods) > 1 else "medium" if len(methods) > 1 else "low"
                matches.append({"instance_token_fp": _fp(instance), "disk_key_fp": _fp(mapping["disk_key"]),
                                "methods": methods, "confidence": confidence,
                                "observed_metric_leaves": sorted(leaves)})
                matched_instances.add(instance)
        if len(matches) == 1:
            matched.extend(matches)
        elif len(matches) > 1:
            unmatched_mappings.append({"disk_key_fp": _fp(mapping["disk_key"]),
                                       "status": "ambiguous_candidate_identifier_match",
                                       "candidate_instance_token_fps": [match["instance_token_fp"] for match in matches]})
        else:
            unmatched_mappings.append({"disk_key_fp": _fp(mapping["disk_key"]),
                                       "status": "no_candidate_identifier_matched"})
    unmatched_instances = [
        {"instance_token_fp": _fp(instance), "status": "no_soap_rdm_candidate_identifier_matched",
         "observed_metric_leaves": sorted(leaves)}
        for instance, leaves in instances.items() if instance not in matched_instances
    ]
    return {"identity_status": "complete_exact_soap_vm_identity", "matched": matched,
            "unmatched_rdm_mappings": unmatched_mappings,
            "unmatched_operations_disk_instances": unmatched_instances}


def _instance_correlations(instances: dict[str, set[str]], properties: dict[str, dict[str, Any]],
                           identifiers: list[dict[str, Any]], mappings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compatibility summary: matched correlations only."""
    return _rdm_instance_correlation_report(instances, properties, identifiers, mappings)["matched"]


def _release_operations_token(client: Any, cleanup: dict[str, Any]) -> None:
    """Best-effort auth-token release; never mask the collection outcome."""
    if not getattr(client, "_token", None):
        return
    cleanup["attempted"] = True
    try:
        response = client._request("POST", "/api/auth/token/release")
        cleanup["status"] = "released" if response.status_code == 200 else "release_http_failure"
    except Exception:
        cleanup["status"] = "release_exception"


def _resource_identifier_values(resource: Any) -> tuple[Optional[str], list[dict[str, Any]], bool]:
    """Read the complete resource-key identifier set, retaining raw values only in memory."""
    if not isinstance(resource, dict):
        return None, [], False
    resource_id = resource.get("identifier")
    if not isinstance(resource_id, str) or not resource_id:
        resource_id = resource.get("id")
    key = resource.get("resourceKey")
    identifiers = key.get("resourceIdentifiers") if isinstance(key, dict) else None
    if not isinstance(identifiers, list):
        return resource_id if isinstance(resource_id, str) else None, [], False
    sanitized = []
    complete = isinstance(resource_id, str) and bool(resource_id)
    for item in identifiers:
        identifier_type = item.get("identifierType") if isinstance(item, dict) else None
        name = identifier_type.get("name") if isinstance(identifier_type, dict) else None
        value = item.get("value") if isinstance(item, dict) else None
        unique = identifier_type.get("isPartOfUniqueness") if isinstance(identifier_type, dict) else None
        if not isinstance(name, str) or not name or not isinstance(value, str) or not isinstance(unique, bool):
            complete = False
            continue
        sanitized.append({"name": name, "value_fp": _fp(value), "is_part_of_uniqueness": unique})
    return resource_id if isinstance(resource_id, str) else None, sanitized, complete


def _ops_vm_match(resources: list[dict[str, Any]], vm_moid: str, vcenter_instance_uuid: str,
                  display_name: Optional[str] = None) -> tuple[dict[str, Any], Optional[str]]:
    """Require exact VMEntityObjectID + VMEntityVCID evidence; names are discovery-only."""
    candidates = []
    proven: list[str] = []
    incomplete_possible_match = False
    for resource in resources:
        resource_id, identifiers, complete = _resource_identifier_values(resource)
        key = resource.get("resourceKey") if isinstance(resource, dict) else None
        name = key.get("name") if isinstance(key, dict) else None
        raw_values = {
            item["name"]: None for item in identifiers
        }
        # Read values directly from the response only for comparison; never
        # attach this map to the returned report.
        for item in (key.get("resourceIdentifiers") if isinstance(key, dict) and isinstance(key.get("resourceIdentifiers"), list) else []):
            identifier_type = item.get("identifierType") if isinstance(item, dict) else None
            identifier_name = identifier_type.get("name") if isinstance(identifier_type, dict) else None
            if isinstance(identifier_name, str) and isinstance(item.get("value"), str):
                raw_values[identifier_name] = item["value"]
        moid_match = raw_values.get("VMEntityObjectID") == vm_moid
        vcid_match = raw_values.get("VMEntityVCID") == vcenter_instance_uuid
        display_name_match = isinstance(display_name, str) and name == display_name
        pair_match = moid_match and vcid_match and complete and resource_id is not None
        partial_match = moid_match or vcid_match
        if (partial_match or display_name_match) and not pair_match and not complete:
            incomplete_possible_match = True
        if partial_match or display_name_match:
            candidates.append({
                "resource_uuid_fp": _fp(resource_id),
                "resource_name_fp": _fp(name),
                "identifier_values": identifiers,
                "matching_evidence": {
                    "vm_moid_exact": moid_match,
                    "vcenter_instance_uuid_exact": vcid_match,
                    "display_name_exact_discovery_only": display_name_match,
                    "pair_exact": pair_match,
                },
                "candidate_status": "complete_pair_match" if pair_match else
                "incomplete_identifier_set" if not complete else
                "partial_identity_match" if partial_match else "display_name_candidate_only",
            })
        if pair_match:
            proven.append(resource_id)
    if len(proven) == 1:
        status = "unique"
        handoff_resource_id: Optional[str] = proven[0]
    elif len(proven) > 1:
        status = "ambiguous"
        handoff_resource_id = None
    elif incomplete_possible_match:
        status = "incomplete"
        handoff_resource_id = None
    else:
        status = "absent"
        handoff_resource_id = None
    return ({"status": status, "candidate_count": len(candidates), "candidates": candidates}, handoff_resource_id)


def _ops_vm_discovery(profile: str) -> tuple[dict[str, Any], Optional[str]]:
    """Read all VMWARE VirtualMachine resource keys and prove one scoped match."""
    from vcfcf_common.client import VCFOpsClient

    vm_moid = os.environ.get("RDM_PROBE_TARGET_VM_MOID", "")
    display_name = os.environ.get("RDM_PROBE_TARGET_VM_DISPLAY_NAME") or None
    if not vm_moid:
        raise RuntimeError("missing RDM_PROBE_TARGET_VM_MOID")
    vcenter_instance_uuid = _vcenter_instance_uuid()
    client = VCFOpsClient.from_env(profile, default_profile="devel")
    cleanup = {"attempted": False, "status": "not_needed"}
    resources: list[dict[str, Any]] = []
    try:
        expected_total: Optional[int] = None
        for page in range(OPS_VM_DISCOVERY_MAX_PAGES):
            response = client._request("GET", "/api/resources", params={
                "adapterKind": "VMWARE", "resourceKind": "VirtualMachine",
                "page": page, "pageSize": OPS_VM_DISCOVERY_PAGE_SIZE,
            })
            if response.status_code != 200:
                raise OperationsDiscoveryError("Operations VM resource listing failed")
            payload = response.json()
            rows = payload.get("resourceList") if isinstance(payload, dict) else None
            page_info = payload.get("pageInfo") if isinstance(payload, dict) else None
            total = page_info.get("totalCount") if isinstance(page_info, dict) else None
            if not isinstance(rows, list) or not isinstance(total, int) or total < 0:
                raise OperationsDiscoveryError("Operations VM resource listing has incomplete pagination")
            if expected_total is None:
                expected_total = total
            elif expected_total != total:
                raise OperationsDiscoveryError("Operations VM resource listing changed during pagination")
            if not all(isinstance(row, dict) for row in rows):
                raise OperationsDiscoveryError("Operations VM resource listing contains an invalid resource")
            resources.extend(rows)
            if len(resources) >= total:
                if len(resources) != total:
                    raise OperationsDiscoveryError("Operations VM resource listing exceeded declared total")
                break
            if not rows:
                raise OperationsDiscoveryError("Operations VM resource listing ended before declared total")
        else:
            raise OperationsDiscoveryError("Operations VM resource listing exceeded safety page limit")
        result, handoff_resource_id = _ops_vm_match(resources, vm_moid, vcenter_instance_uuid, display_name)
        result.update({
            "profile": profile,
            "vcenter_instance_uuid_fp": _fp(vcenter_instance_uuid),
            "target_vm_moid_fp": _fp(vm_moid),
            "display_name_search_requested": display_name is not None,
            "resources_examined": len(resources),
            "token_cleanup": cleanup,
        })
        return result, handoff_resource_id
    finally:
        _release_operations_token(client, cleanup)


def _ops_probe(profile: str, mappings: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
    """Read explicit VCF Operations VM resources and observed disk instances."""
    from vcfcf_common.client import VCFOpsClient

    resource_ids = _env_csv("RDM_PROBE_OPS_RESOURCE_IDS")
    if not resource_ids:
        raise RuntimeError("missing RDM_PROBE_OPS_RESOURCE_IDS; selected resource UUIDs are required")
    client = VCFOpsClient.from_env(profile, default_profile="devel")
    now = int(time.time() * 1000)
    rows = []
    cleanup = {"attempted": False, "status": "not_needed"}
    try:
        for resource_id in resource_ids:
            resource = client._request("GET", f"/api/resources/{resource_id}")
            statkeys = client._request("GET", "/api/adapterkinds/VMWARE/resourcekinds/VirtualMachine/statkeys")
            stats = client._request("GET", f"/api/resources/{resource_id}/stats", params={"begin": now - 3600000, "end": now})
            properties = client._request("GET", f"/api/resources/{resource_id}/properties")
            relationships = client._request("GET", f"/api/resources/{resource_id}/relationships", params={"relationshipType": "ALL"})
            if any(response.status_code != 200 for response in (resource, statkeys, stats, properties, relationships)):
                rows.append({"resource_id_fp": _fp(resource_id), "status": "read_failed",
                             "http_statuses": [response.status_code for response in (resource, statkeys, stats, properties, relationships)]})
                continue
            body = resource.json()
            identifiers = (body.get("resourceKey") or body).get("resourceIdentifiers") or []
            declared = (statkeys.json().get("resourceTypeAttributes") or statkeys.json().get("statKey") or [])
            disk_schema = [entry.get("key") for entry in declared if str(entry.get("key", "")).startswith("virtualDisk|")]
            # Discover labels in memory without retaining or serializing the raw stats payload.
            instances = _operations_instances(stats.json())
            disk_tokens = sorted(instances)
            props_by_instance = _operations_properties(properties.json())
            rdm_correlation = _rdm_instance_correlation_report(instances, props_by_instance, identifiers, mappings or [])
            prop_names = [name for name in (entry.get("name") for entry in (properties.json().get("property") or []))
                          if isinstance(name, str) and name.startswith("virtualDisk:")]
            related = relationships.json().get("resourceList") or []
            rows.append({
                "resource_id_fp": _fp(resource_id), "status": "ok",
                "resource_key_identifiers": [{"name": (item.get("identifierType") or {}).get("name"),
                    "unique": (item.get("identifierType") or {}).get("isPartOfUniqueness"),
                    "value_present": bool(item.get("value"))} for item in identifiers],
                "declared_virtual_disk_fields": sorted(filter(None, disk_schema)),
                "observed_instance_token_fps": sorted(filter(None, (_fp(token) for token in disk_tokens))),
                "virtual_disk_property_key_fps": sorted(filter(None, (_fp(name) for name in prop_names))),
                "disk_instance_correlations": rdm_correlation["matched"],
                "rdm_disk_instance_correlation": rdm_correlation,
                "related_resource_kind_counts": _kind_counts(related),
            })
    finally:
        _release_operations_token(client, cleanup)
    return {"profile": profile, "resources": rows, "token_cleanup": cleanup}


def _kind_counts(resources: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in resources:
        key = ((item.get("resourceKey") or {}).get("resourceKindKey") or "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def _virtual_disk_instance_labels(value: Any) -> set[str]:
    """Collect only instance labels from nested stats responses in memory."""
    found: set[str] = set()
    if isinstance(value, dict):
        for item in value.values():
            found.update(_virtual_disk_instance_labels(item))
    elif isinstance(value, list):
        for item in value:
            found.update(_virtual_disk_instance_labels(item))
    elif isinstance(value, str) and value.startswith("virtualDisk:") and "|" in value:
        found.add(value.split("|", 1)[0])
    return found


def _safe_output_path(path: Path) -> Path:
    """Limit reports to the gitignored lab scratch area and never overwrite."""
    repo_root = Path(__file__).resolve().parents[1]
    allowed = repo_root / "tmp" / "rdm-lab-probes"
    if path.is_absolute():
        candidate = path
    else:
        candidate = repo_root / path
    if candidate.exists() or candidate.is_symlink():
        raise ValueError("refusing to overwrite or follow an existing output path")
    allowed.mkdir(mode=0o700, parents=True, exist_ok=True)
    if allowed.is_symlink() or candidate.parent.resolve() != allowed.resolve():
        raise ValueError("--output must be a new file directly under tmp/rdm-lab-probes")
    return candidate


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path = _safe_output_path(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    directory_flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        directory_flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        directory_flags |= os.O_NOFOLLOW
    directory_fd = os.open(path.parent, directory_flags)
    try:
        fd = os.open(path.name, flags, stat.S_IRUSR | stat.S_IWUSR, dir_fd=directory_fd)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(report, handle, indent=2, sort_keys=True)
                handle.write("\n")
        except Exception:
            try:
                path.unlink()
            except OSError:
                pass
            raise
    finally:
        os.close(directory_fd)


def _write_ops_uuid_handoff(path: Path, resource_id: str) -> None:
    """Write a unique resolved UUID only to a new local mode-0600 handoff file."""
    _write_report(path, {"RDM_PROBE_OPS_RESOURCE_IDS": [resource_id]})


def _fixture_output_path() -> Path:
    """Fixed, ignored, owner-only destination; check before accessing inventory."""
    root = Path(__file__).resolve().parents[1]
    path = root / "tmp/rdm-lab-probes/rdm-fixture-vm-71.json"
    for parent in (root / "tmp", path.parent):
        if parent.is_symlink() or not parent.is_dir():
            raise FixtureExportError("Fixture scratch directory unavailable")
    info = path.parent.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise FixtureExportError("Fixture scratch directory must be owned by this user with mode 0700")
    if path.exists() or path.is_symlink():
        raise FixtureExportError("Fixture output already exists; refusing overwrite")
    relative = path.relative_to(root).as_posix()
    ignored = subprocess.run(["git", "check-ignore", "--quiet", "--", relative], cwd=root,
                             capture_output=True, timeout=15)
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", "--", relative], cwd=root,
                             capture_output=True, timeout=15)
    if ignored.returncode != 0 or tracked.returncode != 1:
        raise FixtureExportError("Fixture output is not verified ignored and untracked")
    return path


@contextmanager
def _fixture_validator():
    """Compile the actual E2.1 parser; only send sensitive payload over stdin."""
    root = Path(__file__).resolve().parents[1]
    source = root / "content/sdk-adapters/rdm-topology-poc/src/com/vcfcf/adapters/rdmtopologypoc"
    sdk = Path(os.environ.get("VCFCF_SDK_JAR", ""))
    if not sdk.is_file():
        raise FixtureExportError("Offline SDK unavailable", stage="JAVA_PARSER_SETUP", code="SDK_UNAVAILABLE")
    if not shutil.which("javac") or not shutil.which("java"):
        raise FixtureExportError("Offline Java tools unavailable", stage="JAVA_PARSER_SETUP", code="JAVA_UNAVAILABLE")
    files = [source / f"{name}.java" for name in
             ("RuntimeFixture", "ForeignVmIdentity", "RdmMappingIdentity")]
    files.append(root / "scripts/RdmFixtureValidate.java")
    if not all(path.is_file() for path in files):
        raise FixtureExportError("Actual E2.1 parser source unavailable", stage="JAVA_PARSER_SETUP", code="PARSER_SOURCE_UNAVAILABLE")
    with tempfile.TemporaryDirectory(prefix="rdm-fixture-validator-") as build:
        with _fixture_stage("JAVA_PARSER_SETUP"):
            compiled = subprocess.run(["javac", "-proc:none", "-cp", str(sdk), "-d", build,
                                       *(str(path) for path in files)], capture_output=True, timeout=60)
        if compiled.returncode != 0:
            raise FixtureExportError("Offline Java parser compilation failed", stage="JAVA_PARSER_SETUP", code="COMPILE_FAILED")

        def validate(payload: bytes) -> None:
            with _fixture_stage("JAVA_PARSER_VALIDATION"):
                result = subprocess.run(["java", "-cp", os.pathsep.join((build, str(sdk))),
                                         "com.vcfcf.adapters.rdmtopologypoc.RdmFixtureValidate"],
                                        input=payload, capture_output=True, timeout=30)
            if result.returncode != 0 or result.stdout != b"VALID\n":
                raise FixtureExportError("Actual Java runtime fixture parser rejected capture", stage="JAVA_PARSER_VALIDATION", code="PARSER_REJECTED")
        yield validate


def _capture_soap_fixture() -> dict[str, Any]:
    """Only vm-71, with instance UUID and stable pre/post configuration snapshots."""
    with _fixture_stage("VCENTER_CONFIGURATION"):
        from pyVim.connect import Disconnect, SmartConnect
        from pyVmomi import vim

    host, user, password = (os.environ.get(f"RDM_PROBE_VCENTER_{key}", "")
                            for key in ("HOST", "USER", "PASSWORD"))
    if not all((host, user, password)):
        raise FixtureExportError("Missing configured vCenter probe credentials", stage="VCENTER_CONFIGURATION", code="MISSING_CONFIGURATION")
    verify = os.environ.get("RDM_PROBE_VCENTER_VERIFY_SSL", "true").lower() not in {"0", "false", "no", "off"}
    instance = None
    try:
        auth_errors = (vim.fault.InvalidLogin, vim.fault.NotAuthenticated)
        with _fixture_stage("VCENTER_SESSION", authentication_errors=auth_errors):
            instance = SmartConnect(host=host, user=user, pwd=password, disableSslCertValidation=not verify,
                                    httpConnectionTimeout=30)
        with _fixture_stage("VCENTER_READ", authentication_errors=auth_errors):
            content = instance.RetrieveContent()
            vc = _get(content.about, "instanceUuid")
            vm = vim.VirtualMachine("vm-71", instance._stub)
            paths = ["config.instanceUuid", "config.changeVersion", "runtime.host", "config.hardware.device"]
            before = _collect_properties(content.propertyCollector, [vm], vim.VirtualMachine, paths)["vm-71"]
            after = _collect_properties(content.propertyCollector, [vm], vim.VirtualMachine, paths[:-1])["vm-71"]
            with _fixture_stage("VM_IDENTITY_CORRELATION"):
                _validate_fixture_snapshot(before, after)
            devices = before["config.hardware.device"]
            if not isinstance(devices, (list, tuple)):
                _fixture_schema_failure("VM_DEVICES_NOT_ARRAY", "vcenter.config.hardware.device")
            disks = [device for device in devices if isinstance(device, vim.vm.device.VirtualDisk)
                     and isinstance(_get(device, "backing"), vim.vm.device.VirtualDisk.RawDiskMappingVer1BackingInfo)]
            return _single_rdm_fixture_mapping(vc, before["config.instanceUuid"], disks)
    finally:
        if instance is not None:
            try:
                Disconnect(instance)
            except Exception:
                pass  # Session cleanup must not mask the primary collection result.


def _validate_fixture_snapshot(before: dict[str, Any], after: dict[str, Any]) -> None:
    for key in ("config.instanceUuid", "config.changeVersion"):
        if not isinstance(before.get(key), str) or not before[key] or before[key] != after.get(key):
            raise FixtureExportError("VM identity or configuration snapshot incomplete or changed")
    host = _get(before.get("runtime.host"), "_moId")
    if not host or host != _get(after.get("runtime.host"), "_moId"):
        raise FixtureExportError("VM host snapshot incomplete or changed")


def _single_rdm_fixture_mapping(vc: Any, vm_uuid: Any, disks: list[Any]) -> dict[str, Any]:
    if len(disks) != 1:
        raise FixtureExportError("Capture requires exactly one identified RDM", stage="RDM_AMBIGUITY",
                                 code="NO_RDM" if not disks else "MULTIPLE_RDMS")
    lun = _get(_get(disks[0], "backing"), "lunUuid")
    key = _get(disks[0], "key")
    if not isinstance(lun, str) or not lun:
        _fixture_schema_failure("RDM_LUN_IDENTITY_INVALID", "vcenter.rdm.backing.lunUuid")
    if type(key) is not int or not 0 < key <= 2147483647:
        _fixture_schema_failure("RDM_DISK_KEY_INVALID", "mapping.virtual_disk_key")
    return {"vm_moid": "vm-71", "vcenter_instance_uuid": vc,
            "vm_instance_uuid": vm_uuid, "virtual_disk_key": str(key)}


def _fixture_resource_key(resource: Any) -> dict[str, Any]:
    """Project schema identity members, never omit an identifier or default a flag."""
    base = "resource.resourceKey"
    if not isinstance(resource, dict):
        _fixture_schema_failure("RESOURCE_NOT_OBJECT", "resource")
    if "resourceKey" not in resource:
        _fixture_schema_failure("RESOURCE_KEY_MISSING", base)
    key = resource["resourceKey"]
    if not isinstance(key, dict):
        _fixture_schema_failure("RESOURCE_KEY_NOT_OBJECT", base)
    if key.get("adapterKindKey") != "VMWARE":
        _fixture_schema_failure("ADAPTER_KIND_INVALID", base + ".adapterKindKey")
    if key.get("resourceKindKey") != "VirtualMachine":
        _fixture_schema_failure("RESOURCE_KIND_INVALID", base + ".resourceKindKey")
    if "name" not in key:
        _fixture_schema_failure("RESOURCE_NAME_MISSING", base + ".name")
    if not isinstance(key["name"], str) or not key["name"]:
        _fixture_schema_failure("RESOURCE_NAME_INVALID", base + ".name")
    if "resourceIdentifiers" not in key:
        _fixture_schema_failure("IDENTIFIERS_MISSING", base + ".resourceIdentifiers")
    identifiers = key["resourceIdentifiers"]
    if not isinstance(identifiers, list):
        _fixture_schema_failure("IDENTIFIERS_NOT_ARRAY", base + ".resourceIdentifiers")
    if not identifiers:
        _fixture_schema_failure("IDENTIFIERS_EMPTY", base + ".resourceIdentifiers")
    projected = []
    names = set()
    for item in identifiers:
        field = base + ".resourceIdentifiers[]"
        if not isinstance(item, dict):
            _fixture_schema_failure("IDENTIFIER_NOT_OBJECT", field)
        if "identifierType" not in item:
            _fixture_schema_failure("IDENTIFIER_TYPE_MISSING", field + ".identifierType")
        kind = item["identifierType"]
        if not isinstance(kind, dict):
            _fixture_schema_failure("IDENTIFIER_TYPE_NOT_OBJECT", field + ".identifierType")
        if "name" not in kind:
            _fixture_schema_failure("IDENTIFIER_NAME_MISSING", field + ".identifierType.name")
        name = kind["name"]
        if not isinstance(name, str) or not name:
            _fixture_schema_failure("IDENTIFIER_NAME_INVALID", field + ".identifierType.name")
        if name in names:
            _fixture_schema_failure("IDENTIFIER_NAME_DUPLICATE", field + ".identifierType.name")
        if "isPartOfUniqueness" not in kind:
            _fixture_schema_failure("IDENTIFIER_UNIQUENESS_MISSING", field + ".identifierType.isPartOfUniqueness")
        unique = kind["isPartOfUniqueness"]
        if type(unique) is not bool:
            _fixture_schema_failure("IDENTIFIER_UNIQUENESS_NOT_BOOLEAN", field + ".identifierType.isPartOfUniqueness")
        if "value" not in item:
            _fixture_schema_failure("IDENTIFIER_VALUE_MISSING", field + ".value")
        value = item["value"]
        if value is None:
            _fixture_schema_failure("IDENTIFIER_VALUE_NULL", field + ".value")
        if not isinstance(value, str):
            _fixture_schema_failure("IDENTIFIER_VALUE_NOT_STRING", field + ".value")
        # The SDK retains "" exactly, but rejects null entries. Only explicit
        # nonunique empty strings are supported; never default a missing flag,
        # fill a missing value, or normalize null into an empty string.
        if not value and unique:
            _fixture_schema_failure("IDENTIFIER_VALUE_EMPTY", field + ".value")
        names.add(name)
        projected.append({"identifierType": {"name": name, "isPartOfUniqueness": unique}, "value": value})
    return {"adapterKindKey": key["adapterKindKey"], "resourceKindKey": key["resourceKindKey"],
            "name": key["name"], "resourceIdentifiers": projected}


def _fixture_from_resources(resources: list[Any], mapping: dict[str, Any]) -> dict[str, Any]:
    if mapping.get("vm_moid") != "vm-71":
        raise FixtureExportError("Unexpected fixture VM")
    matches = []
    for resource in resources:
        with _fixture_stage("FIXTURE_SCHEMA_VALIDATION"):
            key = _fixture_resource_key(resource)  # Any malformed inventory fails closed.
        identifiers = {item["identifierType"]["name"]: item for item in key["resourceIdentifiers"]}
        moid = identifiers.get("VMEntityObjectID")
        vcid = identifiers.get("VMEntityVCID")
        if not moid or not vcid:
            raise FixtureExportError("Unscoped Operations VM response")
        if moid["value"] == mapping["vm_moid"] and vcid["value"] == mapping["vcenter_instance_uuid"]:
            if not all(item["identifierType"]["isPartOfUniqueness"] for item in (moid, vcid)):
                raise FixtureExportError("VM scope is not uniqueness-bearing")
            matches.append(key)
    if len(matches) != 1:
        raise FixtureExportError("Operations scoped VM match is absent or ambiguous")
    return {"foreign_vm": matches[0], "mapping": {key: mapping[key] for key in
            ("vcenter_instance_uuid", "vm_instance_uuid", "virtual_disk_key")}}


def _capture_fixture_resources(client: Any) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    expected = None
    seen = set()
    for page in range(OPS_VM_DISCOVERY_MAX_PAGES):
        with _fixture_stage("OPS_READ"):
            response = client._request("GET", "/api/resources", params={"adapterKind": "VMWARE",
                "resourceKind": "VirtualMachine", "page": page, "pageSize": OPS_VM_DISCOVERY_PAGE_SIZE}, timeout=30)
        if response.status_code == 401:
            raise FixtureExportError("Operations request not authenticated", stage="OPS_AUTHENTICATION", code="AUTH_REJECTED")
        if response.status_code == 403:
            raise FixtureExportError("Operations request forbidden", stage="OPS_AUTHORIZATION", code="HTTP_ERROR")
        if response.status_code != 200:
            raise FixtureExportError("Operations VM listing failed", stage="OPS_READ", code="HTTP_ERROR")
        with _fixture_stage("FIXTURE_SCHEMA_VALIDATION"):
            try:
                payload = response.json()
            except ValueError as exc:
                raise FixtureExportError("Operations response JSON unavailable", stage="FIXTURE_SCHEMA_VALIDATION",
                                         code="OPS_RESPONSE_JSON_INVALID", field="operations.response") from exc
        rows = payload.get("resourceList") if isinstance(payload, dict) else None
        info = payload.get("pageInfo") if isinstance(payload, dict) else None
        total = info.get("totalCount") if isinstance(info, dict) else None
        if not isinstance(rows, list) or type(total) is not int or total < 0 or (expected is not None and expected != total):
            raise FixtureExportError("Operations pagination incomplete or unstable")
        expected = total
        for row in rows:
            rid = row.get("identifier") if isinstance(row, dict) else None
            if not isinstance(rid, str) or not rid or rid in seen:
                raise FixtureExportError("Operations inventory contains invalid or repeated resources")
            seen.add(rid)
        resources.extend(rows)
        if len(resources) == total:
            return resources
        if not rows or len(resources) > total:
            raise FixtureExportError("Operations inventory count mismatch")
    raise FixtureExportError("Operations inventory page limit exceeded")


def _write_fixture(payload: bytes) -> Path:
    path = _fixture_output_path()
    directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    fd = None
    created = False
    identity = None
    try:
        info = os.fstat(directory_fd)
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700:
            raise FixtureExportError("Unsafe fixture directory")
        fd = os.open(path.name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory_fd)
        created = True
        identity = os.fstat(fd)
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w+b") as output:
            fd = None
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
            output.seek(0)
            if output.read() != payload or stat.S_IMODE(os.fstat(output.fileno()).st_mode) != 0o600:
                raise FixtureExportError("Fixture write verification failed")
        return path
    except BaseException:
        if fd is not None:
            os.close(fd)
        if created:
            current = os.stat(path.name, dir_fd=directory_fd, follow_symlinks=False)
            if identity is None or (identity.st_dev, identity.st_ino) != (current.st_dev, current.st_ino):
                raise FixtureExportError("Cannot verify failed fixture ownership for cleanup") from None
            os.unlink(path.name, dir_fd=directory_fd)
        raise
    finally:
        os.close(directory_fd)


def _export_fixture(profile: str) -> None:
    """No reports or payload logs; only the fixed local handoff after Java acceptance."""
    if profile != "devel":
        raise FixtureExportError("Fixture export is restricted to the development profile",
                                 stage="CONFIGURATION", code="UNSUPPORTED_PROFILE")
    with _fixture_stage("OUTPUT_FILE"):
        _fixture_output_path()
    with _fixture_stage("OPS_CONFIGURATION"):
        from vcfcf_common.client import VCFOpsClient
        client = VCFOpsClient.from_env(profile, default_profile="devel")
    if not all(os.environ.get(f"RDM_PROBE_VCENTER_{key}") for key in ("HOST", "USER", "PASSWORD")):
        raise FixtureExportError("Missing configured vCenter probe credentials",
                                 stage="VCENTER_CONFIGURATION", code="MISSING_CONFIGURATION")
    cleanup = {"attempted": False, "status": "not_needed"}
    with _fixture_stage("JAVA_PARSER_SETUP"), _fixture_validator() as validate:
        try:
            with _fixture_stage("VCENTER_READ"):
                mapping = _capture_soap_fixture()
            # Explicitly separate initial token acquisition from inventory reads.
            # Failure here identifies the operation, not necessarily bad credentials.
            with _fixture_stage("OPS_AUTHENTICATION"):
                client.authenticate()
            with _fixture_stage("OPS_READ"):
                resources = _capture_fixture_resources(client)
            with _fixture_stage("VM_IDENTITY_CORRELATION"):
                fixture = _fixture_from_resources(resources, mapping)
            with _fixture_stage("FIXTURE_SCHEMA_VALIDATION"):
                try:
                    payload = (json.dumps(fixture, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
                except (TypeError, ValueError, UnicodeError) as exc:
                    raise FixtureExportError("Fixture serialization unavailable", stage="FIXTURE_SCHEMA_VALIDATION",
                                             code="FIXTURE_SERIALIZATION_FAILED", field="fixture") from exc
            with _fixture_stage("JAVA_PARSER_VALIDATION"):
                validate(payload)
            with _fixture_stage("OUTPUT_FILE"):
                _write_fixture(payload)
        finally:
            _release_operations_token(client, cleanup)


@contextmanager
def _private_fixture_capture():
    """Third-party diagnostics must not disclose endpoint names or raw payloads."""
    previous = logging.root.manager.disable
    try:
        logging.disable(logging.CRITICAL)
        with open(os.devnull, "w", encoding="utf-8") as sink, warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with redirect_stdout(sink), redirect_stderr(sink):
                yield
    finally:
        logging.disable(previous)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="print the offline execution plan (default)")
    parser.add_argument("--execute", action="store_true", help="allow a live read-only probe")
    parser.add_argument("--allow-read-only-lab", action="store_true", help="second explicit acknowledgement required with --execute")
    parser.add_argument("--mode", choices=("vcenter-soap", "vim-json", "ops", "ops-vm-discovery", "soap-ops", "both", "fixture-export"), default="both")
    parser.add_argument("--profile", default="devel", help="VCF Operations profile for --mode ops")
    parser.add_argument("--output", type=Path, help="optional sanitized JSON report; never use a tracked path")
    parser.add_argument("--handoff-output", type=Path,
                        help="discovery-only local mode-0600 file holding a uniquely resolved Operations resource UUID")
    args = parser.parse_args(argv)
    if not args.execute:
        print("OFFLINE PLAN: no network calls. Re-run only after approval with --execute --allow-read-only-lab.")
        print("Modes: vcenter-soap, vim-json, ops, ops-vm-discovery, soap-ops, both. VIM JSON uses an environment-only session header.")
        print("fixture-export: development-only secure runtime fixture capture to its fixed local handoff.")
        return 0
    if not args.allow_read_only_lab:
        parser.error("--execute requires --allow-read-only-lab")
    if args.mode == "fixture-export":
        if args.output or args.handoff_output:
            parser.error("fixture-export uses only its fixed secure output")
        try:
            with _private_fixture_capture():
                _export_fixture(args.profile)
        except Exception as exc:
            stage = exc.stage if isinstance(exc, FixtureExportError) and exc.stage in FixtureExportError.STAGES else "UNCLASSIFIED"
            code = exc.code if isinstance(exc, FixtureExportError) and exc.code in FixtureExportError.CODES else "FAILED"
            field = exc.field if isinstance(exc, FixtureExportError) and exc.field in FixtureExportError.FIELDS else None
            location = f"; field={field}" if field is not None else ""
            print(f"Fixture export failed: stage={stage}; code={code}{location}; no success claimed.", file=sys.stderr)
            return 2
        print("Fixture ready: tmp/rdm-lab-probes/rdm-fixture-vm-71.json; mode 0600; Java parser VALID; one scoped VM and one RDM.")
        return 0
    if args.handoff_output and args.mode != "ops-vm-discovery":
        parser.error("--handoff-output requires --mode ops-vm-discovery")
    report: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "mode": args.mode, "started_at_epoch_ms": int(time.time() * 1000)}
    private_mappings: list[dict[str, Any]] = []
    handoff_resource_id: Optional[str] = None
    try:
        if args.mode in {"vcenter-soap", "soap-ops", "both"}:
            report["vcenter_soap"], private_mappings = _soap_probe()
        if args.mode in {"vim-json", "both"}:
            report["vim_json"] = _vim_json_probe()
        if args.mode == "both":
            report["vim_json_parity"] = _json_parity(report["vcenter_soap"], report["vim_json"])
        if args.mode in {"ops", "soap-ops", "both"}:
            report["operations"] = _ops_probe(args.profile, private_mappings)
        if args.mode == "ops-vm-discovery":
            report["operations_vm_discovery"], handoff_resource_id = _ops_vm_discovery(args.profile)
            if args.handoff_output and handoff_resource_id is None:
                raise OperationsDiscoveryError("refusing handoff without a unique Operations VM match")
    except Exception as exc:
        report["error"] = {"class": type(exc).__name__}
        print(json.dumps(report, sort_keys=True))
        return 2
    if args.output:
        _write_report(args.output, report)
    if args.handoff_output and handoff_resource_id is not None:
        _write_ops_uuid_handoff(args.handoff_output, handoff_resource_id)
    print(json.dumps({"schema_version": SCHEMA_VERSION, "mode": args.mode, "status": "complete",
                      "output_written": bool(args.output), "handoff_written": bool(args.handoff_output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
