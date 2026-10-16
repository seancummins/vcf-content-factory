"""DEF-019: reverse real synthetic XML through public parsers, YAML and render.

Fixtures use public VMWARE kinds and explicitly synthetic member/filter keys.
They were generated once with the existing loader/renderer; source XML bytes,
not hand-created dataclasses, are the regression input on every run.
"""
from __future__ import annotations

from dataclasses import asdict
from copy import deepcopy
import importlib
import io
from zipfile import ZipFile
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest
import yaml

FIXTURES = Path(__file__).with_name("fixtures")
ROUTES = ["extractor", "reverse_local", "dataclass"]


def _source(name):
    return (FIXTURES / f"view_reverse_fidelity_{name}.xml").read_text(encoding="utf-8")


def _view_element(source):
    return ET.fromstring(source).find(".//ViewDef")


def _dataclass_doc(view):
    """Serialize the returned model using the existing YAML schema, no XML cache."""
    doc = {"id": view.id, "name": view.name, "description": view.description}
    if view.subjects:
        doc["subjects"] = [asdict(s) for s in view.subjects]
    else:
        doc["subject"] = {"adapter_kind": view.adapter_kind, "resource_kind": view.resource_kind}
    if view.subject_filter is not None:
        doc.setdefault("subject", {})["filter"] = [
            [{k: v for k, v in asdict(c).items() if v is not None} for c in group]
            for group in view.subject_filter
        ]
    doc["columns"] = []
    for column in view.columns:
        col = {k: v for k, v in asdict(column).items() if v is not None}
        if column.instanced_group and column.instanced_group.prefix is not None:
            col["instanced_group"].pop("show_instance_name")
            col["instanced_group"].pop("keep_instance_summary")
        if column.instanced_group or column.time_segment:
            col.pop("attribute", None)
        doc["columns"].append(col)
    if view.summary is not None:
        doc["summary"] = {"display_name": view.summary.display_name, "aggregation": view.summary.aggregation}
        if view.summary.column_indexes is not None:
            doc["summary"]["columns"] = view.summary.column_indexes
    if view.time_window is not None:
        doc["time_window"] = asdict(view.time_window)
    return doc


def _round_trip(tmp_path, route, source, *, factory=False):
    from vcfcf_core.dashboards.loader import load_view

    prefix = "vcfcf_" if factory else "vcfcf_core."
    view_id = _view_element(source).get("id")
    output = tmp_path / f"{route}.yaml"
    parsed_view = None
    if route == "extractor":
        module = importlib.import_module(prefix + "extractor.extractor")
        exported = io.BytesIO()
        with ZipFile(exported, "w") as archive:
            archive.writestr("content.xml", source)
        data = module._parse_view_xml(exported.getvalue(), view_id)
        module._write_view_yaml(output, data)
    elif route == "reverse_local":
        module = importlib.import_module(prefix + "extractor.reverse_local")
        xml_dir = tmp_path / "xml"
        xml_dir.mkdir(exist_ok=True)
        (xml_dir / "synthetic.xml").write_text(source, encoding="utf-8")
        data = module.build_view_uuid_map(xml_dir)[view_id.lower()]
        module._write_view_yaml(output, data, {})
    else:
        module = importlib.import_module(prefix + "dashboards.reverse")
        parsed_view = module.parse_view_from_content_xml(source.encode(), view_id)
        output.write_text(yaml.safe_dump(_dataclass_doc(parsed_view), sort_keys=False), encoding="utf-8")
    return yaml.safe_load(output.read_text()), load_view(output), parsed_view


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("fixture", ["ordinary", "filtered", "instanced"])
def test_source_xml_yaml_reload_is_byte_identical(tmp_path, route, fixture):
    from vcfcf_core.dashboards.render import render_views_xml

    source = _source(fixture)
    doc, view, parsed = _round_trip(tmp_path, route, source)
    assert view.id == _view_element(source).get("id")
    assert render_views_xml([view]) == source
    assert render_views_xml([view]) == render_views_xml([view])
    if parsed is not None:
        assert render_views_xml([parsed]) == source
    if fixture == "ordinary":
        assert "filter" not in doc.get("subject", {})
        assert "summary" not in doc
        assert all(not c.get("is_property", False) and "instanced_group" not in c for c in doc["columns"])


@pytest.mark.parametrize("route", ROUTES)
def test_uniform_filters_preserve_types_group_order_and_optional_absence(tmp_path, route):
    doc, view, _ = _round_trip(tmp_path, route, _source("instanced"))
    groups = doc["subject"]["filter"]
    assert [len(g) for g in groups] == [2, 2]
    assert groups[0][0]["value"] == 12 and type(groups[0][0]["value"]) is int
    assert groups[0][0]["business_hours"] is False
    assert groups[0][0]["transform"] == "AVG"
    assert "business_hours" not in groups[0][1] and "transform" not in groups[0][1]
    assert groups[1][0]["value"] == "true" and groups[1][0]["business_hours"] is True
    assert groups[1][1]["value"] == 1.5 and type(groups[1][1]["value"]) is float
    assert [(s.adapter_kind, s.resource_kind) for s in view.subjects] == [("VMWARE", "Datacenter"), ("VMWARE", "vSphere World")]


@pytest.mark.parametrize("route", ROUTES)
def test_instanced_roles_flags_transformations_and_summary_survive(tmp_path, route):
    doc, view, _ = _round_trip(tmp_path, route, _source("instanced"))
    columns = doc["columns"]
    assert columns[0]["instanced_group"]["show_instance_name"] is False
    assert columns[0]["instanced_group"]["keep_instance_summary"] is True
    assert columns[1]["is_property"] is True and columns[1]["is_string_attribute"] is True
    assert not columns[2].get("is_property", False) and not columns[2].get("is_string_attribute", False)
    assert columns[3]["is_property"] is True and not columns[3].get("is_string_attribute", False)
    assert all("attribute" not in c for c in columns)
    assert columns[4]["instanced_group"] == {"name": "GROUP_synthetic", "prefix": "diskspace", "sample_instance": "262", "suffix": "snapshot:snapshot-1|used"}
    assert view.columns[4].attribute == "diskspace:262|snapshot:snapshot-1|used"
    assert columns[4]["unit"] == "gb" and columns[4]["transformation"] == "MAX"
    assert [columns[4][k] for k in ("yellow_bound", "orange_bound", "red_bound")] == [10.0, 20.0, 30.0]
    assert columns[5]["transformation"] == "TRANSFORM_EXPRESSION"
    assert columns[5]["transform_expression"] == "(current-first)/60000"
    assert columns[6]["transformation"] == "TIMESTAMP"
    assert doc["summary"] == {"display_name": "Synthetic totals", "aggregation": "SUM", "columns": [2, 1]}


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("columns", [None, [0], []])
def test_summary_all_zero_and_empty_indexes_are_distinct(tmp_path, route, columns):
    from vcfcf_core.dashboards.loader import load_view
    from vcfcf_core.dashboards.render import render_views_xml

    # Construct source with the real YAML loader/renderer, never a hand-made model.
    doc = {"id": "77f12d52-3dfc-43e3-958a-63de7395c7c2", "name": "[VCF Content Factory] Synthetic summary", "subject": {"adapter_kind": "VMWARE", "resource_kind": "Datacenter"}, "columns": [{"attribute": "summary|total_number_hosts", "display_name": "Hosts"}, {"attribute": "summary|total_number_vms", "display_name": "VMs"}], "summary": {"display_name": "Synthetic count", "aggregation": "COUNT"}}
    if columns is not None:
        doc["summary"]["columns"] = columns
    path = tmp_path / "source.yaml"
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")
    source = render_views_xml([load_view(path)])
    reversed_doc, view, _ = _round_trip(tmp_path, route, source)
    assert reversed_doc["summary"]["columns"] == ([0, 1] if columns is None else columns)
    assert render_views_xml([view]) == source


def _parse(route, elem):
    if route == "extractor":
        from vcfcf_core.extractor.extractor import _parse_view_def_element
        return _parse_view_def_element(elem)
    if route == "reverse_local":
        from vcfcf_core.extractor.reverse_local import _parse_view_xml_to_dict
        return _parse_view_xml_to_dict(elem)
    from vcfcf_core.dashboards.reverse import parse_view_xml_element
    return parse_view_xml_element(elem)


def _bad_filters():
    good = json.loads(_view_element(_source("filtered")).find("SubjectType").get("filter"))
    raw = json.dumps(good, separators=(",", ":"))
    cases = ["", "{", "null", "[]", "[[]]", "[[1]]", raw.replace('"condition":"GREATER_THAN"', '"condition":"EQUALS","condition":"GREATER_THAN"', 1), raw.replace('"value":12', '"value":NaN', 1), raw.replace('"value":12', '"value":Infinity', 1), raw.replace('"value":12', '"value":1e999', 1)]
    for field in ("condition", "metricKey", "metricValue", "filterType"):
        value = json.loads(raw)
        del value[0][0][field]
        cases.append(json.dumps(value))
    for field, value in [("unexpected", "synthetic-hidden"), ("condition", "LESS_THAN"), ("transform", None), ("transform", 5), ("businessHours", "false"), ("businessHours", None)]:
        payload = json.loads(raw)
        payload[0][0][field] = value
        cases.append(json.dumps(payload))
    for field, value in [("value", True), ("value", None), ("value", []), ("value", {}), ("isStringMetric", True), ("isStringMetric", 0), ("unexpected", 1)]:
        payload = json.loads(raw)
        payload[0][0]["metricValue"][field] = value
        cases.append(json.dumps(payload))
    for field in ("isStringMetric", "value"):
        payload = json.loads(raw)
        del payload[0][0]["metricValue"][field]
        cases.append(json.dumps(payload))
    return cases


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("raw", _bad_filters())
def test_unsupported_filters_fail_before_writing_an_unfiltered_view(route, raw):
    elem = _view_element(_source("filtered"))
    for subject in elem.findall("SubjectType"):
        subject.set("filter", raw)
    with pytest.raises(ValueError, match="subject filter") as failure:
        _parse(route, elem)
    assert "synthetic-hidden" not in str(failure.value)


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("change", ["absent", "different"])
def test_heterogeneous_subject_filters_fail_closed(route, change):
    elem = _view_element(_source("instanced"))
    subject = elem.findall("SubjectType")[-1]
    if change == "absent":
        subject.attrib.pop("filter")
    else:
        payload = json.loads(subject.get("filter"))
        payload[0][0]["metricValue"]["value"] = 99
        subject.set("filter", json.dumps(payload))
    with pytest.raises(ValueError, match="subject filter"):
        _parse(route, elem)


@pytest.mark.parametrize("route", ROUTES)
def test_factory_alias_callers_preserve_supported_xml(tmp_path, route):
    from vcfcf_core.dashboards.render import render_views_xml

    source = _source("instanced")
    _, view, _ = _round_trip(tmp_path, route, source, factory=True)
    assert render_views_xml([view]) == source


@pytest.mark.parametrize("route", ROUTES)
def test_public_callers_propagate_filter_failures(tmp_path, route):
    source = _source("filtered").replace('&quot;GREATER_THAN&quot;', '&quot;UNSUPPORTED&quot;')
    with pytest.raises(ValueError, match="subject filter"):
        _round_trip(tmp_path, route, source)
    assert not (tmp_path / f"{route}.yaml").exists()


@pytest.mark.parametrize("route", ROUTES)
def test_present_default_summary_preserves_default_label_and_aggregation(tmp_path, route):
    from vcfcf_core.dashboards.loader import load_view
    from vcfcf_core.dashboards.render import render_views_xml

    doc = {"id": "77f12d52-3dfc-43e3-958a-63de7395c7c2", "name": "[VCF Content Factory] Synthetic default summary", "subject": {"adapter_kind": "VMWARE", "resource_kind": "Datacenter"}, "columns": [{"attribute": "summary|total_number_hosts", "display_name": "Hosts"}], "summary": True}
    path = tmp_path / "source.yaml"
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")
    source = render_views_xml([load_view(path)])
    reversed_doc, view, _ = _round_trip(tmp_path, route, source)
    assert reversed_doc["summary"] == {"display_name": "Summary", "aggregation": "SUM", "columns": [0]}
    assert render_views_xml([view]) == source


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("value", ["false", "", -3, 0, -1.25])
def test_representable_scalar_filter_values_preserve_exact_types(tmp_path, route, value):
    elem = _view_element(_source("filtered"))
    for subject in elem.findall("SubjectType"):
        payload = json.loads(subject.get("filter"))
        payload[0][0]["metricValue"] = {"isStringMetric": isinstance(value, str), "value": value}
        subject.set("filter", json.dumps(payload))
    parsed = _parse(route, elem)
    actual = parsed.subject_filter[0][0].value if route == "dataclass" else parsed["subject_filter"][0][0]["value"]
    assert actual == value and type(actual) is type(value)


def _column_values(elem):
    return elem.find("Controls/Control[@type='attributes-selector']/Property[@name='attributeInfos']/List")


def _prop(value, name):
    return value.find(f"Property[@name='{name}']")


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("case", ["multiple-drivers", "member-before-driver", "missing-driver-name", "wrong-driver-key", "absent-driver-key", "empty-driver-key", "malformed-member", "missing-property-value", "nested-property-value", "duplicate-property", "invalid-property-flag", "missing-string-value", "missing-driver-flag", "nested-group-name", "missing-show-instance-flag", "missing-keep-summary-flag", "nested-expression"])
def test_ambiguous_groups_and_malformed_fidelity_flags_fail_closed(route, case):
    elem = _view_element(_source("instanced"))
    items = _column_values(elem)
    driver, member = items[0][0], items[1][0]
    if case == "multiple-drivers":
        items.append(deepcopy(items[0]))
    elif case == "member-before-driver":
        first = items[0]
        items.remove(first)
        items.insert(1, first)
    elif case == "missing-driver-name":
        driver.remove(_prop(driver, "instanceGroupName"))
    elif case == "wrong-driver-key":
        _prop(driver, "attributeKey").set("value", "synthetic-hidden")
    elif case == "absent-driver-key":
        driver.remove(_prop(driver, "attributeKey"))
    elif case == "empty-driver-key":
        _prop(driver, "attributeKey").set("value", "")
    elif case == "malformed-member":
        _prop(member, "attributeKey").set("value", "synthetic:hidden")
    elif case == "duplicate-property":
        member.append(deepcopy(_prop(member, "isProperty")))
    elif case == "invalid-property-flag":
        _prop(member, "isProperty").set("value", "synthetic-hidden")
    else:
        prop = {"missing-property-value": _prop(member, "isProperty"), "nested-property-value": _prop(member, "isProperty"), "missing-string-value": _prop(member, "isStringAttribute"), "missing-driver-flag": _prop(driver, "isInstancedGroup"), "nested-group-name": _prop(driver, "instanceGroupName"), "missing-show-instance-flag": _prop(driver, "showInstanceName"), "missing-keep-summary-flag": _prop(driver, "keepInstanceSummary"), "nested-expression": _prop(items[5][0], "transformExpression")}[case]
        prop.attrib.pop("value")
        if case.startswith("nested"):
            ET.SubElement(prop, "List")
    with pytest.raises(ValueError, match="unsupported (instanced group|view column)") as failure:
        _parse(route, elem)
    assert "synthetic-hidden" not in str(failure.value)


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("case", ["empty", "duplicate-block", "multiple-rows", "unknown-list-property", "unknown-scalar-property", "unknown-child", "nested-row", "missing-list", "scalar-list", "missing-label-value", "absent-label", "absent-aggregation", "nested-label", "unknown-aggregation", "duplicate-indexes", "absent-indexes", "scalar-indexes", "nested-indexes", "invalid-index", "out-of-range-index", "missing-index-value", "nested-index-item", "unknown-index-attribute", "duplicate-label"])
def test_unrepresentable_summary_shapes_fail_closed(route, case):
    elem = _view_element(_source("instanced"))
    control = elem.find("Controls/Control[@type='attributes-selector']")
    summary = control.find("Property[@name='summaryInfos']")
    rows = summary[0]
    value = rows[0][0]
    indexes = _prop(value, "attributeIndexes")
    if case == "empty":
        rows.clear()
    elif case == "duplicate-block":
        control.append(deepcopy(summary))
    elif case == "multiple-rows":
        rows.append(deepcopy(rows[0]))
    elif case == "unknown-list-property":
        ET.SubElement(ET.SubElement(value, "Property", name="synthetic-hidden"), "List")
    elif case == "unknown-scalar-property":
        ET.SubElement(value, "Property", name="synthetic-hidden", value="synthetic-hidden")
    elif case == "unknown-child":
        ET.SubElement(value, "synthetic-hidden")
    elif case == "nested-row":
        child = rows[0]
        rows.remove(child)
        ET.SubElement(rows, "List").append(child)
    elif case == "missing-list":
        summary.clear()
        summary.set("name", "summaryInfos")
    elif case == "scalar-list":
        summary.set("value", "synthetic-hidden")
    elif case == "missing-label-value":
        _prop(value, "displayName").attrib.pop("value")
    elif case == "absent-label":
        value.remove(_prop(value, "displayName"))
    elif case == "absent-aggregation":
        value.remove(_prop(value, "aggregation"))
    elif case == "nested-label":
        ET.SubElement(_prop(value, "displayName"), "List")
    elif case == "unknown-aggregation":
        _prop(value, "aggregation").set("value", "synthetic-hidden")
    elif case == "duplicate-indexes":
        value.append(deepcopy(indexes))
    elif case == "absent-indexes":
        value.remove(indexes)
    elif case == "scalar-indexes":
        indexes.set("value", "synthetic-hidden")
    elif case == "nested-indexes":
        indexes[0].append(ET.Element("List"))
    elif case == "invalid-index":
        indexes[0][0].set("value", "1.5")
    elif case == "out-of-range-index":
        indexes[0][0].set("value", "99")
    elif case == "missing-index-value":
        indexes[0][0].attrib.pop("value")
    elif case == "nested-index-item":
        ET.SubElement(indexes[0][0], "Value")
    elif case == "unknown-index-attribute":
        indexes[0][0].set("synthetic-hidden", "synthetic-hidden")
    elif case == "duplicate-label":
        value.append(deepcopy(_prop(value, "displayName")))
    with pytest.raises(ValueError, match="unsupported summaryInfos") as failure:
        _parse(route, elem)
    assert "synthetic-hidden" not in str(failure.value)
