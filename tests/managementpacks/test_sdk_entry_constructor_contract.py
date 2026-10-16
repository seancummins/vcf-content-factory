"""Collector/controller constructor ABI checks inspect bytecode, never run it."""
import re
import shutil
import subprocess

import pytest

from vcfcf_managementpacks import sdk_builder


@pytest.fixture(scope="module")
def compiled(tmp_path_factory):
    if not shutil.which("javac") or not shutil.which("javap"):
        pytest.skip("JDK javac/javap required for bytecode contract tests")
    root = tmp_path_factory.mktemp("entry-abi")
    sources = {
        "Good": 'public Good() {} public Good(String dir, Integer id) {}',
        "GenericCtor": 'public <T> GenericCtor() {} public <T> GenericCtor(String d, Integer i) {}',
        "Strictfp": 'public Strictfp() {} public Strictfp(String d, Integer i) {}',
        "StrictfpGeneric": 'public <T> StrictfpGeneric() {} public <T> StrictfpGeneric(String d, Integer i) {}',
        "StrictfpPrimitive": 'public StrictfpPrimitive() {} public StrictfpPrimitive(String d, int i) {}',
        "StrictfpPrivate": 'public StrictfpPrivate() {} private StrictfpPrivate(String d, Integer i) {}',
        "StrictfpNoBare": 'public StrictfpNoBare(String d, Integer i) {}',
        "Missing": 'public Missing() {}',
        "Private": 'public Private() {} private Private(String d, Integer i) {}',
        "Primitive": 'public Primitive() {} public Primitive(String d, int i) {}',
        "Varargs": 'public Varargs() {} public Varargs(String d, Object... i) {}',
        "ObjectArg": 'public ObjectArg() {} public ObjectArg(String d, Object i) {}',
        "NoBare": 'public NoBare(String d, Integer i) {}',
        "Abstract": 'public Abstract() {} public Abstract(String d, Integer i) {}',
        "Hidden": 'public Hidden() {} public Hidden(String d, Integer i) {}',
        "Inherited": 'public Inherited() {}',
        "NeverRun": 'static { if (true) throw new Error("MUST NOT INITIALIZE"); } '
                    'public NeverRun() { throw new Error("MUST NOT RUN"); } '
                    'public NeverRun(String d, Integer i) { throw new Error("MUST NOT RUN"); }',
    }
    paths = []
    for name, constructors in sources.items():
        modifier = "public abstract" if name == "Abstract" else "public"
        if name.startswith("Strictfp"):
            modifier = "public strictfp"
        if name == "Hidden":
            modifier = ""
        superclass = " extends Good" if name == "Inherited" else ""
        source = root / f"{name}.java"
        source.write_text(
            f"package synthetic; {modifier} class {name}{superclass} {{ {constructors} }}",
            encoding="utf-8",
        )
        paths.append(str(source))
    subprocess.run([shutil.which("javac"), "--release", "11", "-proc:none", "-d", str(root), *paths],
                   check=True, capture_output=True, timeout=30)
    return root


@pytest.mark.parametrize("name", ["Good", "GenericCtor", "NeverRun"])
def test_exact_public_constructors_pass_without_execution(compiled, name):
    sdk_builder._validate_entry_constructor_contract(compiled, f"synthetic.{name}")


@pytest.mark.parametrize("name", ["Strictfp", "StrictfpGeneric"])
def test_java_11_strictfp_constructor_metadata_passes(compiled, name):
    entry_class = f"synthetic.{name}"
    metadata = subprocess.run(
        [shutil.which("javap"), "-public", "-s", str(compiled / "synthetic" / f"{name}.class")],
        check=True, capture_output=True, text=True, timeout=15,
    ).stdout
    assert re.search(r"public strictfp (?:<.*> )?" + re.escape(entry_class) + r"\(", metadata)
    # Confirm the real Java 11 output reproduces the previously rejected case.
    old_pattern = r"public (?:<.*> )?" + re.escape(entry_class) + r"\("
    assert not any(re.match(old_pattern, line.strip()) for line in metadata.splitlines())
    sdk_builder._validate_entry_constructor_contract(compiled, entry_class)


@pytest.mark.parametrize("name,reason", [
    ("Missing", "collector"), ("Private", "collector"),
    ("Primitive", "collector"), ("Varargs", "collector"),
    ("ObjectArg", "collector"), ("NoBare", "controller"),
    ("Abstract", "public and concrete"), ("Hidden", "public and concrete"),
    ("Inherited", "collector"), ("Absent", "not found"),
    ("StrictfpPrimitive", "collector"), ("StrictfpPrivate", "collector"),
    ("StrictfpNoBare", "controller"),
])
def test_invalid_declared_constructor_abi_rejected(compiled, name, reason):
    with pytest.raises(sdk_builder.SdkBuildError, match=reason):
        sdk_builder._validate_entry_constructor_contract(compiled, f"synthetic.{name}")


def test_missing_javap_is_not_a_pass(compiled, monkeypatch):
    monkeypatch.setattr(sdk_builder.shutil, "which", lambda _: None)
    with pytest.raises(sdk_builder.SdkBuildError, match="ABI unverified"):
        sdk_builder._validate_entry_constructor_contract(compiled, "synthetic.Good")


@pytest.mark.parametrize("failure", ["timeout", "exit", "malformed"])
def test_inspection_failures_fail_closed(compiled, monkeypatch, failure):
    def inspect(*args, **kwargs):
        assert kwargs["timeout"] == 15
        assert "-public" in args[0] and "-s" in args[0]
        if failure == "timeout":
            raise subprocess.TimeoutExpired("javap", 15)
        return subprocess.CompletedProcess(args[0], 1 if failure == "exit" else 0,
                                           stdout="not class metadata", stderr="")
    monkeypatch.setattr(sdk_builder.subprocess, "run", inspect)
    with pytest.raises(sdk_builder.SdkBuildError, match="entry-constructor-contract"):
        sdk_builder._validate_entry_constructor_contract(compiled, "synthetic.Good")


def _project(tmp_path, good):
    (tmp_path / "adapter.yaml").write_text('''name: "VCF Content Factory ABI Test"
version: "1.0.0"
build_number: 1
adapter_kind: constructor_contract_test
tier: 2
description: "Synthetic constructor contract test"
entry_class: synthetic.Entry
''', encoding="utf-8")
    (tmp_path / "describe.xml").write_text(
        '<AdapterKind key="constructor_contract_test"><ResourceKinds/></AdapterKind>',
        encoding="utf-8",
    )
    (tmp_path / "src").mkdir()
    collector = 'public Entry(String d, Integer i) {}' if good else ''
    (tmp_path / "src" / "Entry.java").write_text(
        'package synthetic; public class Entry { public Entry() {} ' + collector + '}',
        encoding="utf-8",
    )
    return tmp_path


@pytest.mark.parametrize("good", [False, True])
def test_validate_sdk_enforces_compiled_entry_contract(tmp_path, monkeypatch, compiled, good):
    project = _project(tmp_path, good)
    monkeypatch.setenv("VCFCF_SDK_JAR", "/synthetic-only-marker.jar")
    monkeypatch.setattr(sdk_builder, "_ensure_framework_jar", lambda: None)
    monkeypatch.setattr(sdk_builder, "_build_classpath", lambda _: "")
    errors = sdk_builder.validate_sdk_project(project)
    assert bool(errors) is not good
    if not good:
        assert "collector constructor" in errors[0]


def test_build_rejects_bad_abi_before_packaging(tmp_path, monkeypatch, compiled):
    project = _project(tmp_path, False)
    monkeypatch.setattr(sdk_builder, "_ensure_framework_jar", lambda: None)
    monkeypatch.setattr(sdk_builder, "_build_classpath", lambda _: "")
    def unexpected(*args, **kwargs):
        pytest.fail("invalid constructor ABI must not reach JAR/docs/PAK generation")
    monkeypatch.setattr(sdk_builder, "_package_adapter_jar", unexpected)
    monkeypatch.setattr(sdk_builder, "_generate_docs", unexpected)
    monkeypatch.setattr(sdk_builder, "_write_outer_pak", unexpected)
    with pytest.raises(sdk_builder.SdkBuildError, match="collector constructor"):
        sdk_builder.build_sdk_pak(project, tmp_path / "dist")


def test_no_jdk_reports_constructor_contract_unverified(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path, False)
    monkeypatch.setattr(sdk_builder.shutil, "which", lambda _: None)
    assert sdk_builder.validate_sdk_project(project) == []
    assert "constructor ABI checks (unverified)" in capsys.readouterr().err
