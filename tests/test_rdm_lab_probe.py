"""Safety contracts for the RDM read-only lab probe."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


_PATH = Path(__file__).parents[1] / "scripts" / "rdm_lab_probe.py"
_SPEC = importlib.util.spec_from_file_location("rdm_lab_probe", _PATH)
assert _SPEC and _SPEC.loader
probe = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(probe)


def test_plan_mode_does_not_require_live_configuration(capsys):
    assert probe.main([]) == 0
    assert "OFFLINE PLAN" in capsys.readouterr().out


def test_execute_requires_second_explicit_acknowledgement():
    try:
        probe.main(["--execute"])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover - parser.error always exits
        raise AssertionError("live execution acknowledgement was not required")


def test_fingerprint_never_returns_raw_value():
    assert probe._fp("lun-sensitive-value") != "lun-sensitive-value"
    assert probe._fp(None) is None


def test_json_parity_distinguishes_missing_from_empty_fields():
    soap = {"rdm_mappings": [{"vm_moid_fp": "vm", "disk_key_fp": "disk",
        "lun_uuid_fp": None, "lun_uuid_present": True,
        "device_name_fp": None, "device_name_present": True,
        "file_name_fp": None, "file_name_present": True,
        "compatibility_mode": "physicalMode", "compatibility_mode_present": True}]}
    vim_json = {"rdm_disks": [{"vm_moid_fp": "vm", "disk_key_fp": "disk",
        "lun_uuid_fp": None, "lun_uuid_present": False,
        "device_name_fp": None, "device_name_present": True,
        "file_name_fp": None, "file_name_present": True,
        "compatibility_mode": "physicalMode", "compatibility_mode_present": True}], "failures": []}
    assert probe._json_parity(soap, vim_json)["status"] == "fail"


def test_output_path_refuses_existing_or_outside_scratch(tmp_path):
    existing = tmp_path / "existing.json"
    existing.write_text("x", encoding="utf-8")
    try:
        probe._safe_output_path(existing)
    except ValueError:
        pass
    else:  # pragma: no cover - safety contract
        raise AssertionError("existing file was accepted as a lab report output")
    try:
        probe._safe_output_path(tmp_path / "new-outside-scratch.json")
    except ValueError:
        pass
    else:  # pragma: no cover - safety contract
        raise AssertionError("outside scratch path was accepted as a lab report output")


def test_global_lun_match_does_not_claim_current_host_visibility():
    other_host = {"host_moid_fp": "other", "canonical_name_fp": "naa"}
    global_status, current_status, global_views, current_views = probe._lun_visibility(
        "uuid", [other_host], "current", unstable=False
    )
    assert global_status == "exact_uuid_one_host_lun"
    assert current_status == "not_visible_on_current_host"
    assert global_views == [other_host]
    assert current_views == []


def test_property_collection_completeness_rejects_missing_object_or_property():
    with pytest.raises(probe.PropertyCollectionError):
        probe._validate_property_completeness({"vm-1", "vm-2"}, {"vm-1": {"runtime.host": object()}}, {})
    with pytest.raises(probe.PropertyCollectionError):
        probe._validate_property_completeness({"vm-1"}, {"vm-1": {}}, {"vm-1": {"runtime.host"}})


def test_vim_json_parser_distinguishes_documented_and_unrecognized_shapes():
    devices, representation = probe._vim_json_devices({"hardware": {"device": [{"key": 1}]}})
    assert representation == "device_array"
    assert devices == [{"key": 1}]
    devices, representation = probe._vim_json_devices({"hardware": {"device": {"_value": [{"key": 1}]}}})
    assert representation == "boxed_device_array"
    assert devices == [{"key": 1}]
    devices, representation = probe._vim_json_devices({"hardware": {"device": {}}})
    assert devices is None
    assert representation == "unrecognized_device_representation"


def test_operations_stats_parser_requires_documented_shape():
    payload = {"values": [{"stat-list": {"stat": [
        {"statKey": {"key": "virtualDisk:scsi0:1|read"}},
        {"statKey": {"key": "cpu|usage"}},
    ]}}]}
    assert probe._operations_instances(payload) == {"virtualDisk:scsi0:1": {"read"}}
    with pytest.raises(probe.OperationsShapeError):
        probe._operations_instances({"values": [{}]})


def test_operations_disk_instance_correlation_uses_in_memory_candidates_only():
    mappings = [{"vm_moid": "vm-123", "disk_key": 7, "label": "Hard disk 2",
                 "file_name": "[ds] vm/rdm.vmdk", "lun_uuid": "lun-uuid",
                 "controller_unit": "scsi0:1"}]
    rows = probe._instance_correlations(
        {"virtualDisk:scsi0:1": {"read"}},
        {"virtualDisk:scsi0:1": {"label": "Hard disk 2", "lunUuid": "lun-uuid"}},
        [{"identifierType": {"name": "VMEntityObjectID"}, "value": "vm-123"}], mappings,
    )
    assert rows[0]["confidence"] == "high"
    assert "instance_equals_controller_unit" in rows[0]["methods"]
    assert "vm-123" not in repr(rows)
    assert "lun-uuid" not in repr(rows)


def test_token_release_failure_is_recorded_without_raising():
    class Client:
        _token = "present"

        @staticmethod
        def _request(method, path):
            assert (method, path) == ("POST", "/api/auth/token/release")
            raise RuntimeError("release unavailable")

    cleanup = {"attempted": False, "status": "not_needed"}
    probe._release_operations_token(Client(), cleanup)
    assert cleanup == {"attempted": True, "status": "release_exception"}


def test_report_creation_is_exclusive_and_restrictive(tmp_path):
    repo_root = Path(probe.__file__).parents[1]
    scratch = repo_root / "tmp" / "rdm-lab-probes"
    output = scratch / "test-exclusive-report.json"
    if output.exists():
        output.unlink()
    try:
        probe._write_report(output, {"status": "ok"})
        assert output.stat().st_mode & 0o777 == 0o600
        with pytest.raises(ValueError):
            probe._write_report(output, {"status": "again"})
    finally:
        if output.exists():
            output.unlink()
