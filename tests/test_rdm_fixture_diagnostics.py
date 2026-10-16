"""Failure stages identify verified operations; secret-bearing causes stay private."""
from contextlib import contextmanager
import importlib.util
import logging
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import warnings

import pytest
from requests.exceptions import ConnectionError as RequestConnectionError, Timeout

SPEC = importlib.util.spec_from_file_location("rdm_diagnostics", Path(__file__).parents[1] / "scripts/rdm_lab_probe.py")
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)
SECRET = "synthetic-password-token-raw-ResourceKey-and-inventory"


@pytest.mark.parametrize("active,error,expected,code", [
    ("OPS_READ", RequestConnectionError(SECRET), "OPS_CONNECTION", "TRANSPORT_ERROR"),
    ("OPS_AUTHENTICATION", Timeout(SECRET), "OPS_CONNECTION", "TIMEOUT"),
    ("VCENTER_SESSION", ConnectionError(SECRET), "VCENTER_CONNECTION", "TRANSPORT_ERROR"),
    ("VCENTER_READ", TimeoutError(SECRET), "VCENTER_CONNECTION", "TIMEOUT"),
    ("VCENTER_SESSION", ValueError(SECRET), "VCENTER_SESSION", "FAILED"),
    ("OPS_AUTHENTICATION", ValueError(SECRET), "OPS_AUTHENTICATION", "FAILED"),
    ("FIXTURE_SCHEMA_VALIDATION", ValueError(SECRET), "FIXTURE_SCHEMA_VALIDATION", "FAILED"),
    ("JAVA_PARSER_VALIDATION", subprocess.TimeoutExpired(SECRET, 30, output=SECRET), "JAVA_PARSER_VALIDATION", "TIMEOUT"),
    ("OUTPUT_FILE", PermissionError(SECRET), "OUTPUT_FILE", "FAILED"),
])
def test_verified_operation_and_transport_classification(active, error, expected, code):
    with pytest.raises(probe.FixtureExportError) as caught:
        with probe._fixture_stage(active): raise error
    assert caught.value.stage == expected and caught.value.code == code
    assert caught.value.__cause__ is error


def test_typed_vcenter_auth_failure_not_guessed_from_text():
    class InvalidLogin(Exception): pass
    with pytest.raises(probe.FixtureExportError) as caught:
        with probe._fixture_stage("VCENTER_SESSION", authentication_errors=(InvalidLogin,)):
            raise InvalidLogin(SECRET)
    assert (caught.value.stage, caught.value.code) == ("VCENTER_AUTHENTICATION", "AUTH_REJECTED")
    with pytest.raises(probe.FixtureExportError) as unknown:
        with probe._fixture_stage("VCENTER_SESSION", authentication_errors=(InvalidLogin,)):
            raise ValueError("InvalidLogin password rejected " + SECRET)
    assert unknown.value.stage == "VCENTER_SESSION"


@pytest.mark.parametrize("stage", sorted(probe.FixtureExportError.STAGES))
def test_every_stage_cli_redacts_message_cause_and_third_party_output(stage, monkeypatch, capsys):
    def fail(profile):
        print(SECRET)
        print(SECRET, file=sys.stderr)
        logging.error(SECRET)
        warnings.warn(SECRET)
        try: raise ValueError(SECRET)
        except ValueError as cause:
            raise probe.FixtureExportError(SECRET, stage=stage) from cause
    monkeypatch.setattr(probe, "_export_fixture", fail)
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "fixture-export"]) == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err == f"Fixture export failed: stage={stage}; code=FAILED; no success claimed.\n"
    assert SECRET not in output.err


def test_untrusted_diagnostic_fields_are_not_printed(monkeypatch, capsys):
    def fail(profile):
        error = probe.FixtureExportError(SECRET)
        error.stage = error.code = SECRET
        raise error
    monkeypatch.setattr(probe, "_export_fixture", fail)
    assert probe.main(["--execute", "--allow-read-only-lab", "--mode", "fixture-export"]) == 2
    assert capsys.readouterr().err == "Fixture export failed: stage=UNCLASSIFIED; code=FAILED; no success claimed.\n"


@pytest.mark.parametrize("status,stage,code", [(401, "OPS_AUTHENTICATION", "AUTH_REJECTED"),
    (403, "OPS_AUTHORIZATION", "HTTP_ERROR"), (500, "OPS_READ", "HTTP_ERROR")])
def test_http_evidence_distinguishes_authentication_authorization_and_server_failure(status, stage, code):
    response = SimpleNamespace(status_code=status, text=SECRET)
    client = SimpleNamespace(_request=lambda *args, **kwargs: response)
    with pytest.raises(probe.FixtureExportError) as caught: probe._capture_fixture_resources(client)
    assert (caught.value.stage, caught.value.code) == (stage, code)
    assert SECRET not in str(caught.value)


@pytest.mark.parametrize("count,code", [(0, "NO_RDM"), (2, "MULTIPLE_RDMS")])
def test_rdm_count_has_verified_reason(count, code):
    with pytest.raises(probe.FixtureExportError) as caught:
        probe._single_rdm_fixture_mapping(None, None, [object()] * count)
    assert (caught.value.stage, caught.value.code) == ("RDM_AMBIGUITY", code)


def test_missing_sdk_identifies_local_setup_without_reading_credentials(monkeypatch):
    monkeypatch.setenv("VCFCF_SDK_JAR", "/nonexistent-synthetic-sdk.jar")
    with pytest.raises(probe.FixtureExportError) as caught:
        with probe._fixture_validator(): pytest.fail("missing SDK accepted")
    assert (caught.value.stage, caught.value.code) == ("JAVA_PARSER_SETUP", "SDK_UNAVAILABLE")


@pytest.mark.parametrize("compile_status,parse_status,stage,code", [
    (1, 0, "JAVA_PARSER_SETUP", "COMPILE_FAILED"),
    (0, 2, "JAVA_PARSER_VALIDATION", "PARSER_REJECTED"),
])
def test_java_diagnostics_never_include_captured_tool_output(compile_status, parse_status, stage, code,
                                                           tmp_path, monkeypatch):
    sdk = tmp_path / "synthetic-sdk.jar"
    sdk.touch()
    monkeypatch.setenv("VCFCF_SDK_JAR", str(sdk))
    monkeypatch.setattr(probe.shutil, "which", lambda name: name)
    def run(args, **kwargs):
        assert kwargs.get("capture_output") is True
        if args[0] == "java": assert kwargs["input"] == SECRET.encode()
        return SimpleNamespace(returncode=compile_status if args[0] == "javac" else parse_status,
                               stdout=SECRET.encode(), stderr=SECRET.encode())
    monkeypatch.setattr(probe.subprocess, "run", run)
    with pytest.raises(probe.FixtureExportError) as caught:
        with probe._fixture_validator() as validate: validate(SECRET.encode())
    assert (caught.value.stage, caught.value.code) == (stage, code)
    assert SECRET not in str(caught.value)


@pytest.fixture
def export_setup(monkeypatch):
    import vcfcf_common.client
    monkeypatch.setattr(probe, "_fixture_output_path", lambda: None)
    client = SimpleNamespace(authenticate=lambda: None)
    monkeypatch.setattr(vcfcf_common.client.VCFOpsClient, "from_env", lambda *args, **kwargs: client)
    for key in ("HOST", "USER", "PASSWORD"):
        monkeypatch.setenv(f"RDM_PROBE_VCENTER_{key}", "synthetic")
    @contextmanager
    def validator(): yield lambda payload: None
    monkeypatch.setattr(probe, "_fixture_validator", validator)
    monkeypatch.setattr(probe, "_capture_soap_fixture", lambda: {})
    monkeypatch.setattr(probe, "_capture_fixture_resources", lambda client: [])
    monkeypatch.setattr(probe, "_fixture_from_resources", lambda *args: {})
    monkeypatch.setattr(probe, "_write_fixture", lambda payload: None)
    released = []
    monkeypatch.setattr(probe, "_release_operations_token", lambda *args: released.append(True))
    return client, released


@pytest.mark.parametrize("function,stage", [("_fixture_output_path", "OUTPUT_FILE"),
    ("_capture_soap_fixture", "VCENTER_READ"), ("_capture_fixture_resources", "OPS_READ"),
    ("_fixture_from_resources", "VM_IDENTITY_CORRELATION"), ("_write_fixture", "OUTPUT_FILE")])
def test_pipeline_stages_with_synthetic_inputs(function, stage, export_setup, monkeypatch):
    monkeypatch.setattr(probe, function, lambda *args: (_ for _ in ()).throw(ValueError(SECRET)))
    with pytest.raises(probe.FixtureExportError) as caught: probe._export_fixture("devel")
    assert caught.value.stage == stage
    if function != "_fixture_output_path": assert export_setup[1] == [True]


def test_authentication_failure_is_separate_and_cleanup_preserved(export_setup):
    client, released = export_setup
    client.authenticate = lambda: (_ for _ in ()).throw(RuntimeError(SECRET))
    with pytest.raises(probe.FixtureExportError) as caught: probe._export_fixture("devel")
    assert (caught.value.stage, caught.value.code) == ("OPS_AUTHENTICATION", "FAILED")
    assert released == [True]


def test_inner_diagnostic_is_not_overwritten_by_outer_stage():
    with pytest.raises(probe.FixtureExportError) as caught:
        with probe._fixture_stage("JAVA_PARSER_SETUP"):
            with probe._fixture_stage("VM_IDENTITY_CORRELATION"):
                raise ValueError(SECRET)
    assert caught.value.stage == "VM_IDENTITY_CORRELATION"


def test_serialization_failure_is_sanitized_and_does_not_write(export_setup, monkeypatch):
    monkeypatch.setattr(probe, "_fixture_from_resources", lambda *args: {"synthetic": "\ud800"})
    monkeypatch.setattr(probe, "_write_fixture", lambda *args: pytest.fail("unserializable fixture was written"))
    with pytest.raises(probe.FixtureExportError) as caught: probe._export_fixture("devel")
    assert (caught.value.stage, caught.value.code, caught.value.field) == (
        "FIXTURE_SCHEMA_VALIDATION", "FIXTURE_SERIALIZATION_FAILED", "fixture")
    assert isinstance(caught.value.__cause__, UnicodeEncodeError)
    assert export_setup[1] == [True]
