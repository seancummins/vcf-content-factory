"""Offline-only synthetic E3.5 fixture projection and secure parser handoff."""
import copy
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parents[1] / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prep = load("rdm_prepare_canonical_fixture")
probe = load("rdm_lab_probe")
NAA = "6123456789abcdef0123456789abcdef"
VC = "11111111-1111-1111-1111-111111111111"
VM = "22222222-2222-2222-2222-222222222222"


def inputs():
    mapping = dict(vcenter_instance_uuid=VC, vm_instance_uuid=VM, virtual_disk_key="2001")
    identifiers = [{"identifierType": {"name": k, "isPartOfUniqueness": u}, "value": v}
                   for k, v, u in [("VMEntityObjectID", "vm-71", True), ("VMEntityVCID", VC, True),
                                   ("VMEntityName", "", False)]]
    vm = {"foreign_vm": {"adapterKindKey": "VMWARE", "resourceKindKey": "VirtualMachine",
                        "name": "SyntheticVM", "resourceIdentifiers": identifiers}, "mapping": mapping}
    evidence = {**mapping, "vm_moid": "vm-71", "lun_uuid": "synthetic-lun", "host_moid": "host-1",
                "lun_observations": [{"host_moid": "host-1", "join_method": "exact_backing_uuid", "lun": {
                    "uuid": "synthetic-lun", "canonicalName": "naa." + NAA, "vendor": "SyntheticVendor",
                    "durableName": {"namespace": "NAA", "namespaceId": 3,
                                    "data": [1, 3, 0, 16, *bytes.fromhex(NAA)]},
                    "alternateName": [], "descriptor": [], "capacity": {"block": 128, "blockSize": 512}}}]}
    return vm, evidence, {"naa": "0x" + NAA}


def test_projection_preserves_key_and_qualified_descriptor():
    vm, evidence, ref = inputs()
    before = copy.deepcopy(vm)
    result = prep.build_fixture(vm, evidence, ref)
    attachment = result["attachments"][0]
    assert result["schema_version"] == "2"
    assert attachment["foreign_vm"] == vm["foreign_vm"] and attachment["mapping"] == vm["mapping"]
    assert attachment["canonical_lun"]["descriptors"][0]["data_hex"] == "01030010" + NAA
    assert attachment["canonical_lun"]["properties"]["capacity_blocks"] == "128"
    attachment["foreign_vm"]["name"] = "changed"
    assert vm == before


@pytest.mark.parametrize("field", ["vcenter_instance_uuid", "vm_instance_uuid", "virtual_disk_key", "vm_moid"])
def test_wrong_mapping_scope_rejected(field):
    vm, evidence, ref = inputs()
    evidence[field] = "different"
    with pytest.raises(ValueError): prep.build_fixture(vm, evidence, ref)


def test_conflicting_naa_not_hidden_by_projection():
    vm, evidence, ref = inputs()
    lun = evidence["lun_observations"][0]["lun"]
    alternate = copy.deepcopy(lun["durableName"])
    alternate["data"][-1] ^= 1
    lun["alternateName"].append(alternate)
    with pytest.raises(ValueError): prep.build_fixture(vm, evidence, ref)


def test_duplicate_json_keys_rejected():
    with pytest.raises(ValueError): json.loads('{"naa":"a","naa":"b"}', object_pairs_hook=prep._json_object)


def test_actual_java_parser_accepts_legacy_and_projected_v2():
    if not os.environ.get("VCFCF_SDK_JAR"):
        pytest.skip("explicit local SDK path required; never install")
    vm, evidence, ref = inputs()
    with probe._fixture_validator() as validate:
        validate(json.dumps(vm).encode())
        validate(json.dumps(prep.build_fixture(vm, evidence, ref)).encode())


def setup_cli(tmp_path, monkeypatch):
    scratch = tmp_path / "tmp/rdm-lab-probes"
    scratch.mkdir(parents=True, mode=0o700)
    monkeypatch.setattr(probe, "__file__", str(tmp_path / "scripts/rdm_lab_probe.py"))
    monkeypatch.setattr(probe.subprocess, "run", lambda args, **kw:
                        SimpleNamespace(returncode=0 if args[1] == "check-ignore" else 1))
    paths = [scratch / name for name in ("vm.json", "evidence.json", "reference.json")]
    for path, value in zip(paths, inputs()): probe._write_report(path, value)
    original = prep._module
    monkeypatch.setattr(prep, "_module", lambda name: probe if name == "rdm_lab_probe" else original(name))
    output = scratch / "fixture.json"
    args = ["--vm-fixture", str(paths[0]), "--lun-evidence", str(paths[1]),
            "--storage-reference", str(paths[2]), "--output", str(output)]
    return paths, output, args


def test_cli_validates_before_exclusive_private_write(tmp_path, monkeypatch, capsys):
    paths, output, args = setup_cli(tmp_path, monkeypatch)
    validated = []
    @contextmanager
    def validator(): yield lambda payload: validated.append(json.loads(payload))
    monkeypatch.setattr(probe, "_fixture_validator", validator)
    assert prep.main(args) == 0
    assert output.stat().st_mode & 0o777 == 0o600
    assert json.loads(output.read_text()) == validated[0]
    assert NAA not in capsys.readouterr().out
    assert prep.main(args) == 2  # Never overwrite an existing fixture.


@pytest.mark.parametrize("failure", ["parser", "permissions", "duplicate", "serialization"])
def test_failure_has_no_fixture_or_sensitive_diagnostics(failure, tmp_path, monkeypatch, capsys):
    paths, output, args = setup_cli(tmp_path, monkeypatch)
    @contextmanager
    def validator():
        def validate(payload):
            if failure == "parser": raise ValueError("secret-parser-payload")
        yield validate
    monkeypatch.setattr(probe, "_fixture_validator", validator)
    if failure == "permissions": paths[1].chmod(0o644)
    if failure == "duplicate":
        paths[2].write_text('{"naa":"secret","naa":"secret2"}')
    if failure == "serialization":
        original = prep.build_fixture
        def invalid(*args):
            result = original(*args)
            result["unsupported"] = object()
            return result
        monkeypatch.setattr(prep, "build_fixture", invalid)
    assert prep.main(args) == 2
    assert not output.exists()
    text = capsys.readouterr().out
    assert "secret" not in text and NAA not in text


def test_evidence_size_limit_explicit_default_guard_preserved(tmp_path, monkeypatch):
    paths, _, _ = setup_cli(tmp_path, monkeypatch)
    path = paths[1]
    path.write_text(" " * 9000)
    with pytest.raises(ValueError): probe._lun_local_path(path, reading=True)
    assert probe._lun_local_path(path, reading=True, max_bytes=1048576) == path
    with pytest.raises(ValueError): probe._lun_local_path(path, reading=True, max_bytes=1048577)
