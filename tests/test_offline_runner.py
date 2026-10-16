"""CLI/safety contract for the opt-in runner; never starts a nested full suite."""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "tests/offline/run.py"
spec = importlib.util.spec_from_file_location("offline_runner_contract", RUNNER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_environment_is_explicit_and_uses_owned_scratch(monkeypatch, tmp_path):
    monkeypatch.setenv("VCFOPS_PROD_PASSWORD", "synthetic-do-not-forward")
    monkeypatch.setenv("SSH_AUTH_SOCK", "/synthetic-not-a-socket")
    env = runner.environment(REPO, tmp_path)
    assert "VCFOPS_PROD_PASSWORD" not in env and "SSH_AUTH_SOCK" not in env
    assert "CLASSPATH" not in env and "JAVA_TOOL_OPTIONS" not in env
    assert env["HOME"] == str(tmp_path / "home")
    assert env["TMPDIR"] == str(tmp_path / "tmp")
    assert env["PYTHONDONTWRITEBYTECODE"] == env["PIP_NO_INDEX"] == "1"
    assert "VCFCF_SDK_JAR" not in env
    assert runner.environment(REPO, tmp_path, Path("/synthetic/sdk.jar"))["VCFCF_SDK_JAR"] == "/synthetic/sdk.jar"


@pytest.mark.parametrize("value", ["--collect-only", "/tmp/test.py", "tests/../src/test.py", "tests/no-such-test.py", "tests/test_offline_runner.py::"])
def test_selection_rejects_flags_and_escaping_paths(value):
    with pytest.raises(argparse.ArgumentTypeError):
        runner.selection(value)


def test_selection_rejects_symlink_escape_and_accepts_node(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    outside = tmp_path / "outside.py"
    outside.write_text("# synthetic")
    (repo / "tests/link.py").symlink_to(outside)
    with pytest.raises(argparse.ArgumentTypeError):
        runner.selection("tests/link.py", repo)
    assert runner.selection("tests/test_offline_runner.py::test_environment_is_explicit_and_uses_owned_scratch")


def test_pytest_command_is_serial_clears_defaults_and_preserves_only_exclusion(tmp_path):
    args = runner.pytest_argv(tmp_path, [])
    assert args[:4] == [sys.executable, "-B", "-m", "pytest"]
    assert "tests" in args and "--override-ini=addopts=" in args
    assert args[args.index("-m") + 1] == "pytest"  # first -m is Python's module flag
    assert [args[i + 1] for i, value in enumerate(args) if value == "-m"][1] == ""
    assert "no:cacheprovider" in args and not any(a.startswith("-n") for a in args)
    assert [a for a in args if a.startswith("--deselect=")] == ["--deselect=" + runner.WHEEL_TEST]
    assert not any("xfail" in a or "test_common_setup" in a for a in args)


def test_smoke_sentinel_is_restrictive_exclusive_and_does_not_follow_symlinks(tmp_path):
    sentinel = tmp_path / "synthetic-sentinel"
    runner.create_smoke_sentinel(sentinel)
    assert sentinel.stat().st_mode & 0o777 == 0o600
    original = sentinel.read_text()
    with pytest.raises(FileExistsError):
        runner.create_smoke_sentinel(sentinel)
    link = tmp_path / "synthetic-link"
    link.symlink_to(sentinel)
    with pytest.raises(FileExistsError):
        runner.create_smoke_sentinel(link)
    assert sentinel.read_text() == original


def test_writable_inputs_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(runner.Path, "read_text", lambda *args, **kwargs: pytest.fail("writable inputs must fail before Linux mountinfo is read"))
    with pytest.raises(runner.GuardUnavailable, match="externally read-only"):
        runner.readonly_inputs(tmp_path)


def test_missing_linux_primitives_fail_closed_before_rules(monkeypatch, tmp_path):
    monkeypatch.setattr(runner.platform, "machine", lambda: "unsupported-test-architecture")
    with pytest.raises(runner.GuardUnavailable, match="Linux x86_64/aarch64"):
        runner.install_native_guard(REPO, tmp_path)


def test_nested_invocation_refused_without_new_scratch(monkeypatch, capsys):
    monkeypatch.setenv("VCFCF_OFFLINE_ACTIVE", "1")
    monkeypatch.setattr(runner.tempfile, "mkdtemp", lambda **kwargs: pytest.fail("nested scratch must not be created"))
    assert runner.main(["--smoke"]) == 2
    assert "already guarded" in capsys.readouterr().err


def test_pytest_failure_exit_status_is_preserved(monkeypatch, tmp_path):
    work = tmp_path / "owned"
    work.mkdir()
    monkeypatch.setattr(runner.os, "environ", {})
    monkeypatch.setattr(runner.os, "chdir", lambda path: None)
    monkeypatch.setattr(runner, "readonly_inputs", lambda *args: None)
    monkeypatch.setattr(runner.tempfile, "mkdtemp", lambda **kwargs: str(work))
    monkeypatch.setattr(runner, "install_native_guard", lambda *args: 3)
    monkeypatch.setattr(runner, "wheel_prerequisites", lambda: "synthetic prerequisite status")
    seen = []
    monkeypatch.setattr(runner.subprocess, "run", lambda command: seen.append(command) or SimpleNamespace(returncode=7))
    assert runner.main(["--test", "tests/test_offline_runner.py"]) == 7
    assert seen[0][4] == "tests/test_offline_runner.py"


def test_wheel_prerequisites_are_diagnosed_without_install(monkeypatch):
    def missing(name):
        raise runner.importlib.metadata.PackageNotFoundError(name)
    monkeypatch.setattr(runner.importlib.metadata, "version", missing)
    assert runner.wheel_prerequisites() == "missing local prerequisites: setuptools>=64, setuptools-scm>=8, wheel"


def test_help_has_no_passthrough_or_dependency_install_action():
    result = subprocess.run([sys.executable, "-B", str(RUNNER), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "--smoke" in result.stdout and "--sdk-jar" in result.stdout and "--test" in result.stdout
    assert "No installs, downloads" in result.stdout
    bad = subprocess.run([sys.executable, "-B", str(RUNNER), "--", "echo", "unsafe"], capture_output=True, text=True)
    assert bad.returncode == 2 and "unrecognized arguments" in bad.stderr


def test_smoke_or_already_inherited_native_guard(tmp_path):
    if os.environ.get("VCFCF_OFFLINE_ACTIVE") == "1":
        # Native -S bypasses startup hooks. Never attempt a second guard/full run.
        code = "import socket\ntry: socket.socket()\nexcept PermissionError: pass\nelse: raise AssertionError('native socket guard missing')"
        result = subprocess.run([sys.executable, "-B", "-S", "-c", code], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        directory = os.open(tmp_path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            descriptor = os.open("synthetic-dir-fd", os.O_WRONLY | os.O_CREAT, 0o600, dir_fd=directory)
            os.close(descriptor)
        finally:
            os.close(directory)
        link = tmp_path / "synthetic-interpreter-link"
        link.symlink_to(sys.executable)
        link.unlink()
    else:
        result = subprocess.run([sys.executable, "-B", str(RUNNER), "--smoke"], capture_output=True, text=True)
        if sys.platform != "linux" or not os.statvfs(REPO).f_flag & os.ST_RDONLY:
            assert result.returncode == 2 and "OFFLINE_RUNNER_BLOCKED" in result.stderr
        else:
            capability_errors = (
                "Linux x86_64/aarch64", "PR_SET_NO_NEW_PRIVS unavailable",
                "Landlock ABI query unavailable", "Landlock ABI>=3",
                "Landlock ruleset unavailable", "Landlock path rule unavailable",
                "Landlock restriction unavailable", "libseccomp.so.2 is required",
                "system libseccomp.so.2 could not load", "seccomp initialization failed",
                "required seccomp network rule unavailable", "seccomp could not load",
            )
            blocked = next((line for line in result.stderr.splitlines() if line.startswith("OFFLINE_RUNNER_BLOCKED:")), "")
            if result.returncode == 2 and any(reason in blocked for reason in capability_errors):
                pytest.skip(blocked)
            assert result.returncode == 0, result.stderr
            assert "OFFLINE_SMOKE_PASS" in result.stdout
            assert "NATIVE_CHILD_READ_WRITE_SOCKET_DENIED" in result.stdout
            assert "SYNTHETIC_DOTENV_PASS" in result.stdout
