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
    mappings = [{"vcenter_instance_uuid": "vc-a", "vm_moid": "vm-123", "disk_key": 7, "label": "Hard disk 2",
                 "file_name": "[ds] vm/rdm.vmdk", "lun_uuid": "lun-uuid",
                 "controller_unit": "scsi0:1"}]
    rows = probe._instance_correlations(
        {"virtualDisk:scsi0:1": {"read"}},
        {"virtualDisk:scsi0:1": {"label": "Hard disk 2", "lunUuid": "lun-uuid"}},
        [{"identifierType": {"name": "VMEntityObjectID"}, "value": "vm-123"},
         {"identifierType": {"name": "VMEntityVCID"}, "value": "vc-a"}], mappings,
    )
    assert rows[0]["confidence"] == "high"
    assert "instance_equals_controller_unit" in rows[0]["methods"]
    assert "vm-123" not in repr(rows)
    assert "lun-uuid" not in repr(rows)


def test_soap_ops_correlation_uses_composite_vm_identity_with_overlapping_disk_keys():
    mappings = [
        {"vcenter_instance_uuid": "vc-a", "vm_moid": "vm-71", "disk_key": 7,
         "label": "RDM A", "file_name": "a.vmdk", "lun_uuid": "lun-a", "controller_unit": "scsi0:1"},
        {"vcenter_instance_uuid": "vc-b", "vm_moid": "vm-71", "disk_key": 7,
         "label": "RDM B", "file_name": "b.vmdk", "lun_uuid": "lun-b", "controller_unit": "scsi0:2"},
    ]
    report = probe._rdm_instance_correlation_report(
        {"virtualDisk:scsi0:1": {"read"}},
        {"virtualDisk:scsi0:1": {"lunUuid": "lun-a"}},
        [{"identifierType": {"name": "VMEntityObjectID"}, "value": "vm-71"},
         {"identifierType": {"name": "VMEntityVCID"}, "value": "vc-a"}], mappings,
    )
    assert report["identity_status"] == "complete_exact_soap_vm_identity"
    assert len(report["matched"]) == 1
    assert report["matched"][0]["confidence"] == "high"
    assert report["unmatched_rdm_mappings"] == []
    assert "lun-b" not in repr(report)


def test_soap_ops_correlation_distinguishes_missing_instances_from_no_identifier_match():
    mapping = {"vcenter_instance_uuid": "vc-a", "vm_moid": "vm-71", "disk_key": 7,
               "label": "RDM A", "file_name": "a.vmdk", "lun_uuid": "lun-a", "controller_unit": "scsi0:1"}
    identifiers = [{"identifierType": {"name": "VMEntityObjectID"}, "value": "vm-71"},
                   {"identifierType": {"name": "VMEntityVCID"}, "value": "vc-a"}]
    missing = probe._rdm_instance_correlation_report({}, {}, identifiers, [mapping])
    assert missing["unmatched_rdm_mappings"][0]["status"] == "missing_instance_data"
    nonmatching = probe._rdm_instance_correlation_report(
        {"virtualDisk:scsi1:9": {"read"}}, {}, identifiers, [mapping]
    )
    assert nonmatching["unmatched_rdm_mappings"][0]["status"] == "no_candidate_identifier_matched"
    assert nonmatching["unmatched_operations_disk_instances"][0]["status"] == "no_soap_rdm_candidate_identifier_matched"


def test_soap_ops_correlation_refuses_a_resource_from_another_vcenter():
    mapping = {"vcenter_instance_uuid": "vc-a", "vm_moid": "vm-71", "disk_key": 7,
               "label": "RDM A", "file_name": "a.vmdk", "lun_uuid": "lun-a", "controller_unit": "scsi0:1"}
    report = probe._rdm_instance_correlation_report(
        {"virtualDisk:scsi0:1": {"read"}}, {},
        [{"identifierType": {"name": "VMEntityObjectID"}, "value": "vm-71"},
         {"identifierType": {"name": "VMEntityVCID"}, "value": "vc-b"}], [mapping],
    )
    assert report["identity_status"] == "no_matching_soap_vm_identity"
    assert report["matched"] == []


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


def _vm_resource(resource_id, name, moid, vcid, *, complete=True):
    identifiers = [
        {"identifierType": {"name": "VMEntityObjectID", "isPartOfUniqueness": True}, "value": moid},
        {"identifierType": {"name": "VMEntityVCID", "isPartOfUniqueness": True}, "value": vcid},
        {"identifierType": {"name": "VMEntityName", "isPartOfUniqueness": False}, "value": name},
    ]
    if not complete:
        identifiers[1]["identifierType"].pop("isPartOfUniqueness")
    return {"identifier": resource_id, "resourceKey": {"name": name, "resourceIdentifiers": identifiers}}


def test_vm_discovery_scopes_same_moid_to_owning_vcenter():
    resources = [
        _vm_resource("ops-vc-a", "lab-rdm", "vm-71", "vc-a"),
        _vm_resource("ops-vc-b", "lab-rdm", "vm-71", "vc-b"),
    ]
    result, handoff = probe._ops_vm_match(resources, "vm-71", "vc-b", "lab-rdm")
    assert result["status"] == "unique"
    assert handoff == "ops-vc-b"
    assert result["candidate_count"] == 2
    assert all(candidate["matching_evidence"]["vm_moid_exact"] for candidate in result["candidates"])
    assert "ops-vc-b" not in repr(result)
    assert "vc-b" not in repr(result)


def test_vm_discovery_duplicate_display_names_are_not_identity_proof():
    resources = [
        _vm_resource("ops-first", "duplicate-name", "vm-71", "vc-a"),
        _vm_resource("ops-second", "duplicate-name", "vm-72", "vc-a"),
    ]
    result, handoff = probe._ops_vm_match(resources, "vm-71", "vc-a", "duplicate-name")
    assert result["status"] == "unique"
    assert handoff == "ops-first"
    assert all(candidate["matching_evidence"]["display_name_exact_discovery_only"] for candidate in result["candidates"])
    assert sum(candidate["matching_evidence"]["pair_exact"] for candidate in result["candidates"]) == 1


def test_vm_discovery_never_selects_multiple_or_incomplete_pair_matches():
    duplicate = [_vm_resource("ops-one", "lab", "vm-71", "vc-a"), _vm_resource("ops-two", "lab", "vm-71", "vc-a")]
    result, handoff = probe._ops_vm_match(duplicate, "vm-71", "vc-a")
    assert result["status"] == "ambiguous"
    assert handoff is None
    incomplete = [_vm_resource("ops-one", "lab", "vm-71", "vc-a", complete=False)]
    result, handoff = probe._ops_vm_match(incomplete, "vm-71", "vc-a")
    assert result["status"] == "incomplete"
    assert handoff is None


def test_ops_handoff_is_restricted_and_contains_only_local_operator_input():
    repo_root = Path(probe.__file__).parents[1]
    handoff = repo_root / "tmp" / "rdm-lab-probes" / "test-ops-handoff.json"
    if handoff.exists():
        handoff.unlink()
    try:
        probe._write_ops_uuid_handoff(handoff, "ops-resource-uuid")
        assert handoff.stat().st_mode & 0o777 == 0o600
        assert handoff.read_text(encoding="utf-8") == '{\n  "RDM_PROBE_OPS_RESOURCE_IDS": [\n    "ops-resource-uuid"\n  ]\n}\n'
        with pytest.raises(ValueError):
            probe._write_ops_uuid_handoff(handoff, "again")
    finally:
        if handoff.exists():
            handoff.unlink()
