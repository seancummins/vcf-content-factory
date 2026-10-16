"""Synthetic-only contracts for explicitly invoked, read-only LUN discovery."""
import copy
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parents[1] / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lun = load("rdm_lun_discovery")
probe = load("rdm_lab_probe")
SOURCE = {"lun_uuid": "secret-lun", "canonical_name": "naa.secret", "vcenter_instance_uuid": "secret-vc"}
BINDINGS = {"adapter_kind": "TEST", "resource_kind": "PhysicalLun", "granularity": "physical_lun",
    "uuid": {"source": "identifier", "name": "uuid"},
    "vcenter_instance_uuid": {"source": "identifier", "name": "vc"}}


def row(rid="secret-resource", uuid="secret-lun", vc="secret-vc", kind="PhysicalLun"):
    return {"resource": {"identifier": rid, "resourceKey": {"adapterKindKey": "TEST", "resourceKindKey": kind,
        "name": "secret-display", "resourceIdentifiers": [
            {"identifierType": {"name": name, "isPartOfUniqueness": True}, "value": value}
            for name, value in (("uuid", uuid), ("vc", vc))]}}, "properties": {"canonical": "naa.secret"}}


def test_no_observed_kind_is_not_evidence_for_canonical_lun():
    report, handoff, _ = lun.analyze(SOURCE, [row(kind="VirtualMachine")])
    assert report["status"] == "no_candidate_kinds_observed"
    assert report["recommendation"] == "INSUFFICIENT EVIDENCE" and handoff is None


def test_exact_values_without_semantic_bindings_do_not_prove_identity():
    report, handoff, evidence = lun.analyze(SOURCE, [row()])
    assert report["status"] == "semantic_bindings_required" and handoff is None
    assert evidence["candidates"][0]["resourceKey"] == row()["resource"]["resourceKey"]


@pytest.mark.parametrize("role,field,method", [("uuid", "uuid", "uuid_exact"), ("canonical_name", "canonical", "canonical_name_exact")])
def test_exact_scoped_match_and_exact_full_key_handoff(role, field, method):
    policy = copy.deepcopy(BINDINGS)
    policy.pop("uuid")
    policy[role] = {"source": "identifier" if role == "uuid" else "property", "name": field}
    item = row()
    item["resource"]["resourceKey"]["resourceIdentifiers"].append(
        {"identifierType": {"name": "optional", "isPartOfUniqueness": False}, "value": ""})
    report, handoff, _ = lun.analyze(SOURCE, [item], policy)
    assert report["recommendation"] == "REUSE"
    assert report["candidates"][0]["match_methods"] == [method]
    assert handoff["resourceKey"] == item["resource"]["resourceKey"]
    handoff["resourceKey"]["name"] = "changed"
    assert item["resource"]["resourceKey"]["name"] == "secret-display"


@pytest.mark.parametrize("items,status", [
    ([row(uuid="different")], "no_unique_match"),
    ([row(), row(rid="second-secret")], "ambiguous_matches"),
    ([row(vc="another-vc")], "no_unique_match"),
    ([row(), row(rid="second-secret", kind="OtherStorage")], "incomplete_candidate_evidence"),
])
def test_absence_ambiguity_scope_and_competing_kind(items, status):
    report, handoff, _ = lun.analyze(SOURCE, items, BINDINGS)
    assert report["status"] == status and handoff is None
    assert report["recommendation"] == "INSUFFICIENT EVIDENCE"


def test_same_uuid_on_other_vcenter_does_not_create_ambiguity():
    report, _, _ = lun.analyze(SOURCE, [row(), row(rid="other", vc="other-vc")], BINDINGS)
    assert report["status"] == "unique_match"
    assert report["candidates"][1]["status"] == "scope_conflict"


def test_uuid_and_canonical_conflict_fails_closed():
    policy = copy.deepcopy(BINDINGS)
    policy["canonical_name"] = {"source": "property", "name": "canonical"}
    item = row()
    item["properties"]["canonical"] = "different"
    report, private, _ = lun.analyze(SOURCE, [item], policy)
    assert report["candidates"][0]["status"] == "identity_conflict" and private is None


@pytest.mark.parametrize("mutation", ["null", "omitted", "flag", "duplicate", "empty_unique", "no_ids", "missing_scope"])
def test_incomplete_and_ambiguous_keys(mutation):
    item = row()
    ids = item["resource"]["resourceKey"]["resourceIdentifiers"]
    if mutation == "null": ids[0]["value"] = None
    if mutation == "omitted": del ids[0]["value"]
    if mutation == "flag": ids[0]["identifierType"]["isPartOfUniqueness"] = "true"
    if mutation == "duplicate": ids.append({"identifierType": {"name": "UUID", "isPartOfUniqueness": False}, "value": "x"})
    if mutation == "empty_unique": ids[0]["value"] = ""
    if mutation == "no_ids": ids.clear()
    if mutation == "missing_scope": ids.pop()
    report, private, _ = lun.analyze(SOURCE, [item], BINDINGS)
    assert report["status"] == "incomplete_candidate_evidence" and private is None


def test_report_redacts_all_raw_values_names_and_identifiers():
    report, private, evidence = lun.analyze(SOURCE, [row()], BINDINGS)
    rendered = json.dumps(report)
    for secret in [*SOURCE.values(), "secret-resource", "secret-display"]:
        assert secret not in rendered
    assert private and evidence


@pytest.mark.parametrize("payload", [{}, {"resourceId": "wrong", "property": []},
    {"resourceId": "id", "property": [{"name": "x", "value": "a"}, {"name": "x", "value": "b"}]},
    {"resourceId": "id", "property": [{"name": "x", "value": {}}]}])
def test_incomplete_properties_not_empty_inventory(payload):
    with pytest.raises(lun.LunDiscoveryError, match="INCOMPLETE_PROPERTIES"):
        lun.properties(payload, "id")


class Client:
    def __init__(self): self.calls = []
    def _request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        assert method == "GET"
        data = ({"resourceList": [row()["resource"]], "pageInfo": {"totalCount": 1}}
            if path == "/api/resources" else {"resourceId": "secret-resource", "property": []}
            if path.endswith("/properties") else row()["resource"])
        return SimpleNamespace(status_code=200, json=lambda: data)


def test_complete_paginated_get_census_and_candidate_detail():
    client = Client()
    assert len(lun.collect(client, BINDINGS)) == 1
    assert [p for _, p, _ in client.calls] == ["/api/resources", "/api/resources/secret-resource", "/api/resources/secret-resource/properties"]


@pytest.mark.parametrize("body", [{"resourceList": [], "pageInfo": {"totalCount": 1}},
    {"resourceList": [], "pageInfo": {}}, {"resourceList": [row()["resource"]] * 2, "pageInfo": {"totalCount": 2}}])
def test_incomplete_census_fails_closed(body):
    class Broken(Client):
        def _request(self, method, path, **kwargs):
            return SimpleNamespace(status_code=200, json=lambda: body) if path == "/api/resources" else super()._request(method, path, **kwargs)
    with pytest.raises(lun.LunDiscoveryError, match="INCOMPLETE_INVENTORY"):
        lun.collect(Broken(), BINDINGS)


def test_cli_plan_and_double_guard(capsys):
    assert probe.main(["--mode", "lun-discovery"]) == 0
    with pytest.raises(SystemExit): probe.main(["--execute", "--mode", "lun-discovery"])


def test_cli_failure_does_not_print_exception_or_library_output(monkeypatch, capsys):
    def fail(*args):
        print("secret-library-output")
        raise RuntimeError("secret-exception")
    monkeypatch.setattr(probe, "_lun_discovery_module", lambda: SimpleNamespace(
        validate_bindings=lambda v: v, run=fail, LunDiscoveryError=lun.LunDiscoveryError))
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "lun-discovery"]) == 2
    output = capsys.readouterr()
    assert "secret" not in output.out + output.err
    assert "source_or_local_output_unavailable" in output.out


def test_secure_creation_no_overwrite_and_restricted_path(monkeypatch, tmp_path):
    scratch = tmp_path / "tmp/rdm-lab-probes"
    scratch.mkdir(parents=True, mode=0o700)
    monkeypatch.setattr(probe, "__file__", str(tmp_path / "scripts/rdm_lab_probe.py"))
    monkeypatch.setattr(probe.subprocess, "run", lambda args, **kw: SimpleNamespace(returncode=0 if args[1] == "check-ignore" else 1))
    target = scratch / "private.json"
    probe._write_report(probe._lun_local_path(target), {"synthetic": "private"})
    assert target.stat().st_mode & 0o777 == 0o600
    with pytest.raises(ValueError): probe._lun_local_path(target)
    with pytest.raises(ValueError): probe._lun_local_path(tmp_path / "outside.json")
    link = scratch / "link.json"
    link.symlink_to(target)
    with pytest.raises(ValueError): probe._lun_local_path(link)
    scratch.chmod(0o755)
    with pytest.raises(ValueError): probe._lun_local_path(scratch / "new.json")


@pytest.mark.parametrize("scenario", ["unique", "missing", "duplicate", "changed"])
def test_soap_current_host_identity_and_stable_snapshot(monkeypatch, scenario):
    class Backing:
        lunUuid = "secret-lun"
        deviceName = "secret-device"
    class Disk:
        RawDiskMappingVer1BackingInfo = Backing
        backing = Backing()
        key = 2001
    host = SimpleNamespace(_moId="host-secret")
    content = SimpleNamespace(about=SimpleNamespace(instanceUuid="secret-vc"), propertyCollector=object())
    connection = SimpleNamespace(_stub=object(), RetrieveContent=lambda: content)
    disconnected = []
    vim = SimpleNamespace(VirtualMachine=lambda *args: object(), HostSystem=object(),
        fault=SimpleNamespace(InvalidLogin=type("InvalidLogin", (Exception,), {}), NotAuthenticated=type("NotAuthenticated", (Exception,), {})),
        vm=SimpleNamespace(device=SimpleNamespace(VirtualDisk=Disk)))
    monkeypatch.setitem(sys.modules, "pyVmomi", SimpleNamespace(vim=vim))
    monkeypatch.setitem(sys.modules, "pyVim", SimpleNamespace())
    monkeypatch.setitem(sys.modules, "pyVim.connect", SimpleNamespace(SmartConnect=lambda **kw: connection,
        Disconnect=lambda conn: disconnected.append(conn)))
    for key in ("HOST", "USER", "PASSWORD"): monkeypatch.setenv("RDM_PROBE_VCENTER_" + key, "synthetic")
    calls = []
    def collect(pc, objects, kind, paths):
        if "config.storageDevice.scsiLun" in paths:
            count = {"missing": 0, "duplicate": 2}.get(scenario, 1)
            return {"host-secret": {paths[0]: [SimpleNamespace(uuid="secret-lun", canonicalName="naa.secret")] * count}}
        calls.append(True)
        return {"vm-71": {"config.instanceUuid": "vm-secret", "config.changeVersion":
            "changed" if scenario == "changed" and len(calls) == 3 else "same",
            "runtime.host": host, "config.hardware.device": [Disk()]}}
    monkeypatch.setattr(probe, "_collect_properties", collect)
    if scenario == "unique":
        assert probe._capture_soap_fixture(include_lun=True)["canonical_name"] == "naa.secret"
    else:
        with pytest.raises(probe.FixtureExportError): probe._capture_soap_fixture(include_lun=True)
    assert disconnected == [connection]


def test_output_failure_removes_already_written_private_evidence(monkeypatch, tmp_path, capsys):
    private = tmp_path / "private.json"
    output = tmp_path / "report.json"
    monkeypatch.setattr(probe, "_lun_local_path", lambda path, **kw: path)
    monkeypatch.setattr(probe, "_lun_discovery_module", lambda: SimpleNamespace(
        validate_bindings=lambda v: v, LunDiscoveryError=lun.LunDiscoveryError,
        run=lambda *args: ({"status": "synthetic"}, None, {"secret": "private-evidence"})))
    original = probe._write_report
    def write(path, payload):
        if path == output: raise OSError("secret-output-error")
        original(path, payload)
    monkeypatch.setattr(probe, "_write_report", write)
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "lun-discovery",
        "--output", str(output), "--lun-evidence-output", str(private)]) == 2
    assert not private.exists() and not output.exists()
    assert "secret" not in capsys.readouterr().out


def test_cli_allowlisted_reason(monkeypatch, capsys):
    def fail(*args): raise lun.LunDiscoveryError("INCOMPLETE_PROPERTIES")
    monkeypatch.setattr(probe, "_lun_discovery_module", lambda: SimpleNamespace(
        validate_bindings=lambda v: v, run=fail, LunDiscoveryError=lun.LunDiscoveryError))
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "lun-discovery"]) == 2
    assert json.loads(capsys.readouterr().out)["reason"] == "INCOMPLETE_PROPERTIES"


@pytest.mark.parametrize("success", [False, True])
def test_run_releases_token_and_requires_development_profile(monkeypatch, success):
    import vcfcf_common.client
    client = Client()
    monkeypatch.setattr(vcfcf_common.client.VCFOpsClient, "from_env", lambda *a, **kw: client)
    released = []
    def capture(**kwargs):
        assert kwargs == {"include_lun": True}
        if not success: raise RuntimeError("secret")
        return SOURCE
    if success:
        assert lun.run("devel", capture, lambda *args: released.append(args))[0]["candidate_count"] == 1
    else:
        with pytest.raises(RuntimeError): lun.run("devel", capture, lambda *args: released.append(args))
    assert released[0][0] is client
    with pytest.raises(lun.LunDiscoveryError, match="INVALID_PROFILE"):
        lun.run("production", capture, lambda *args: None)


@pytest.mark.parametrize("change", ["unknown", "shared_role", "no_storage", "wrong_granularity"])
def test_invalid_semantic_bindings_rejected(change):
    policy = copy.deepcopy(BINDINGS)
    if change == "unknown": policy["guessed"] = True
    if change == "shared_role": policy["uuid"] = policy["vcenter_instance_uuid"]
    if change == "no_storage": policy.pop("uuid")
    if change == "wrong_granularity": policy["granularity"] = "datastore"
    with pytest.raises(lun.LunDiscoveryError, match="INVALID_BINDINGS"):
        lun.validate_bindings(policy)


def test_missing_property_scope_and_incomplete_competing_key_block_reuse():
    policy = copy.deepcopy(BINDINGS)
    policy["vcenter_instance_uuid"] = {"source": "property", "name": "vc"}
    item = row()
    item["properties"]["vc"] = None
    report, private, _ = lun.analyze(SOURCE, [item], policy)
    assert private is None and report["candidates"][0]["missing_roles"] == ["vcenter_instance_uuid"]
    competitor = row(rid="other", kind="OtherStorage")
    competitor["resource"]["resourceKey"].pop("resourceIdentifiers")
    assert lun.analyze(SOURCE, [row(), competitor], BINDINGS)[1] is None
