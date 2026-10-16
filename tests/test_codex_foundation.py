"""Contract tests for the additive Codex foundation."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": f"{ROOT / 'src'}:{os.environ.get('PYTHONPATH', '')}"},
        check=False,
    )


def test_codex_skills_pass_parity_check() -> None:
    result = run(sys.executable, "scripts/check_skill_parity.py")
    assert result.returncode == 0, result.stderr
    assert "Codex skill parity: PASS" in result.stdout


def test_preflight_rejects_unknown_option_without_bootstrapping() -> None:
    result = run("bash", "scripts/codex-preflight.sh", "--unknown")
    assert result.returncode == 2
    assert "Usage:" in result.stderr


def test_changed_content_validator_rejects_bad_invocation() -> None:
    result = run("bash", "scripts/validate-changed-content.sh")
    assert result.returncode == 2
    assert "Usage:" in result.stderr


def test_tier2_verifier_rejects_missing_arguments_before_work() -> None:
    result = run("bash", "scripts/verify-tier2-sdk.sh")
    assert result.returncode == 2
    assert "Usage:" in result.stderr
