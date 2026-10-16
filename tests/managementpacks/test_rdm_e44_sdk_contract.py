"""Offline contract qualification, not a collector authentication experiment.

The proprietary SDK is operator-supplied, never downloaded or redistributed.
Bytecode inspection does not invoke any credential accessor or open a socket.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

import pytest


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "com.integrien.alive.common.adapter3."


@pytest.fixture(scope="module")
def sdk():
    path = Path(os.environ.get(
        "VCFCF_SDK_JAR", str(Path.home() / "Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar")
    ))
    if not path.is_file() or shutil.which("javap") is None:
        pytest.skip("Authorized local legacy SDK and javap are required")
    return path


def inspect(sdk, name):
    result = subprocess.run(
        ["javap", "-classpath", str(sdk), "-c", "-p", PACKAGE + name],
        capture_output=True, text=True, timeout=20, check=False,
    )
    assert result.returncode == 0, "Offline SDK inspection failed"
    return result.stdout


def method(bytecode, signature):
    # javap class members begin with exactly two spaces; instructions are indented further.
    start = bytecode.index("  " + signature + ";")
    following = bytecode[start:].splitlines(keepends=True)
    return following[0] + "".join(
        re.split(r"(?m)^  (?:public|private|protected|static) ", "".join(following[1:]), maxsplit=1)[:1]
    )


def test_native_monitoring_lookup_delegates_to_adapter_cache(sdk):
    base = inspect(sdk, "AdapterBase")
    all_resources = method(base, "public java.util.Collection<com.integrien.alive.common.adapter3.config.ResourceConfig> getAllMonitoringResources()")
    key_lookup = method(base, "public com.integrien.alive.common.adapter3.config.ResourceConfig getMonitoringResource(com.integrien.alive.common.adapter3.ResourceKey)")
    assert "AdapterCache.getMonitoringResources" in all_resources
    assert "AdapterCache.getMonitoringResource" in key_lookup
    cache = inspect(sdk, "AdapterCache")
    lookup = method(cache, "public com.integrien.alive.common.adapter3.config.ResourceConfig getMonitoringResource(com.integrien.alive.common.adapter3.ResourceKey)")
    assert "Map.get:" in lookup
    assert "Http" not in lookup and "Socket" not in lookup


def test_sdk_has_no_native_suite_api_client(sdk):
    with zipfile.ZipFile(sdk) as jar:
        names = jar.namelist()
    assert not any("SuiteAPIClient" in name or "SuiteApiClient" in name for name in names)
    base = inspect(sdk, "AdapterBase")
    assert "getSuiteApiClient(" not in base and "getSuiteAPIClient(" not in base


def test_injected_carrier_is_distinct_and_password_requires_platform_crypto(sdk):
    config = inspect(sdk, "config.AdapterConfig")
    assert "public com.integrien.alive.common.adapter3.config.AdapterCredentialConfig getAdapterCredentials();" in config
    credential = inspect(sdk, "config.AdapterCredentialConfig")
    password = method(credential, "public java.lang.String getPassword()")
    assert "com/vmware/vcops/security/Crypt.getDefaultCrypt" in password
    assert "Crypt.decrypt:" in password
    with zipfile.ZipFile(sdk) as jar:
        assert "com/vmware/vcops/security/Crypt.class" not in jar.namelist()


def test_sdk_does_not_discover_an_operations_endpoint(sdk):
    base = inspect(sdk, "AdapterBase")
    endpoint = method(base, "public java.lang.String getConnectionURL(com.integrien.alive.common.adapter3.config.AdapterConfig)")
    assert "aconst_null" in endpoint and "areturn" in endpoint
    assert 'String https://' not in endpoint


def test_sdk_exposes_instance_trust_carriers_not_an_unconditional_hostname_policy(sdk):
    base = inspect(sdk, "AdapterBase")
    assert "public java.security.KeyStore getAdapterTrustStore();" in base
    resource = inspect(sdk, "config.ResourceConfig")
    assert "getTrustedCertificates();" in resource
    assert "getTrustedCertificateIds();" in resource
    verifier = inspect(sdk, "CustomHostnameVerifier")
    assert "getEnforceHostnameVerification" in verifier


def test_required_identity_reads_and_token_lifecycle_are_public_api_operations():
    public = json.loads((ROOT / "reference/docs/operations-api.json").read_text())
    internal = json.loads((ROOT / "reference/docs/internal-api.json").read_text())
    for path, verb in (("/api/resources", "get"), ("/api/resources/{id}", "get"),
                       ("/api/auth/token/acquire", "post"), ("/api/auth/token/release", "post")):
        assert verb in public["paths"][path]
        assert path not in internal["paths"]
    names = {p["name"] for p in public["paths"]["/api/resources"]["get"]["parameters"]}
    assert {"adapterKind", "resourceKind", "page", "pageSize"} <= names
    assert "resourceIdentifiers" not in names  # Do not invent a query parameter.
