"""Offline-only E3.5 fixture preparation. No VMware or array connections."""
from __future__ import annotations

import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path


def _module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Ambiguous JSON object")
        result[key] = value
    return result


def build_fixture(vm_fixture, evidence, reference):
    """Project qualified evidence; actual Java parser remains the final gate."""
    identity = _module("rdm_lun_identity")
    report, _ = identity.analyze(evidence, reference)
    if report["qualification"] != "CONDITIONALLY QUALIFIED":
        raise ValueError("Evidence is not qualified for the bounded POC")
    if not isinstance(vm_fixture, dict) or set(vm_fixture) != {"foreign_vm", "mapping"}:
        raise ValueError("A legacy exact-key VM fixture is required")
    mapping = vm_fixture["mapping"]
    if not isinstance(mapping, dict) or set(mapping) != {"vcenter_instance_uuid", "vm_instance_uuid", "virtual_disk_key"}:
        raise ValueError("Missing mapping identity")
    if any(mapping[k] != evidence.get(k) for k in mapping):
        raise ValueError("Evidence does not describe the configured mapping")
    foreign = vm_fixture["foreign_vm"]
    ids = foreign.get("resourceIdentifiers", []) if isinstance(foreign, dict) else []
    moids = [entry.get("value") for entry in ids if isinstance(entry, dict)
             and isinstance(entry.get("identifierType"), dict)
             and entry["identifierType"].get("name") == "VMEntityObjectID"]
    if moids != [evidence.get("vm_moid")]:
        raise ValueError("Evidence VM identity differs")
    current = [o for o in evidence["lun_observations"] if o["host_moid"] == evidence["host_moid"]]
    if len(current) != 1:
        raise ValueError("Current-host observation is ambiguous")
    lun = current[0]["lun"]
    names = ([lun["durableName"]] if lun.get("durableName") is not None else []) + lun["alternateName"]
    descriptors = [{"namespace": item["namespace"], "namespace_id": str(item["namespaceId"]),
                    "data_hex": bytes(b & 255 for b in item["data"]).hex()}
                   for item in names if isinstance(item, dict) and isinstance(item.get("namespace"), str)
                   and item["namespace"].lower() == "naa"]
    properties = {}
    for source, target in (("vendor", "vendor"), ("model", "model"), ("revision", "revision"),
                           ("serialNumber", "serial_number"), ("lunType", "lun_type"), ("deviceType", "device_type")):
        value = lun.get(source)
        if value is not None:
            if not isinstance(value, str):
                raise ValueError("Unsupported descriptive value")
            if value:
                properties[target] = value
    if lun.get("capacity") is not None:
        properties.update(capacity_blocks=str(lun["capacity"]["block"]),
                          capacity_block_size=str(lun["capacity"]["blockSize"]))
    local = {"provenance": "vsphere-soap-fixture", "backing_lun_uuid": evidence["lun_uuid"],
             "scsi_lun_uuid": lun["uuid"], "canonical_name": lun["canonicalName"],
             "storage_reference": reference["naa"], "descriptors": descriptors, "properties": properties}
    return {"schema_version": "2", "attachments": [{"foreign_vm": deepcopy(foreign),
            "mapping": deepcopy(mapping), "canonical_lun": local}]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("vm-fixture", "lun-evidence", "storage-reference", "output"):
        parser.add_argument("--" + arg, type=Path, required=True)
    args = parser.parse_args(argv)
    probe = _module("rdm_lab_probe")
    stage = "INPUT"
    try:
        with probe._private_fixture_capture():
            output = probe._lun_local_path(args.output)
            def read(path):
                return json.loads(probe._lun_local_path(path, reading=True, max_bytes=1048576).read_text(encoding="utf-8"),
                                  object_pairs_hook=_json_object)
            vm, evidence, reference = (read(path) for path in
                                       (args.vm_fixture, args.lun_evidence, args.storage_reference))
            stage = "QUALIFICATION_AND_SCOPE"
            fixture = build_fixture(vm, evidence, reference)
            payload = json.dumps(fixture).encode("utf-8")
            stage = "JAVA_PARSER"
            with probe._fixture_validator() as validate:
                validate(payload)
            stage = "OUTPUT"
            probe._lun_local_path(output)
            probe._write_report(output, fixture)
    except Exception:
        print("Fixture preparation failed; stage=" + stage + "; no success claimed.")
        return 2
    print("Offline fixture prepared and Java-validated; mode 0600; one attachment; contents not displayed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
