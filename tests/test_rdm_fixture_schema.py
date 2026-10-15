"""API-vs-fixture contract differences; all data below is synthetic."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

SPEC = importlib.util.spec_from_file_location("rdm_schema_probe", Path(__file__).parents[1] / "scripts/rdm_lab_probe.py")
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)
VC = "11111111-1111-4111-8111-111111111111"
VM = "22222222-2222-4222-8222-222222222222"
SECRET = "synthetic-secret-inventory-value-and-name"


def api_resource():
    # Suite API permits extra nonidentity metadata, plus optional values/flags.
    # This valid fixture case supplies all actual values and explicit flags.
    ids = [
        ("VMEntityObjectID", "vm-71", True), ("VMEntityVCID", VC, True),
        ("VMEntityName", " synthetic VM ", False),
        ("synthetic-extra-identity", "extra-value", True),
        ("synthetic-optional-one", "one", False),
        ("synthetic-optional-two", "two", False),
    ]
    return {"identifier": "synthetic-ops-id", "resourceKey": {"adapterKindKey": "VMWARE",
        "resourceKindKey": "VirtualMachine", "name": "synthetic VM", "extension": {}, "links": [],
        "resourceIdentifiers": [{"identifierType": {"name": name, "isPartOfUniqueness": unique,
            "dataType": "STRING", "links": [], "extension": {}}, "value": value, "links": []}
            for name, value, unique in ids]}}


def mapping():
    return {"vm_moid": "vm-71", "vcenter_instance_uuid": VC,
            "vm_instance_uuid": VM, "virtual_disk_key": "2000"}


def test_documented_api_contract_is_less_restrictive_than_fixture():
    schema = json.loads((Path(__file__).parents[1] / "reference/docs/operations-api.json").read_text())["components"]["schemas"]
    assert "value" not in schema["resource-identifier"]["required"]
    assert "isPartOfUniqueness" not in schema["resource-identifier-type"]["required"]
    assert "By default" in schema["resource-identifier-type"]["properties"]["isPartOfUniqueness"]["description"]


def test_full_projection_preserves_six_identifier_entries_exactly():
    original = api_resource()
    fixture = probe._fixture_from_resources([original], mapping())
    key = fixture["foreign_vm"]
    assert set(key) == {"adapterKindKey", "resourceKindKey", "name", "resourceIdentifiers"}
    assert len(key["resourceIdentifiers"]) == 6
    for actual, raw in zip(key["resourceIdentifiers"], original["resourceKey"]["resourceIdentifiers"]):
        assert actual == {"identifierType": {k: raw["identifierType"][k] for k in ("name", "isPartOfUniqueness")},
                          "value": raw["value"]}
    assert fixture["mapping"] == {k: v for k, v in mapping().items() if k != "vm_moid"}


@pytest.mark.parametrize("variant,code", [("absent", "IDENTIFIER_VALUE_MISSING"),
    (None, "IDENTIFIER_VALUE_NULL"), (12, "IDENTIFIER_VALUE_NOT_STRING")])
def test_nonunique_empty_or_missing_identifier_is_rejected_not_dropped(variant, code):
    row = api_resource()
    for item in row["resourceKey"]["resourceIdentifiers"][-2:]:
        assert item["identifierType"]["isPartOfUniqueness"] is False
        if variant == "absent": del item["value"]
        else: item["value"] = variant
    before = deepcopy(row)
    with pytest.raises(probe.FixtureExportError) as caught:
        probe._fixture_from_resources([row], mapping())
    assert (caught.value.stage, caught.value.code, caught.value.field) == (
        "FIXTURE_SCHEMA_VALIDATION", code, "resource.resourceKey.resourceIdentifiers[].value")
    assert row == before  # No omission, coercion, default or normalization.


def test_two_nonunique_empty_strings_are_preserved_in_original_array_order():
    row = api_resource()
    for item in row["resourceKey"]["resourceIdentifiers"][-2:]: item["value"] = ""
    before = deepcopy(row)
    fixture = probe._fixture_from_resources([row], mapping())
    assert len(fixture["foreign_vm"]["resourceIdentifiers"]) == 6
    for projected, raw in zip(fixture["foreign_vm"]["resourceIdentifiers"], row["resourceKey"]["resourceIdentifiers"]):
        assert projected["value"] == raw["value"]
        assert projected["identifierType"]["name"] == raw["identifierType"]["name"]
        assert projected["identifierType"]["isPartOfUniqueness"] is raw["identifierType"]["isPartOfUniqueness"]
    assert row == before


@pytest.mark.parametrize("variant,code", [("absent", "IDENTIFIER_UNIQUENESS_MISSING"),
    (None, "IDENTIFIER_UNIQUENESS_NOT_BOOLEAN"), ("true", "IDENTIFIER_UNIQUENESS_NOT_BOOLEAN"),
    (1, "IDENTIFIER_UNIQUENESS_NOT_BOOLEAN")])
def test_uniqueness_flags_must_be_explicit_booleans(variant, code):
    row = api_resource()
    kind = row["resourceKey"]["resourceIdentifiers"][0]["identifierType"]
    if variant == "absent": del kind["isPartOfUniqueness"]
    else: kind["isPartOfUniqueness"] = variant
    with pytest.raises(probe.FixtureExportError) as caught: probe._fixture_resource_key(row)
    assert caught.value.code == code
    assert caught.value.field == "resource.resourceKey.resourceIdentifiers[].identifierType.isPartOfUniqueness"


@pytest.mark.parametrize("change,code,field", [
    (lambda r: None, "RESOURCE_NOT_OBJECT", "resource"),
    (lambda r: {}, "RESOURCE_KEY_MISSING", "resource.resourceKey"),
    (lambda r: {"resourceKey": None}, "RESOURCE_KEY_NOT_OBJECT", "resource.resourceKey"),
    (lambda r: {"resourceKey": {**r["resourceKey"], "adapterKindKey": SECRET}}, "ADAPTER_KIND_INVALID", "resource.resourceKey.adapterKindKey"),
    (lambda r: {"resourceKey": {**r["resourceKey"], "resourceKindKey": SECRET}}, "RESOURCE_KIND_INVALID", "resource.resourceKey.resourceKindKey"),
    (lambda r: {"resourceKey": {k: v for k, v in r["resourceKey"].items() if k != "name"}}, "RESOURCE_NAME_MISSING", "resource.resourceKey.name"),
    (lambda r: {"resourceKey": {**r["resourceKey"], "name": None}}, "RESOURCE_NAME_INVALID", "resource.resourceKey.name"),
    (lambda r: {"resourceKey": {k: v for k, v in r["resourceKey"].items() if k != "resourceIdentifiers"}}, "IDENTIFIERS_MISSING", "resource.resourceKey.resourceIdentifiers"),
    (lambda r: {"resourceKey": {**r["resourceKey"], "resourceIdentifiers": None}}, "IDENTIFIERS_NOT_ARRAY", "resource.resourceKey.resourceIdentifiers"),
    (lambda r: {"resourceKey": {**r["resourceKey"], "resourceIdentifiers": []}}, "IDENTIFIERS_EMPTY", "resource.resourceKey.resourceIdentifiers"),
])
def test_resource_shape_rule_diagnostics(change, code, field):
    with pytest.raises(probe.FixtureExportError) as caught: probe._fixture_resource_key(change(api_resource()))
    assert (caught.value.code, caught.value.field) == (code, field)
    assert SECRET not in str(caught.value)


@pytest.mark.parametrize("replacement,code", [(None, "IDENTIFIER_NOT_OBJECT"),
    ({}, "IDENTIFIER_TYPE_MISSING"), ({"identifierType": None}, "IDENTIFIER_TYPE_NOT_OBJECT"),
    ({"identifierType": {}}, "IDENTIFIER_NAME_MISSING"),
    ({"identifierType": {"name": ""}}, "IDENTIFIER_NAME_INVALID")])
def test_identifier_shape_diagnostics(replacement, code):
    row = api_resource()
    row["resourceKey"]["resourceIdentifiers"][0] = replacement
    with pytest.raises(probe.FixtureExportError) as caught: probe._fixture_resource_key(row)
    assert caught.value.code == code


def test_duplicate_identifier_name_is_not_echoed():
    row = api_resource()
    ids = row["resourceKey"]["resourceIdentifiers"]
    ids[0]["identifierType"]["name"] = SECRET
    ids[1]["identifierType"]["name"] = SECRET
    with pytest.raises(probe.FixtureExportError) as caught: probe._fixture_resource_key(row)
    assert caught.value.code == "IDENTIFIER_NAME_DUPLICATE"
    assert SECRET not in str(caught.value) + str(caught.value.field)


@pytest.mark.parametrize("lun,key,code,field", [(None, 2000, "RDM_LUN_IDENTITY_INVALID", "vcenter.rdm.backing.lunUuid"),
    ("synthetic-lun", True, "RDM_DISK_KEY_INVALID", "mapping.virtual_disk_key"),
    ("synthetic-lun", "2000", "RDM_DISK_KEY_INVALID", "mapping.virtual_disk_key")])
def test_rdm_identity_rule_diagnostics(lun, key, code, field):
    disk = SimpleNamespace(backing=SimpleNamespace(lunUuid=lun), key=key)
    with pytest.raises(probe.FixtureExportError) as caught: probe._single_rdm_fixture_mapping(VC, VM, [disk])
    assert (caught.value.code, caught.value.field) == (code, field)


def test_json_decoding_has_safe_field_and_retains_private_cause():
    error = ValueError(SECRET)
    def invalid(): raise error
    client = SimpleNamespace(_request=lambda *args, **kwargs: SimpleNamespace(status_code=200, json=invalid))
    with pytest.raises(probe.FixtureExportError) as caught: probe._capture_fixture_resources(client)
    assert (caught.value.code, caught.value.field) == ("OPS_RESPONSE_JSON_INVALID", "operations.response")
    assert caught.value.__cause__ is error


@pytest.mark.parametrize("field", sorted(probe.FixtureExportError.FIELDS))
def test_cli_only_renders_allowlisted_structural_fields(field, monkeypatch, capsys):
    def fail(profile):
        raise probe.FixtureExportError(SECRET, stage="FIXTURE_SCHEMA_VALIDATION",
                                      code="IDENTIFIER_VALUE_EMPTY", field=field)
    monkeypatch.setattr(probe, "_export_fixture", fail)
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "fixture-export"]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == f"Fixture export failed: stage=FIXTURE_SCHEMA_VALIDATION; code=IDENTIFIER_VALUE_EMPTY; field={field}; no success claimed.\n"


def test_untrusted_field_cannot_leak_through_cli(monkeypatch, capsys):
    def fail(profile):
        error = probe.FixtureExportError(SECRET)
        error.field = SECRET
        raise error
    monkeypatch.setattr(probe, "_export_fixture", fail)
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "fixture-export"]) == 2
    assert "field=" not in capsys.readouterr().err


def test_java_accepts_nonunique_empty_but_rejects_missing_null_or_blank_values():
    if not os.environ.get("VCFCF_SDK_JAR"): pytest.skip("explicit local SDK path required")
    fixture = probe._fixture_from_resources([api_resource()], mapping())
    with probe._fixture_validator() as validate:
        validate(json.dumps(fixture).encode())
        accepted = deepcopy(fixture)
        accepted["foreign_vm"]["resourceIdentifiers"][-1]["value"] = ""
        validate(json.dumps(accepted).encode())
        for variant in ("missing", None, " "):
            invalid = deepcopy(fixture)
            item = invalid["foreign_vm"]["resourceIdentifiers"][-1]
            if variant == "missing": del item["value"]
            else: item["value"] = variant
            with pytest.raises(probe.FixtureExportError) as caught: validate(json.dumps(invalid).encode())
            assert caught.value.code == "PARSER_REJECTED"
        invalid = {**fixture, "foreign_vm": api_resource()["resourceKey"]}
        with pytest.raises(probe.FixtureExportError): validate(json.dumps(invalid).encode())
        for field in ("vcenter_instance_uuid", "vm_instance_uuid", "virtual_disk_key"):
            for variant in ("missing", None, ""):
                invalid = deepcopy(fixture)
                if variant == "missing": del invalid["mapping"][field]
                else: invalid["mapping"][field] = variant
                with pytest.raises(probe.FixtureExportError): validate(json.dumps(invalid).encode())


def test_python_and_actual_java_value_presence_contract_agree():
    if not os.environ.get("VCFCF_SDK_JAR"): pytest.skip("explicit local SDK path required")
    with probe._fixture_validator() as validate:
        for unique in (False, True):
            for presence in ("populated", "empty", "omitted", "null"):
                row = api_resource()
                item = row["resourceKey"]["resourceIdentifiers"][-1]
                item["identifierType"]["isPartOfUniqueness"] = unique
                if presence == "empty": item["value"] = ""
                elif presence == "omitted": del item["value"]
                elif presence == "null": item["value"] = None
                supported = presence == "populated" or (presence == "empty" and not unique)
                # Retain the original response's exact presence in the direct Java
                # fixture, even for rejected data. Never fill or drop identifiers.
                direct_key = {k: row["resourceKey"][k] for k in ("adapterKindKey", "resourceKindKey", "name")}
                direct_key["resourceIdentifiers"] = []
                for entry in row["resourceKey"]["resourceIdentifiers"]:
                    projected = {"identifierType": {k: entry["identifierType"][k] for k in ("name", "isPartOfUniqueness")}}
                    if "value" in entry: projected["value"] = entry["value"]
                    direct_key["resourceIdentifiers"].append(projected)
                direct = {"foreign_vm": direct_key, "mapping": {k: v for k, v in mapping().items() if k != "vm_moid"}}
                if supported:
                    exported = probe._fixture_from_resources([row], mapping())
                    assert exported == direct
                    validate(json.dumps(exported).encode())
                else:
                    with pytest.raises(probe.FixtureExportError): probe._fixture_from_resources([row], mapping())
                    with pytest.raises(probe.FixtureExportError): validate(json.dumps(direct).encode())


def test_actual_java_gate_rejects_empty_identity_evidence_and_sdk_name_aliases():
    if not os.environ.get("VCFCF_SDK_JAR"): pytest.skip("explicit local SDK path required")
    with probe._fixture_validator() as validate:
        for name in ("VMEntityObjectID", "VMEntityVCID", "VMEntityInstanceUUID"):
            row = api_resource()
            item = row["resourceKey"]["resourceIdentifiers"][-1]
            item["identifierType"]["name"] = name
            item["value"] = ""
            if name != "VMEntityInstanceUUID":
                row["resourceKey"]["resourceIdentifiers"] = [entry for entry in row["resourceKey"]["resourceIdentifiers"]
                    if entry is item or entry["identifierType"]["name"] != name]
            key = probe._fixture_resource_key(row)
            direct = {"foreign_vm": key, "mapping": {k: v for k, v in mapping().items() if k != "vm_moid"}}
            with pytest.raises(probe.FixtureExportError): validate(json.dumps(direct).encode())
        row = api_resource()
        row["resourceKey"]["resourceIdentifiers"][-1]["identifierType"]["name"] = "vmentityobjectid"
        direct = probe._fixture_from_resources([row], mapping())
        with pytest.raises(probe.FixtureExportError): validate(json.dumps(direct).encode())
