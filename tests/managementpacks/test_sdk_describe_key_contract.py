"""SDK descriptor segments are not fully qualified runtime MetricKeys."""
from pathlib import Path
from types import SimpleNamespace
from xml.sax.saxutils import quoteattr

import pytest

from vcfcf_managementpacks import cli, sdk_builder


def _describe(tmp_path, body, namespace=True):
    path = tmp_path / "describe.xml"
    ns = ' xmlns="http://schemas.vmware.com/vcops/schema"' if namespace else ""
    path.write_text(
        f'<AdapterKind{ns} key="test"><ResourceKinds>'
        f'<ResourceKind key="Thing">{body}</ResourceKind>'
        '</ResourceKinds></AdapterKind>', encoding="utf-8",
    )
    return path


@pytest.mark.parametrize("namespace", [False, True])
@pytest.mark.parametrize("tag", ["ResourceAttribute", "ResourceGroup"])
@pytest.mark.parametrize("key", ["identity|format", "storage:vendor", "a|b:c"])
def test_sdk_reserved_separators_rejected(tmp_path, namespace, tag, key):
    path = _describe(tmp_path, f'<{tag} key={quoteattr(key)}/>', namespace)
    errors = sdk_builder._validate_describe_key_contract(path)
    assert len(errors) == 1
    assert tag in errors[0] and "SDK-reserved" in errors[0]


@pytest.mark.parametrize("namespace", [False, True])
def test_grouped_working_descriptor_and_nonmetric_keys_are_valid(tmp_path, namespace):
    path = _describe(tmp_path, '''
        <ResourceIdentifier key="scope:identity|opaque"/>
        <ResourceGroup key="identity">
          <ResourceAttribute key="format" dataType="string" isProperty="true"/>
          <ResourceGroup key="details"><ResourceAttribute key="canonical_name"/></ResourceGroup>
        </ResourceGroup>
        <TraversalSpec key="a|b:c"/>
        <extension:ResourceAttribute xmlns:extension="urn:extension" key="a|b:c"/>
        ''', namespace)
    assert sdk_builder._validate_describe_key_contract(path) == []


@pytest.mark.parametrize("key", ["format", "canonical_name", "vendor.model", "a-b", "capacity bytes", "é"])
def test_no_unproven_character_whitelist(tmp_path, key):
    # The SDK methods check only ':' and '|'; do not silently invent a stricter
    # [A-Za-z0-9_] schema. Other platform requirements remain separate gates.
    path = _describe(tmp_path, f'<ResourceAttribute key={quoteattr(key)}/>')
    assert sdk_builder._validate_describe_key_contract(path) == []


@pytest.mark.parametrize("tag", ["ResourceAttribute", "ResourceGroup"])
def test_missing_required_key_is_rejected(tmp_path, tag):
    assert "missing required key" in sdk_builder._validate_describe_key_contract(
        _describe(tmp_path, f'<{tag}/>')
    )[0]


def test_bad_xml_is_a_validation_failure(tmp_path):
    path = tmp_path / "describe.xml"
    path.write_text("<AdapterKind", encoding="utf-8")
    assert "malformed XML" in sdk_builder._validate_describe_key_contract(path)[0]


def _project(tmp_path):
    (tmp_path / "adapter.yaml").write_text('''name: "VCF Content Factory Test"
version: "1.0.0"
build_number: 1
adapter_kind: test
tier: 2
description: "Synthetic key contract fixture"
''', encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "Test.java").write_text("class Test {}", encoding="utf-8")
    _describe(tmp_path, '<ResourceAttribute key="identity|format"/>')
    return tmp_path


def test_validate_sdk_reports_before_compilation(tmp_path, monkeypatch):
    project = _project(tmp_path)
    monkeypatch.setenv("VCFCF_SDK_JAR", "/nonexistent-sdk.jar")
    monkeypatch.setattr(sdk_builder.shutil, "which", lambda _: "/fake/javac")
    def unexpected(*args, **kwargs):
        pytest.fail("invalid descriptor must not reach compilation")
    monkeypatch.setattr(sdk_builder, "_ensure_framework_jar", unexpected)
    assert any("SDK-reserved" in e for e in sdk_builder.validate_sdk_project(project))


def test_public_validate_cli_returns_failure(tmp_path, capsys):
    project = _project(tmp_path)
    assert cli.cmd_validate_sdk(SimpleNamespace(project_dir=str(project))) == 1
    output = capsys.readouterr()
    assert "SDK-reserved" in output.err + output.out


def test_direct_build_fails_before_compile_docs_or_package(tmp_path, monkeypatch):
    project = _project(tmp_path)
    def unexpected(*args, **kwargs):
        pytest.fail("invalid descriptor must not reach JDK, docs or packaging")
    monkeypatch.setattr(sdk_builder, "_detect_jdk", unexpected)
    monkeypatch.setattr(sdk_builder, "_generate_docs", unexpected)
    monkeypatch.setattr(sdk_builder, "_write_outer_pak", unexpected)
    with pytest.raises(sdk_builder.SdkBuildError, match="SDK-reserved"):
        sdk_builder.build_sdk_pak(project, tmp_path / "dist")
    assert not (tmp_path / "dist").exists()
