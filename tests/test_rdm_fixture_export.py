"""Synthetic-only fixture-export contracts; no live access or inventory logging."""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest


SPEC = importlib.util.spec_from_file_location("rdm_fixture_probe", Path(__file__).parents[1] / "scripts/rdm_lab_probe.py")
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)
VC = "11111111-1111-4111-8111-111111111111"
VM = "22222222-2222-4222-8222-222222222222"


def mapping():
    return {"vm_moid": "vm-71", "vcenter_instance_uuid": VC,
            "vm_instance_uuid": VM, "virtual_disk_key": "2000"}


def resource(vcid=VC, moid="vm-71", rid="synthetic-ops-id"):
    return {"identifier": rid, "resourceKey": {"adapterKindKey": "VMWARE",
        "resourceKindKey": "VirtualMachine", "name": " duplicate display name ",
        "resourceIdentifiers": [
            {"identifierType": {"name": "VMEntityObjectID", "isPartOfUniqueness": True}, "value": moid},
            {"identifierType": {"name": "VMEntityVCID", "isPartOfUniqueness": True}, "value": vcid},
            {"identifierType": {"name": "VMEntityName", "isPartOfUniqueness": False}, "value": " preserve exactly "},
        ]}}


def test_exact_scoped_key_preserves_all_values_flags_and_duplicate_names():
    target = resource()
    target["resourceKey"]["links"] = []  # Nonidentity API metadata is not fixture schema.
    fixture = probe._fixture_from_resources([resource("33333333-3333-4333-8333-333333333333"),
                                             resource(moid="vm-72"), target], mapping())
    assert fixture["foreign_vm"]["resourceIdentifiers"] == target["resourceKey"]["resourceIdentifiers"]
    assert fixture["foreign_vm"]["name"] == target["resourceKey"]["name"]
    assert fixture["mapping"] == {k: v for k, v in mapping().items() if k != "vm_moid"}
    assert set(fixture) == {"foreign_vm", "mapping"}


@pytest.mark.parametrize("resources", [[], [resource(), resource(rid="other")],
    [resource("33333333-3333-4333-8333-333333333333")], [None], [{}]])
def test_absent_ambiguous_unscoped_or_malformed_vm_fails(resources):
    with pytest.raises(probe.FixtureExportError):
        probe._fixture_from_resources(resources, mapping())


@pytest.mark.parametrize("change", ["missing_flag", "false_flag", "string_flag", "duplicate",
                                    "missing_scope", "wrong_kind", "empty_value", "bad_identifier"])
def test_malformed_identity_is_not_repaired(change):
    row = resource()
    ids = row["resourceKey"]["resourceIdentifiers"]
    if change == "missing_flag": del ids[1]["identifierType"]["isPartOfUniqueness"]
    elif change == "false_flag": ids[1]["identifierType"]["isPartOfUniqueness"] = False
    elif change == "string_flag": ids[1]["identifierType"]["isPartOfUniqueness"] = "true"
    elif change == "duplicate": ids.append(deepcopy(ids[0]))
    elif change == "missing_scope": del ids[1]
    elif change == "wrong_kind": row["resourceKey"]["resourceKindKey"] = "HostSystem"
    elif change == "empty_value": ids[0]["value"] = ""
    elif change == "bad_identifier": ids.append(None)
    with pytest.raises(probe.FixtureExportError):
        probe._fixture_from_resources([row], mapping())


@pytest.mark.parametrize("count", [0, 2])
def test_ambiguous_or_absent_rdm_fails(count):
    disk = SimpleNamespace(key=2000, backing=SimpleNamespace(lunUuid="synthetic-lun"))
    with pytest.raises(probe.FixtureExportError):
        probe._single_rdm_fixture_mapping(VC, VM, [disk] * count)


@pytest.mark.parametrize("key", [None, True, "2000", -1, 0, 2147483648])
def test_invalid_disk_key_fails(key):
    with pytest.raises(probe.FixtureExportError):
        probe._single_rdm_fixture_mapping(VC, VM, [SimpleNamespace(key=key, backing=SimpleNamespace(lunUuid="lun"))])


def test_soap_tuple_and_snapshot_stability():
    disk = SimpleNamespace(key=2000, backing=SimpleNamespace(lunUuid="synthetic-lun"))
    assert probe._single_rdm_fixture_mapping(VC, VM, [disk]) == mapping()
    before = {"config.instanceUuid": VM, "config.changeVersion": "1", "runtime.host": SimpleNamespace(_moId="host-1")}
    probe._validate_fixture_snapshot(before, before)
    for key in before:
        after = {**before, key: None}
        with pytest.raises(probe.FixtureExportError):
            probe._validate_fixture_snapshot(before, after)


@pytest.mark.parametrize("payload", [None, {}, {"resourceList": [], "pageInfo": {"totalCount": True}},
    {"resourceList": [None], "pageInfo": {"totalCount": 1}},
    {"resourceList": [resource(), resource()], "pageInfo": {"totalCount": 2}},
    {"resourceList": [], "pageInfo": {"totalCount": 1}}])
def test_malformed_pagination_fails(payload):
    client = SimpleNamespace(_request=lambda *args, **kwargs: SimpleNamespace(status_code=200, json=lambda: payload))
    with pytest.raises(probe.FixtureExportError):
        probe._capture_fixture_resources(client)


def test_read_only_endpoint_and_complete_pagination():
    def request(method, path, params, timeout):
        assert (method, path) == ("GET", "/api/resources")
        assert timeout == 30
        assert params["adapterKind"] == "VMWARE" and params["resourceKind"] == "VirtualMachine"
        row = resource(moid=f"vm-{71 + params['page']}", rid=f"id-{params['page']}")
        return SimpleNamespace(status_code=200, json=lambda: {"resourceList": [row], "pageInfo": {"totalCount": 2}})
    assert len(probe._capture_fixture_resources(SimpleNamespace(_request=request))) == 2


def test_secure_creation_and_no_overwrite(tmp_path, monkeypatch):
    tmp_path.chmod(0o700)
    path = tmp_path / "fixture.json"
    monkeypatch.setattr(probe, "_fixture_output_path", lambda: path)
    assert probe._write_fixture(b"synthetic\n") == path
    assert path.stat().st_mode & 0o777 == 0o600
    with pytest.raises(FileExistsError): probe._write_fixture(b"different")
    assert path.read_bytes() == b"synthetic\n"


def test_failed_write_cleans_up_only_new_file(tmp_path, monkeypatch):
    tmp_path.chmod(0o700)
    path = tmp_path / "fixture.json"
    monkeypatch.setattr(probe, "_fixture_output_path", lambda: path)
    monkeypatch.setattr(probe.os, "fsync", lambda fd: (_ for _ in ()).throw(OSError("synthetic failure")))
    with pytest.raises(OSError): probe._write_fixture(b"sensitive synthetic payload")
    assert not path.exists()


def test_fixed_path_ignore_checks_fail_closed(monkeypatch):
    path = Path(probe.__file__).parents[1] / "tmp/rdm-lab-probes/rdm-fixture-vm-71.json"
    if path.exists(): pytest.skip("operator fixture already exists; never touch it")
    calls = []
    def run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0 if "check-ignore" in args else 1)
    monkeypatch.setattr(probe.subprocess, "run", run)
    assert probe._fixture_output_path() == path
    assert all(args[-1] == "tmp/rdm-lab-probes/rdm-fixture-vm-71.json" for args in calls)
    monkeypatch.setattr(probe.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(returncode=128))
    with pytest.raises(probe.FixtureExportError): probe._fixture_output_path()


def test_cli_guards_and_sanitizes_all_diagnostics(monkeypatch, capsys):
    with pytest.raises(SystemExit): probe.main(["--execute", "--mode", "fixture-export"])
    with pytest.raises(SystemExit):
        probe.main(["--execute", "--allow-read-only-lab", "--mode", "fixture-export", "--output", "any"])
    capsys.readouterr()
    def fail(profile):
        print("RAW_SYNTHETIC_IDENTITY")
        raise ValueError("RAW_SYNTHETIC_IDENTITY")
    monkeypatch.setattr(probe, "_export_fixture", fail)
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "fixture-export"]) == 2
    output = capsys.readouterr()
    assert "RAW_SYNTHETIC_IDENTITY" not in output.out + output.err


def test_parser_rejection_never_writes_and_releases_token(monkeypatch):
    import vcfcf_common.client
    monkeypatch.setattr(probe, "_fixture_output_path", lambda: None)
    for key in ("HOST", "USER", "PASSWORD"):
        monkeypatch.setenv(f"RDM_PROBE_VCENTER_{key}", "synthetic")
    client = SimpleNamespace(authenticate=lambda: None)
    monkeypatch.setattr(vcfcf_common.client.VCFOpsClient, "from_env", lambda *args, **kwargs: client)
    monkeypatch.setattr(probe, "_capture_soap_fixture", mapping)
    monkeypatch.setattr(probe, "_capture_fixture_resources", lambda client: [resource()])
    @contextmanager
    def validator():
        yield lambda payload: (_ for _ in ()).throw(probe.FixtureExportError("rejected"))
    monkeypatch.setattr(probe, "_fixture_validator", validator)
    monkeypatch.setattr(probe, "_write_fixture", lambda payload: pytest.fail("wrote unvalidated fixture"))
    released = []
    monkeypatch.setattr(probe, "_release_operations_token", lambda *args: released.append(True))
    with pytest.raises(probe.FixtureExportError): probe._export_fixture("devel")
    assert released == [True]
    with pytest.raises(probe.FixtureExportError): probe._export_fixture("prod")


def test_real_e21_java_parser_accepts_projection_and_rejects_conflicts():
    if not os.environ.get("VCFCF_SDK_JAR"):
        pytest.skip("explicit local SDK path needed; never install")
    fixture = probe._fixture_from_resources([resource()], mapping())
    with probe._fixture_validator() as validate:
        validate(json.dumps(fixture).encode())
        for corrupted in (
            {**fixture, "mapping": {**fixture["mapping"], "vcenter_instance_uuid": VM}},
            {**fixture, "mapping": {**fixture["mapping"], "virtual_disk_key": "02000"}},
        ):
            with pytest.raises(probe.FixtureExportError): validate(json.dumps(corrupted).encode())
