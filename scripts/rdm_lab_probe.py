#!/usr/bin/env python3
"""Read-only, opt-in lab probe for the proposed vSphere RDM topology pack.

The default is offline plan output.  A live read requires both --execute and
--allow-read-only-lab.  Secrets are environment-only and all emitted identity
values are fingerprints, never raw inventory values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Optional


SCHEMA_VERSION = "vcfcf-rdm-lab-probe-v1"


class FieldReadError(RuntimeError):
    """A retrieved VIM object could not expose a requested field safely."""


class PropertyCollectionError(RuntimeError):
    """A PropertyCollector response was incomplete for the requested objects."""


class OperationsShapeError(RuntimeError):
    """A public Operations response did not have its documented read shape."""


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
                    "vm_moid": vm_moid, "disk_key": disk_key, "label": label, "file_name": file_name,
                    "lun_uuid": lun_uuid, "controller_unit": None if bus is None or unit_number is None else f"scsi{bus}:{unit_number}",
                })
        return ({"vc_instance_fp": _fp(_get(content.about, "instanceUuid")), "vm_requested": len(vm_moids),
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


def _instance_correlations(instances: dict[str, set[str]], properties: dict[str, dict[str, Any]],
                           identifiers: list[dict[str, Any]], mappings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    vm_moid = next((item.get("value") for item in identifiers
                    if (item.get("identifierType") or {}).get("name") == "VMEntityObjectID"), None)
    candidates = [item for item in mappings if item["vm_moid"] == vm_moid]
    results = []
    for instance, leaves in instances.items():
        for mapping in candidates:
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
            values = properties.get(instance, {})
            if mapping["label"] and values.get("label") == mapping["label"]:
                methods.append("property_label")
            if mapping["file_name"] and values.get("fileName") == mapping["file_name"]:
                methods.append("property_file_name")
            if mapping["lun_uuid"] and values.get("lunUuid") == mapping["lun_uuid"]:
                methods.append("property_lun_uuid")
            if not methods:
                continue
            confidence = "high" if "instance_equals_controller_unit" in methods and len(methods) > 1 else "medium" if len(methods) > 1 else "low"
            results.append({"instance_token_fp": _fp(instance), "disk_key_fp": _fp(mapping["disk_key"]),
                            "methods": methods, "confidence": confidence,
                            "observed_metric_leaves": sorted(leaves)})
    return results


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
                "disk_instance_correlations": _instance_correlations(instances, props_by_instance, identifiers, mappings or []),
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


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true", help="print the offline execution plan (default)")
    parser.add_argument("--execute", action="store_true", help="allow a live read-only probe")
    parser.add_argument("--allow-read-only-lab", action="store_true", help="second explicit acknowledgement required with --execute")
    parser.add_argument("--mode", choices=("vcenter-soap", "vim-json", "ops", "both"), default="both")
    parser.add_argument("--profile", default="devel", help="VCF Operations profile for --mode ops")
    parser.add_argument("--output", type=Path, help="optional sanitized JSON report; never use a tracked path")
    args = parser.parse_args(argv)
    if not args.execute:
        print("OFFLINE PLAN: no network calls. Re-run only after approval with --execute --allow-read-only-lab.")
        print("Modes: vcenter-soap, vim-json, ops, both. VIM JSON uses an environment-only session header.")
        return 0
    if not args.allow_read_only_lab:
        parser.error("--execute requires --allow-read-only-lab")
    report: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "mode": args.mode, "started_at_epoch_ms": int(time.time() * 1000)}
    private_mappings: list[dict[str, Any]] = []
    try:
        if args.mode in {"vcenter-soap", "both"}:
            report["vcenter_soap"], private_mappings = _soap_probe()
        if args.mode in {"vim-json", "both"}:
            report["vim_json"] = _vim_json_probe()
        if args.mode == "both":
            report["vim_json_parity"] = _json_parity(report["vcenter_soap"], report["vim_json"])
        if args.mode in {"ops", "both"}:
            report["operations"] = _ops_probe(args.profile, private_mappings)
    except Exception as exc:
        report["error"] = {"class": type(exc).__name__}
        print(json.dumps(report, sort_keys=True))
        return 2
    if args.output:
        _write_report(args.output, report)
    print(json.dumps({"schema_version": SCHEMA_VERSION, "mode": args.mode, "status": "complete",
                      "output_written": bool(args.output)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
