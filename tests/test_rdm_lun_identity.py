"""Synthetic-only E3.4 descriptor and opt-in safety contracts."""
import copy
import importlib.util
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parents[1] / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


identity = load("rdm_lun_identity")
probe = load("rdm_lab_probe")
NAA = "6123456789abcdef0123456789abcdef"
REFERENCE = {"naa": "0x" + NAA}


def name(token=NAA):
    return {"namespace": "NAA", "namespaceId": 99, "data": [1, 3, 0, len(bytes.fromhex(token)), *bytes.fromhex(token)]}


def source():
    return {"lun_uuid": "opaque-secret-uuid", "host_moid": "host-1", "lun_observations": [
        {"host_moid": "host-1", "join_method": "exact_backing_uuid", "lun": {
            "uuid": "opaque-secret-uuid", "canonicalName": "naa." + NAA,
            "durableName": name(), "alternateName": [], "descriptor": [], "vendor": "secret-vendor",
            "displayName": "secret-display", "capacity": {"block": 128, "blockSize": 512}}}]}


def test_full_header_payload_match_and_redaction():
    raw = source()
    report, private = identity.analyze(raw, REFERENCE)
    assert report["qualification"] == "CONDITIONALLY QUALIFIED"
    assert report["cross_host_equivalence"] == "not_established"
    detail = report["hosts"][0]["descriptors"][0]
    assert detail["association"] == 0 and detail["designator_type"] == 3
    assert detail["format"] == "page83_header_and_payload"
    for secret in (NAA, "opaque-secret-uuid", "host-1", "secret-vendor", "secret-display"):
        assert secret not in json.dumps(report)
    assert private == raw


@pytest.mark.parametrize("token", [NAA, "5123456789abcdef"])
def test_complete_hex_prefix_and_case_only(token):
    assert identity.naa("NAA." + token.upper(), "naa.") == token
    assert identity.reference({"naa": "0X" + token.upper()}) == token
    for prefix in ("", "uuid.", "vml.", "naa."):
        with pytest.raises(identity.IdentityError):
            identity.reference({"naa": prefix + token})


def test_signed_byte_conversion_preserves_order():
    original = name()
    signed = copy.deepcopy(original)
    signed["data"] = [b - 256 if b > 127 else b for b in signed["data"]]
    assert identity.descriptor(original) == identity.descriptor(signed)
    assert identity.descriptor(original)[1] == NAA


def sdk_source():
    vmomi = pytest.importorskip("pyVmomi.VmomiSupport")
    raw = source()
    lun = raw["lun_observations"][0]["lun"]
    lun["durableName"]["namespaceId"] = vmomi.byte(3)
    lun["durableName"]["data"] = [vmomi.byte(b - 256 if b > 127 else b)
                                  for b in lun["durableName"]["data"]]
    lun["capacity"]["block"] = vmomi.long(128)
    return raw


def test_sdk_integer_subclasses_and_json_integers_have_identical_results():
    raw = sdk_source()
    assert type(raw["lun_observations"][0]["lun"]["durableName"]["namespaceId"]) is not int
    report, _ = identity.analyze(raw, REFERENCE)
    decoded_report, _ = identity.analyze(json.loads(json.dumps(raw)), REFERENCE)
    assert report == decoded_report
    assert report["qualification"] == "CONDITIONALLY QUALIFIED"
    assert report["hosts"][0]["distinct_lu_designators"] == 1
    assert report["hosts"][0]["capacity_dimensions_valid"]


@pytest.mark.parametrize("field", ["namespaceId", "data", "block", "blockSize"])
@pytest.mark.parametrize("value", [True, False, "1", 1.0, None])
def test_integer_compatibility_does_not_coerce_invalid_types(field, value):
    raw = sdk_source()
    lun = raw["lun_observations"][0]["lun"]
    if field == "data": lun["durableName"]["data"][4] = value
    elif field == "namespaceId": lun["durableName"][field] = value
    else: lun["capacity"][field] = value
    report, _ = identity.analyze(raw, REFERENCE)
    assert report["qualification"] == "BLOCKED"


@pytest.mark.parametrize("field", ["namespaceId", "data"])
@pytest.mark.parametrize("value", [-129, 256])
def test_sdk_byte_subclasses_still_obey_existing_range(field, value):
    vmomi = pytest.importorskip("pyVmomi.VmomiSupport")
    raw = sdk_source()
    item = raw["lun_observations"][0]["lun"]["durableName"]
    if field == "namespaceId": item[field] = vmomi.byte(value)
    else: item["data"][4] = vmomi.byte(value)
    assert identity.analyze(raw, REFERENCE)[0]["qualification"] == "BLOCKED"


@pytest.mark.parametrize("value", [0, -1, 2**63])
@pytest.mark.parametrize("field", ["block", "blockSize"])
def test_sdk_capacity_subclasses_still_reject_nonpositive_and_overflow(field, value):
    vmomi = pytest.importorskip("pyVmomi.VmomiSupport")
    raw = sdk_source()
    raw["lun_observations"][0]["lun"]["capacity"][field] = vmomi.long(value)
    assert identity.analyze(raw, REFERENCE)[0]["qualification"] == "BLOCKED"


@pytest.mark.parametrize("change", ["namespace", "association", "encoding", "designator", "length", "ambiguous", "equivalence"])
def test_sdk_integer_acceptance_preserves_identity_rejections(change):
    vmomi = pytest.importorskip("pyVmomi.VmomiSupport")
    raw = sdk_source()
    lun = raw["lun_observations"][0]["lun"]
    item = lun["durableName"]
    if change == "namespace": item["namespace"] = "EUI"
    if change == "association": item["data"][1] = vmomi.byte(0x13)
    if change == "encoding": item["data"][0] = vmomi.byte(2)
    if change == "designator": item["data"][1] = vmomi.byte(2)
    if change == "length": item["data"][3] = vmomi.byte(15)
    if change == "ambiguous":
        other = copy.deepcopy(item)
        other["data"][-1] = vmomi.byte(int(other["data"][-1]) ^ 1)
        lun["alternateName"].append(other)
    if change == "equivalence": lun["canonicalName"] = "naa." + NAA[:-1] + "0"
    assert identity.analyze(raw, REFERENCE)[0]["qualification"] == "BLOCKED"


def test_actual_soap_deserializer_to_capture_to_validator_without_json_roundtrip():
    vmomi = pytest.importorskip("pyVmomi")
    from pyVmomi import SoapAdapter
    payload = [1, 3, 0, 16, *bytes.fromhex(NAA)]
    byte_xml = "".join("<data>" + str(b - 256 if b > 127 else b) + "</data>" for b in payload)
    xml = ('<obj xmlns="urn:vim25" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xsi:type="HostScsiDisk"><uuid>opaque-secret-uuid</uuid><canonicalName>naa.' + NAA +
           '</canonicalName><lunType>disk</lunType><deviceType>scsi-disk</deviceType>'
           '<vendor>SyntheticVendor</vendor><model>SyntheticModel</model><durableName>'
           '<namespace>NAA</namespace><namespaceId>3</namespaceId>' + byte_xml +
           '</durableName><capacity><blockSize>512</blockSize><block>128</block></capacity></obj>')
    disk = SoapAdapter.Deserialize(xml, resultType=vmomi.vim.host.ScsiDisk)
    raw = source()
    raw["lun_observations"][0]["lun"] = probe._raw_lun_identity(disk)
    assert type(disk.durableName.namespaceId) is vmomi.VmomiSupport.byte
    assert type(disk.durableName.data[0]) is vmomi.VmomiSupport.byte
    assert type(disk.capacity.block) is vmomi.VmomiSupport.long
    report, _ = identity.analyze(raw, REFERENCE)
    assert report["qualification"] == "CONDITIONALLY QUALIFIED"
    assert report["hosts"][0]["descriptive_values_valid"]


@pytest.mark.parametrize("change,status", [
    ("port", "not_logical_unit"), ("target", "not_logical_unit"),
    ("length", "invalid_declared_length"), ("reserved", "unsupported_header_bits"),
    ("piv", "unsupported_header_bits"), ("protocol", "unsupported_header_bits"),
    ("eui", "unsupported_designator"), ("ascii", "unsupported_designator"),
    ("byte_type", "invalid_bytes"), ("byte_range", "invalid_bytes"),
    ("payload_only", "unsupported_header_bits"), ("short", "missing_descriptor_header"),
    ("naa3", "unsupported_naa_format"), ("naa2", "unsupported_naa_format"),
])
def test_descriptor_rejection(change, status):
    item = name()
    data = item["data"]
    if change == "port": data[1] |= 0x10
    if change == "target": data[1] |= 0x20
    if change == "length": data[3] -= 1
    if change == "reserved": data[2] = 1
    if change == "piv": data[1] |= 0x80
    if change == "protocol": data[0] |= 0x10
    if change == "eui": data[1] = 2
    if change == "ascii": data[0] = 2
    if change == "byte_type": data[4] = True
    if change == "byte_range": data[4] = 256
    if change == "payload_only": item["data"] = data[4:]
    if change == "short": item["data"] = [1, 3]
    if change in {"naa2", "naa3"}: data[4] = 0x20 if change == "naa2" else 0x30
    detail, token = identity.descriptor(item)
    assert detail["status"] == status and token is None


@pytest.mark.parametrize("namespace", ["EUI", "T10", "vendor-secret", "page80", None])
def test_namespace_does_not_prove_lu_association(namespace):
    item = name()
    item["namespace"] = namespace
    detail, token = identity.descriptor(item)
    assert token is None
    assert "vendor-secret" not in json.dumps(detail)


@pytest.mark.parametrize("mutation", ["reference", "canonical", "different_descriptor", "missing_descriptor",
    "invalid_alternate", "port", "missing_lun", "missing_current", "bad_method"])
def test_conflict_or_missing_identity_blocks(mutation):
    raw = source()
    ref = copy.deepcopy(REFERENCE)
    lun = raw["lun_observations"][0]["lun"]
    if mutation == "reference": ref["naa"] = "0x" + NAA[:-1] + "0"
    if mutation == "canonical": lun["canonicalName"] = "naa." + NAA[:-1] + "0"
    if mutation == "different_descriptor": lun["alternateName"] = [name(NAA[:-1] + "0")]
    if mutation == "missing_descriptor": lun["durableName"] = None
    if mutation == "invalid_alternate": lun["alternateName"] = [{"namespace": "naa", "data": []}]
    if mutation == "port": lun["durableName"]["data"][1] = 0x13
    if mutation == "missing_lun": raw["lun_observations"][0]["lun"] = None
    if mutation == "missing_current": raw["host_moid"] = "host-2"
    if mutation == "bad_method": raw["lun_observations"][0]["join_method"] = "secret-value"
    report, _ = identity.analyze(raw, ref)
    assert report["qualification"] == "BLOCKED"
    assert "secret-value" not in json.dumps(report)


def test_cross_host_canonical_join_not_uuid_equivalence_assumption():
    raw = source()
    other = copy.deepcopy(raw["lun_observations"][0])
    other.update(host_moid="host-2", join_method="exact_canonical_candidate")
    other["lun"]["uuid"] = "different-opaque-uuid"
    raw["lun_observations"].append(other)
    report, _ = identity.analyze(raw, REFERENCE)
    assert report["qualification"] == "CONDITIONALLY QUALIFIED"
    assert report["cross_host_equivalence"] == "observed"
    assert not report["hosts"][1]["uuid_equals_backing"]
    other["lun"]["canonicalName"] = "naa." + NAA[:-1] + "0"
    assert identity.analyze(raw, REFERENCE)[0]["qualification"] == "BLOCKED"


def test_duplicate_empty_hosts_or_missing_backing_rejected():
    for mutation in ("empty", "duplicate", "backing"):
        raw = source()
        if mutation == "empty": raw["lun_observations"] = []
        if mutation == "duplicate": raw["lun_observations"] *= 2
        if mutation == "backing": raw["lun_uuid"] = ""
        with pytest.raises(identity.IdentityError): identity.analyze(raw, REFERENCE)


@pytest.mark.parametrize("field", ["capacity", "vendor", "model", "lunType", "deviceType"])
def test_conflicting_host_descriptions_quarantine(field):
    raw = source()
    original = raw["lun_observations"][0]
    original["lun"].setdefault(field, "first")
    other = copy.deepcopy(original)
    other["host_moid"] = "host-2"
    other["lun"][field] = {"block": 256, "blockSize": 512} if field == "capacity" else "different"
    raw["lun_observations"].append(other)
    report, _ = identity.analyze(raw, REFERENCE)
    assert report["qualification"] == "BLOCKED"
    assert field in report["conflicting_descriptive_fields"]


@pytest.mark.parametrize("capacity", [{"block": 0, "blockSize": 512}, {"block": True, "blockSize": 512},
    {"block": 2**63, "blockSize": 512}, {"block": 1}, "raw-secret"])
def test_invalid_capacity_is_not_success(capacity):
    raw = source()
    raw["lun_observations"][0]["lun"]["capacity"] = capacity
    report, _ = identity.analyze(raw, REFERENCE)
    assert report["qualification"] == "BLOCKED"
    assert "raw-secret" not in json.dumps(report)


@pytest.mark.parametrize("hosts", [["host-1", "host-1"], ["vm-71"], ["host-2"] * 16, ["host-2/secret"]])
def test_explicit_host_selection_guards(hosts):
    with pytest.raises(ValueError): probe._identity_host_selection(hosts, "host-1")


def test_current_host_always_included_without_sweep():
    assert probe._identity_host_selection(["host-2", "host-1"], "host-1") == ["host-1", "host-2"]


def test_raw_descriptor_capture_preserves_namespace_id_and_signed_bytes():
    obj = NS(uuid="opaque", canonicalName="naa.synthetic", durableName=NS(namespace="NAA", namespaceId=99, data=[-1, 1]),
             alternateName=None, descriptor=None, capacity=NS(block=128, blockSize=512))
    raw = probe._raw_lun_identity(obj)
    assert raw["durableName"] == {"namespace": "NAA", "namespaceId": 99, "data": [-1, 1]}
    assert raw["capacity"] == {"block": 128, "blockSize": 512}
    assert raw["alternateName"] == []


def test_cli_offline_and_double_guard(monkeypatch, capsys):
    monkeypatch.setattr(probe, "_capture_soap_fixture", lambda **kw: pytest.fail("must not connect"))
    assert probe.main(["--mode", "lun-identity"]) == 0
    with pytest.raises(SystemExit): probe.main(["--execute", "--mode", "lun-identity"])
    with pytest.raises(SystemExit): probe.main(["--execute", "--allow-read-only-lab", "--mode", "lun-identity"])
    with pytest.raises(SystemExit): probe.main(["--execute", "--allow-read-only-lab", "--mode", "lun-identity",
        "--profile", "prod", "--storage-reference-file", "not-read.json"])
    assert "OFFLINE PLAN" in capsys.readouterr().out


def test_cli_suppresses_exception_payload_and_partial_output_cleanup(monkeypatch, tmp_path, capsys):
    ref = tmp_path / "reference.json"
    ref.write_text(json.dumps(REFERENCE))
    private, report = tmp_path / "private.json", tmp_path / "report.json"
    monkeypatch.setattr(probe, "_lun_local_path", lambda p, **kw: p)
    monkeypatch.setattr(probe, "_capture_soap_fixture", lambda **kw: source())
    monkeypatch.setattr(probe, "_env_csv", lambda name: [])
    written = []
    def write(path, payload):
        if path == report:
            print("SECRET-INVENTORY")
            raise ValueError("SECRET-TOKEN")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(payload, stream)
        written.append(path)
    monkeypatch.setattr(probe, "_write_report", write)
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "lun-identity",
        "--storage-reference-file", str(ref), "--output", str(report), "--lun-evidence-output", str(private)]) == 2
    text = capsys.readouterr()
    assert "SECRET" not in text.out + text.err
    assert written == [private]
    assert not private.exists()


def test_non_lu_alternate_is_excluded_not_conflicting():
    raw = source()
    port = name()
    port["data"][1] = 0x13
    raw["lun_observations"][0]["lun"]["alternateName"] = [port]
    report, _ = identity.analyze(raw, REFERENCE)
    assert report["qualification"] == "CONDITIONALLY QUALIFIED"
    assert report["hosts"][0]["descriptors"][1]["status"] == "not_logical_unit"


@pytest.mark.parametrize("value", [None, True, "3", 256, -129])
def test_namespace_id_is_present_byte_not_designator_type(value):
    item = name()
    item["namespaceId"] = value
    assert identity.descriptor(item)[0]["status"] == "namespace_id_missing_or_invalid"
    assert identity.descriptor(item)[1] is None


def test_claimed_uuid_join_must_be_exact():
    raw = source()
    raw["lun_observations"][0]["lun"]["uuid"] = "different"
    with pytest.raises(identity.IdentityError): identity.analyze(raw, REFERENCE)


@pytest.mark.parametrize("scenario", ["valid", "uuid_difference", "case_difference", "canonical_conflict", "ambiguous", "missing", "changed", "unreadable", "no_backing_uuid", "no_vcenter"])
def test_soap_selected_hosts_exact_join_and_final_snapshot(monkeypatch, scenario):
    class Backing:
        lunUuid = "opaque-secret-uuid"
        deviceName = "secret-device"
    class Disk:
        RawDiskMappingVer1BackingInfo = Backing
        backing = Backing()
        key = 2001
    host = NS(_moId="host-1")
    content = NS(about=NS(instanceUuid="synthetic-vcenter"), propertyCollector=object())
    connection = NS(_stub=object(), RetrieveContent=lambda: content)
    disconnected = []
    vm = NS(_moId="vm-71")
    vim = NS(VirtualMachine=lambda *args: vm, HostSystem=lambda moid, stub: NS(_moId=moid),
        fault=NS(InvalidLogin=type("InvalidLogin", (Exception,), {}), NotAuthenticated=type("NotAuthenticated", (Exception,), {})),
        vm=NS(device=NS(VirtualDisk=Disk)))
    monkeypatch.setitem(sys.modules, "pyVmomi", NS(vim=vim))
    monkeypatch.setitem(sys.modules, "pyVim", NS())
    monkeypatch.setitem(sys.modules, "pyVim.connect", NS(SmartConnect=lambda **kw: connection,
        Disconnect=lambda conn: disconnected.append(conn)))
    for key in ("HOST", "USER", "PASSWORD"): monkeypatch.setenv("RDM_PROBE_VCENTER_" + key, "synthetic")
    if scenario == "no_backing_uuid": Disk.backing.lunUuid = None
    if scenario == "no_vcenter": content.about.instanceUuid = None
    calls = []
    hosts = []
    def collect(pc, objects, kind, paths):
        if "config.storageDevice.scsiLun" in paths:
            moid = objects[0]._moId
            hosts.append(moid)
            if scenario == "unreadable" and moid == "host-2":
                raise probe.PropertyCollectionError("private-error")
            count = {"missing": 0, "ambiguous": 2}.get(scenario, 1) if moid == "host-2" else 1
            raw = source()["lun_observations"][0]["lun"]
            if scenario in {"uuid_difference", "case_difference"} and moid == "host-2": raw["uuid"] = "other-opaque"
            if scenario == "case_difference" and moid == "host-2": raw["canonicalName"] = raw["canonicalName"].upper()
            luns = [NS(**{**raw, "durableName": NS(**raw["durableName"]), "capacity": NS(**raw["capacity"])})] * count
            if scenario == "canonical_conflict" and moid == "host-2":
                other = copy.copy(luns[0])
                other.uuid = "other-opaque"
                luns.append(other)
            return {moid: {paths[0]: luns}}
        calls.append(True)
        return {"vm-71": {"config.instanceUuid": "synthetic-vm", "config.changeVersion":
            "changed" if scenario == "changed" and len(calls) == 4 else "same",
            "runtime.host": host, "config.hardware.device": [Disk()]}}
    monkeypatch.setattr(probe, "_collect_properties", collect)
    if scenario in {"changed", "unreadable", "no_backing_uuid", "no_vcenter"}:
        with pytest.raises(probe.FixtureExportError):
            probe._capture_soap_fixture(include_identity=True, identity_hosts=["host-2"])
    else:
        raw = probe._capture_soap_fixture(include_identity=True, identity_hosts=["host-2"])
        result, _ = identity.analyze(raw, REFERENCE)
        assert result["qualification"] == ("BLOCKED" if scenario in {"missing", "ambiguous", "canonical_conflict"} else "CONDITIONALLY QUALIFIED")
        assert hosts == ["host-1", "host-2"]
    assert disconnected == [connection]


@pytest.mark.parametrize("duplicate", ["object", "property", "unexpected"])
def test_propertycollector_ambiguous_responses_rejected(monkeypatch, duplicate):
    spec = NS(ObjectSpec=lambda **kw: NS(**kw), PropertySpec=lambda **kw: NS(**kw),
              FilterSpec=lambda **kw: NS(**kw), RetrieveOptions=lambda **kw: NS(**kw))
    monkeypatch.setitem(sys.modules, "pyVmomi", NS(vmodl=NS(query=NS(PropertyCollector=spec))))
    prop = NS(name="x", val="private")
    obj = NS(obj=NS(_moId="host-1"), propSet=[prop], missingSet=[])
    if duplicate == "property": obj.propSet.append(prop)
    if duplicate == "unexpected": obj.obj._moId = "host-2"
    response = NS(objects=[obj, obj] if duplicate == "object" else [obj], token=None)
    pc = NS(RetrievePropertiesEx=lambda **kw: response)
    with pytest.raises(probe.PropertyCollectionError):
        probe._collect_properties(pc, [NS(_moId="host-1")], object, ["x"])


def test_cli_success_outputs_only_sanitized_report(monkeypatch, tmp_path, capsys):
    ref = tmp_path / "reference.json"
    ref.write_text(json.dumps(REFERENCE))
    monkeypatch.setattr(probe, "_lun_local_path", lambda p, **kw: p)
    monkeypatch.setattr(probe, "_capture_soap_fixture", lambda **kw: source())
    monkeypatch.setattr(probe, "_env_csv", lambda name: [])
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "lun-identity",
        "--storage-reference-file", str(ref)]) == 0
    output = capsys.readouterr().out
    assert NAA not in output and "opaque-secret-uuid" not in output
    assert json.loads(output)["qualification"] == "CONDITIONALLY QUALIFIED"


def test_actual_writer_exclusive_0600_and_serialization_cleanup(monkeypatch, tmp_path):
    monkeypatch.setattr(probe, "__file__", str(tmp_path / "scripts" / "rdm_lab_probe.py"))
    scratch = tmp_path / "tmp" / "rdm-lab-probes"
    target = scratch / "identity.json"
    with pytest.raises(TypeError):
        probe._write_report(target, {"nonserializable": object()})
    assert not target.exists()
    probe._write_report(target, {"synthetic": True})
    assert target.stat().st_mode & 0o777 == 0o600
    with pytest.raises(ValueError): probe._write_report(target, {"overwrite": True})
    assert json.loads(target.read_text()) == {"synthetic": True}
    link = scratch / "link.json"
    link.symlink_to(target)
    with pytest.raises(ValueError): probe._write_report(link, {"symlink": True})


def test_timestamp_is_safe_and_explicit():
    raw = source()
    raw["observed_at_epoch_ms"] = 12345
    assert identity.analyze(raw, REFERENCE)[0]["observed_at_epoch_ms"] == 12345
    raw["observed_at_epoch_ms"] = "secret-time"
    with pytest.raises(identity.IdentityError): identity.analyze(raw, REFERENCE)
