"""Synthetic, offline credential policy and all-entry-point regression tests."""
import argparse
import hashlib
import io
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import zipfile

import pytest

from vcfcf_managementpacks import cli, sdk_builder
from vcfcf_managementpacks.pak_compare import (
    BLOCKING, INFO, WARNING, compare_paks, compare_pak_directory, format_report,
)


FIELD = '<CredentialField key="password" nameKey="3" dispOrder="1" type="string" required="true" password="true"/>'


def descriptor(key="a", *, auth=True, required=None, refs=None, fields=FIELD, kinds=None, namespace=""):
    if kinds is None:
        kinds = '<CredentialKinds><CredentialKind key="login" nameKey="2">' + fields + '</CredentialKind></CredentialKinds>' if auth else ''
    binding = (' credentialKind="login"' if auth else '') if refs is None else f' credentialKind="{refs}"'
    required = ('false' if not auth else 'true') if required is None else required
    required_attr = '' if required == 'OMIT' else f' isCredentialRequired="{required}"'
    return f'<AdapterKind key="{key}" nameKey="1" version="1"{namespace}>{kinds}<ResourceKinds><ResourceKind key="{key}" nameKey="4" type="7"{binding}{required_attr}/><ResourceKind key="data" nameKey="5" type="1"/></ResourceKinds></AdapterKind>'


def pak(path, key="a", xml=None, *, extra=None, nested=None, manifest_key=None):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(f"{key}/conf/describe.xml", xml if xml is not None else descriptor(key))
        z.writestr(f"{key}.jar", b"fixture")
        if extra:
            for name, data in extra:
                z.writestr(name, data)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("manifest.txt", json.dumps({"adapter_kinds": [manifest_key or key], "adapters": ["adapters.zip"]}))
        z.writestr("adapters.zip", buf.getvalue() if nested is None else nested)
    return path


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def structural(a, b):
    return compare_paks(a, b, policy="structural", reference_sha256=digest(b))


@pytest.mark.parametrize("reverse", [False, True])
def test_structural_optional_differences_and_legacy_preserved(tmp_path, reverse):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False))
    b = pak(tmp_path / "b.pak", "b")
    if reverse:
        a, b = b, a
    old = compare_paks(a, b)
    assert {f.code for f in old.blocking()} == {"D1", "D6"}
    assert format_report(old) == format_report(compare_paks(a, b, policy="legacy"))
    new = structural(a, b)
    assert not new.blocking()
    assert {f.code for f in new.infos()} >= {"D1", "D6"}
    assert all("both independent credential contracts valid" in f.message for f in new.infos() if f.code in {"D1", "D6"})
    report = format_report(new)
    assert "Policy: structural/1" in report and "Gate: PASS" in report
    assert digest(a) in report and digest(b) in report and "D1:" in report


@pytest.mark.parametrize("required", ["false", "0", " false ", "\t0\n"])
def test_explicit_false_boolean_forms_namespaced_and_no_auth(tmp_path, required):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False, required=required, namespace=' xmlns="http://schemas.vmware.com/vcops/schema"'))
    b = pak(tmp_path / "b.pak", "b", descriptor("b", auth=False))
    assert not structural(a, b).blocking()


@pytest.mark.parametrize("auth", [False, True])
def test_same_adapter_valid_upgrade(tmp_path, auth):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=auth))
    b = pak(tmp_path / "b.pak", xml=descriptor(auth=auth))
    assert not compare_paks(a, b, policy="upgrade").blocking()
    assert any(f.code == "P-IDENTITY" for f in structural(a, b).blocking())


@pytest.mark.parametrize("required", ["true", "1", " true ", "OMIT"])
def test_unbound_required_blocks_both_sides_even_equal(tmp_path, required):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False, required=required))
    b = pak(tmp_path / "b.pak", "b", descriptor("b", auth=False, required=required))
    blockers = structural(a, b).blocking()
    assert len([f for f in blockers if f.code == "C-FREQUIRED"]) == 2
    assert any(f.message.startswith("candidate:") for f in blockers)
    assert any(f.message.startswith("reference:") for f in blockers)


@pytest.mark.parametrize("required", ["false", "true", "0", "1", "OMIT"])
def test_optional_auth_and_default_true_with_binding_valid(tmp_path, required):
    a = pak(tmp_path / "a.pak", xml=descriptor(required=required))
    b = pak(tmp_path / "b.pak", "b")
    assert not structural(a, b).blocking()


@pytest.mark.parametrize("refs", ["", "unknown", "login,", ",login", "login,login", "login, login"])
def test_invalid_bindings_block_even_optional(tmp_path, refs):
    a = pak(tmp_path / "a.pak", xml=descriptor(required="false", refs=refs))
    b = pak(tmp_path / "b.pak", "b")
    assert "C-SBINDING" in {f.code for f in structural(a, b).blocking()}


@pytest.mark.parametrize("fields,code", [
    ("", "C-SFIELD"),
    (FIELD + FIELD, "C-SKEY"),
    (FIELD.replace('key="password"', 'key=""'), "C-SATTR"),
    (FIELD.replace('nameKey="3"', ''), "C-SATTR"),
    (FIELD.replace('dispOrder="1"', ''), "C-SATTR"),
    (FIELD.replace('dispOrder="1"', 'dispOrder="x"'), "C-SATTR"),
    (FIELD.replace('type="string"', 'type="secret"'), "C-STYPE"),
    (FIELD.replace('required="true"', 'required=""'), "C-SBOOL"),
    (FIELD.replace('password="true"', 'password="yes"'), "C-SBOOL"),
    (FIELD.replace('/>', ' enum="maybe"/>'), "C-SBOOL"),
])
def test_invalid_field_metadata(tmp_path, fields, code):
    a = pak(tmp_path / "a.pak", xml=descriptor(fields=fields))
    b = pak(tmp_path / "b.pak", "b")
    assert code in {f.code for f in structural(a, b).blocking()}


def test_optional_field_type_and_enum_supported_without_echoing_values(tmp_path):
    field = FIELD.replace(' type="string"', '').replace('/>', ' enum="true" default="SENSITIVE"><enum value="SENSITIVE" default="true"/></CredentialField>')
    a = pak(tmp_path / "a.pak", xml=descriptor(fields=field))
    b = pak(tmp_path / "b.pak", "b")
    result = structural(a, b)
    assert not result.blocking()
    assert "SENSITIVE" not in format_report(result)


@pytest.mark.parametrize("kinds,code", [
    ('<CredentialKinds/>', "C-FNOAUTH"),
    ('<CredentialKinds/><CredentialKinds/>', "C-SCONTAINER"),
    ('<CredentialKinds><CredentialKind key="login"/></CredentialKinds>', "C-SATTR"),
    ('<CredentialKinds><CredentialKind key="" nameKey="1"/></CredentialKinds>', "C-SATTR"),
    ('<CredentialKinds>' + ('<CredentialKind key="login" nameKey="1">' + FIELD + '</CredentialKind>') * 2 + '</CredentialKinds>', "C-SKEY"),
])
def test_invalid_containers_and_kinds(tmp_path, kinds, code):
    a = pak(tmp_path / "a.pak", xml=descriptor(kinds=kinds))
    b = pak(tmp_path / "b.pak", "b")
    assert code in {f.code for f in structural(a, b).blocking()}


@pytest.mark.parametrize("required", ["", "FALSE", "yes"])
def test_invalid_requiredness(tmp_path, required):
    a = pak(tmp_path / "a.pak", xml=descriptor(required=required))
    b = pak(tmp_path / "b.pak", "b")
    assert "C-SBOOL" in {f.code for f in structural(a, b).blocking()}


def test_unbound_valid_declaration_warning(tmp_path):
    a = pak(tmp_path / "a.pak", xml=descriptor(required="false", refs=None).replace(' credentialKind="login"', ''))
    b = pak(tmp_path / "b.pak", "b")
    result = structural(a, b)
    assert not result.blocking()
    assert any(f.code == "C-UNBOUND" and f.severity == WARNING for f in result.findings)


@pytest.mark.parametrize("change", [
    lambda x: x.replace('key="login"', 'key="renamed"').replace('credentialKind="login"', 'credentialKind="renamed"'),
    lambda x: x.replace('key="password"', 'key="renamed"'),
    lambda x: x.replace('type="string"', 'type="integer"'),
    lambda x: x.replace('password="true"', 'password="false"'),
    lambda x: x.replace('required="false"', 'required="true"'),
    lambda x: x.replace('</CredentialKind>', '<CredentialField key="new" nameKey="5" dispOrder="2" required="true"/></CredentialKind>'),
])
def test_upgrade_regressions_even_same_counts(tmp_path, change):
    old = descriptor(fields=FIELD.replace('required="true"', 'required="false"'))
    a = pak(tmp_path / "a.pak", xml=change(old))
    b = pak(tmp_path / "b.pak", xml=old)
    assert "U-CREDENTIAL" in {f.code for f in compare_paks(a, b, policy="upgrade").blocking()}


def test_upgrade_removal_and_instance_requirement(tmp_path):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False))
    b = pak(tmp_path / "b.pak")
    assert {"D1", "D6", "U-CREDENTIAL"} <= {f.code for f in compare_paks(a, b, policy="upgrade").blocking()}
    a = pak(a, xml=descriptor(required="true"))
    b = pak(b, xml=descriptor(required="false"))
    assert "U-CREDENTIAL" in {f.code for f in compare_paks(a, b, policy="upgrade").blocking()}


def test_upgrade_optional_addition_warns_without_blocking(tmp_path):
    a = pak(tmp_path / "a.pak", xml=descriptor(fields=FIELD + '<CredentialField key="new" nameKey="5" dispOrder="2" required="false"/>'))
    b = pak(tmp_path / "b.pak")
    result = compare_paks(a, b, policy="upgrade")
    assert not result.blocking()
    assert any(f.code == "D3" for f in result.warnings())


@pytest.mark.parametrize("side", ["candidate", "reference"])
@pytest.mark.parametrize("defect", ["xml", "zip", "nested", "duplicate", "ambiguous", "identity", "family", "instance"])
def test_invalid_inputs_fail_closed_on_each_side(tmp_path, side, defect):
    a = pak(tmp_path / "a.pak")
    b = pak(tmp_path / "b.pak", "b")
    bad, key = (a, "a") if side == "candidate" else (b, "b")
    if defect == "xml":
        pak(bad, key, '<bad SECRET')
    elif defect == "zip":
        bad.write_bytes(b"invalid zip")
    elif defect == "nested":
        pak(bad, key, nested=b"invalid zip")
    elif defect == "duplicate":
        with pytest.warns(UserWarning):
            pak(bad, key, extra=[(f"{key}/conf/describe.xml", descriptor(key))])
    elif defect == "ambiguous":
        pak(bad, key, extra=[("other/conf/describe.xml", descriptor("other"))])
    elif defect == "identity":
        pak(bad, key, manifest_key="wrong")
    elif defect == "family":
        pak(bad, key + "_adapter3")
    elif defect == "instance":
        pak(bad, key, descriptor(key).replace('type="7"', 'type="1"'))
    result = structural(a, b)
    assert result.blocking()
    assert any(f.message.startswith(side + ":") for f in result.blocking())
    assert "SECRET" not in format_report(result)


def test_policy_and_digest_errors(tmp_path):
    a, b = pak(tmp_path / "a.pak"), pak(tmp_path / "b.pak", "b")
    with pytest.raises(ValueError):
        compare_paks(a, b, policy="unknown")
    for sha in (None, "bad", "0" * 64):
        with pytest.raises(ValueError):
            compare_paks(a, b, policy="structural", reference_sha256=sha)
    with pytest.raises(ValueError):
        compare_pak_directory(a, tmp_path, policy="structural", reference_sha256=digest(b))
    assert compare_paks(a, b, policy="upgrade").blocking()


def kit(tmp_path):
    from vcfcf_managementpacks.buildkit import _KIT_INIT, _KIT_MAIN, _FACTORY_SOURCES, _IMPORT_REWRITES
    pkg = tmp_path / "portable" / "sdk_buildkit"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text(_KIT_INIT)
    (pkg / "__main__.py").write_text(_KIT_MAIN)
    for name, source in _FACTORY_SOURCES.items():
        text = source.read_text()
        for pattern, replacement in _IMPORT_REWRITES.get(name, []):
            text = re.sub(pattern, replacement, text)
        (pkg / name).write_text(text)
    env = dict(os.environ, PYTHONPATH=str(pkg.parent))
    return env


@pytest.mark.parametrize("mode,expected", [("legacy", 1), ("structural", 0), ("upgrade", 1)])
def test_factory_and_isolated_buildkit_cli_modes(tmp_path, mode, expected):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False))
    b = pak(tmp_path / "b.pak", "b")
    args = cli.build_parser().parse_args(["pak-compare", str(a), str(b), "--policy", mode, "--reference-sha256", digest(b)])
    assert cli.cmd_pak_compare(args) == expected
    result = subprocess.run([sys.executable, "-m", "sdk_buildkit", "pak-compare", str(a), str(b), "--policy", mode, "--reference-sha256", digest(b)], cwd="/tmp", env=kit(tmp_path), capture_output=True, text=True, timeout=30)
    assert result.returncode == expected, result.stderr
    if mode != "legacy":
        assert f"Policy: {mode}/1" in result.stdout


def test_automatic_gate_uses_exact_reference_and_fails_invalid(tmp_path, monkeypatch):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False))
    b = pak(tmp_path / "b.pak", "b")
    monkeypatch.setattr(sdk_builder, "_REFERENCES_DIR", tmp_path / "absent")
    kwargs = dict(policy="structural", reference_pak=b, reference_sha256=digest(b), release_build=True)
    sdk_builder._run_pak_compare(a, **kwargs)
    with pytest.raises(sdk_builder.PakCompareGateError):
        sdk_builder._run_pak_compare(a, policy="structural")
    with pytest.raises(sdk_builder.PakCompareGateError):
        sdk_builder._run_pak_compare(a, **dict(kwargs, reference_sha256="0" * 64))
    pak(a, xml=descriptor(auth=False, required="OMIT"))
    with pytest.raises(sdk_builder.PakCompareGateError):
        sdk_builder._run_pak_compare(a, **kwargs)


def test_build_flags_factory_and_generated_cli(tmp_path):
    from vcfcf_managementpacks.buildkit import _KIT_MAIN
    ns = {"__name__": "test_kit"}
    exec(compile(_KIT_MAIN, "kit/__main__.py", "exec"), ns)
    for parser in (cli.build_parser(), ns["_build_parser"]()):
        args = parser.parse_args(["build-sdk", "project", "--pak-compare-policy", "structural", "--pak-compare-reference", "ref.pak", "--pak-compare-reference-sha256", "a" * 64])
        assert args.pak_compare_policy == "structural"
        assert args.pak_compare_reference == "ref.pak"
        assert args.pak_compare_reference_sha256 == "a" * 64


def test_factory_build_dispatch_propagates_policy(tmp_path, monkeypatch):
    seen = {}
    def build(*args, **kwargs):
        seen.update(kwargs)
        return tmp_path / "out.pak"
    monkeypatch.setattr(sdk_builder, "build_sdk_pak", build)
    args = cli.build_parser().parse_args(["build-sdk", str(tmp_path), "--pak-compare-policy", "structural", "--pak-compare-reference", "ref.pak", "--pak-compare-reference-sha256", "a" * 64])
    assert cli.cmd_build_sdk(args) == 0
    assert seen["pak_compare_policy"] == "structural"
    assert seen["pak_compare_reference"] == "ref.pak"


def test_gate_built_pak_propagates_policy_and_removes_bad_release(tmp_path, monkeypatch):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False))
    b = pak(tmp_path / "b.pak", "b")
    sdk_builder._gate_built_pak(a, release_build=True, warn_only=False, policy="structural", reference_pak=b, reference_sha256=digest(b))
    assert a.exists()
    with pytest.raises(sdk_builder.PakCompareGateError):
        sdk_builder._gate_built_pak(a, release_build=True, warn_only=False, policy="structural", reference_pak=b, reference_sha256="0" * 64)
    assert not a.exists()


def test_java_package_can_contain_docker_icons_but_not_container_entrypoint(tmp_path):
    a = pak(tmp_path / "a.pak", extra=[("a/resources/DockerContainer.svg", "icon")])
    b = pak(tmp_path / "b.pak", "b")
    assert not structural(a, b).blocking()
    pak(a, extra=[("a.conf", "container marker")])
    assert any(f.code == "C-FFAMILY" for f in structural(a, b).blocking())


@pytest.mark.parametrize("attr", ["isCredentialRequired", "required", "password", "enum"])
def test_xml_boolean_rejects_non_xml_whitespace(tmp_path, attr):
    xml = descriptor()
    if attr == "enum":
        xml = xml.replace('type="string"', 'type="string" enum="\u00a0false\u00a0"')
    else:
        xml = xml.replace(f'{attr}="true"', f'{attr}="\u00a0true\u00a0"')
    a = pak(tmp_path / "a.pak", xml=xml)
    b = pak(tmp_path / "b.pak", "b")
    assert any(f.code == "C-SBOOL" for f in structural(a, b).blocking())


@pytest.mark.parametrize("typ", ["+7", "07", " 7 "])
def test_instance_type_integer_lexical_forms(tmp_path, typ):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False).replace('type="7"', f'type="{typ}"'))
    b = pak(tmp_path / "b.pak", "b", descriptor("b", auth=False))
    assert not structural(a, b).blocking()


def test_string_key_whitespace_cannot_alias_binding_or_hide_upgrade_rename(tmp_path):
    a = pak(tmp_path / "a.pak", xml=descriptor().replace('key="login"', 'key=" login "'))
    b = pak(tmp_path / "b.pak", "b")
    assert any(f.code == "C-SBINDING" for f in structural(a, b).blocking())
    pak(a, xml=descriptor().replace('key="password"', 'key="password "'))
    pak(b)
    assert any(f.code == "U-CREDENTIAL" for f in compare_paks(a, b, policy="upgrade").blocking())


def test_multiple_valid_kinds_count_difference_and_data_resource_bindings(tmp_path):
    extra = '<CredentialKind key="other" nameKey="8">' + FIELD + '</CredentialKind>'
    xml = descriptor().replace('</CredentialKinds>', extra + '</CredentialKinds>').replace('credentialKind="login"', 'credentialKind=" login , other "')
    a = pak(tmp_path / "a.pak", xml=xml)
    b = pak(tmp_path / "b.pak", "b")
    result = structural(a, b)
    assert not result.blocking()
    assert any(f.code == "D2" for f in result.infos())
    assert any(f.code == "D3" for f in result.warnings())
    assert any(f.code == "D2" for f in compare_paks(a, b).blocking())
    pak(a, xml=xml.replace('key="data" nameKey="5"', 'key="data" credentialKind="missing" nameKey="5"'))
    assert any(f.code == "C-SBINDING" for f in structural(a, b).blocking())


def test_unknown_and_absent_references_cannot_skip_explicit_build_policy(tmp_path, monkeypatch):
    a = pak(tmp_path / "a.pak")
    monkeypatch.setattr(sdk_builder, "_REFERENCES_DIR", tmp_path / "absent")
    for kwargs in ({"policy": "unknown"}, {"policy": "upgrade"}, {"policy": "structural"}, {"reference_sha256": "a" * 64}):
        with pytest.raises(sdk_builder.PakCompareGateError):
            sdk_builder._run_pak_compare(a, **kwargs)


def test_missing_required_reference_blocks_automatic_gate_and_no_warn_override(tmp_path):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False))
    b = pak(tmp_path / "b.pak", "b", descriptor("b", auth=False, required="OMIT"))
    with pytest.raises(sdk_builder.PakCompareGateError):
        sdk_builder._run_pak_compare(a, policy="structural", reference_pak=b, reference_sha256=digest(b), warn_only=True)
    with pytest.raises(sdk_builder.PakCompareGateError):
        sdk_builder._run_pak_compare(a, policy="structural", reference_pak=tmp_path / "missing.pak", reference_sha256="a" * 64)
    with pytest.raises(sdk_builder.PakCompareGateError):
        sdk_builder._run_pak_compare(a, release_build=True, warn_only=True)


def test_cli_digest_directory_and_unknown_policy_failures(tmp_path):
    a = pak(tmp_path / "a.pak")
    b = pak(tmp_path / "b.pak", "b")
    env = kit(tmp_path)
    cases = [[str(a), str(b), "--policy", "structural"],
             [str(a), str(b), "--policy", "structural", "--reference-sha256", "0" * 64],
             [str(a), "--reference-dir", str(tmp_path), "--policy", "structural"],
             [str(a), str(b), "--policy", "unknown"]]
    for argv in cases:
        assert subprocess.run([sys.executable, "-m", "sdk_buildkit", "pak-compare", *argv], cwd="/tmp", env=env, capture_output=True, timeout=30).returncode != 0
    for argv in cases[:-1]:
        assert cli.cmd_pak_compare(cli.build_parser().parse_args(["pak-compare", *argv])) == 1


def test_schema_optional_booleans_retain_unknown_requiredness(tmp_path):
    old = FIELD.replace(' required="true"', '').replace(' password="true"', '')
    a = pak(tmp_path / "a.pak", xml=descriptor(fields=old))
    b = pak(tmp_path / "b.pak", xml=descriptor(fields=old))
    assert not compare_paks(a, b, policy="upgrade").blocking()
    pak(a, xml=descriptor(fields=old.replace('/>', ' required="true"/>')))
    assert any(f.code == "U-CREDENTIAL" for f in compare_paks(a, b, policy="upgrade").blocking())


def test_isolated_buildkit_automatic_gate_and_build_dispatch(tmp_path):
    a = pak(tmp_path / "a.pak", xml=descriptor(auth=False))
    b = pak(tmp_path / "b.pak", "b")
    env = kit(tmp_path)
    script = '''
import sys
from pathlib import Path
from sdk_buildkit import sdk_builder as s
from sdk_buildkit import __main__ as main
a, b = map(Path, sys.argv[1:3])
digest = sys.argv[3]
s._run_pak_compare(a, release_build=True, policy="structural", reference_pak=b, reference_sha256=digest)
seen = {}
def fake_build(*args, **kwargs):
    seen.update(kwargs)
    return a
s.build_sdk_pak = fake_build
sys.argv = ["sdk_buildkit", "build-sdk", ".", "--pak-compare-policy", "structural", "--pak-compare-reference", str(b), "--pak-compare-reference-sha256", digest]
assert main.main() == 0
assert seen["pak_compare_policy"] == "structural"
assert seen["pak_compare_reference"] == str(b)
assert seen["pak_compare_reference_sha256"] == digest
'''
    argv = [sys.executable, "-c", script, str(a), str(b), digest(b)]
    result = subprocess.run(argv, cwd="/tmp", env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    pak(b, "b", descriptor("b", auth=False, required="OMIT"))
    result = subprocess.run(argv[:-1] + [digest(b)], cwd="/tmp", env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode != 0 and "C-FREQUIRED" in result.stderr


def test_native_manifest_without_adapters_key_remains_supported(tmp_path):
    a = pak(tmp_path / "a.pak")
    b = pak(tmp_path / "b.pak", "b")
    with zipfile.ZipFile(a) as z:
        data = {name: z.read(name) for name in z.namelist()}
    manifest = json.loads(data["manifest.txt"])
    del manifest["adapters"]
    data["manifest.txt"] = json.dumps(manifest)
    with zipfile.ZipFile(a, "w") as z:
        for name, content in data.items():
            z.writestr(name, content)
    assert not any(f.code.startswith("C-") for f in structural(a, b).blocking())
