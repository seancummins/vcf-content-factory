#!/usr/bin/env python3
"""Check the deliberate Claude/Codex skill inventory and essential contracts.

The two directories are intentionally independent during Increment A. This
checker prevents a renamed, deleted, or skeletal Codex skill from silently
falling out of parity with the existing Claude implementation. It does not
require byte-for-byte copies: each runtime has its own concise instructions.
"""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PAIRS = {
    "vcfops-api": ("VCF Operations API", "explicit user approval"),
    "vcfops-content-model": ("VCF Operations content model", "RULE-011"),
    "vcfops-project-conventions": ("VCF Content Factory conventions", "TOOLSET GAP"),
    "vcfops-sdk-adapter": ("Tier 2 Java SDK adapter", "pak-compare"),
    "vcfops-supermetric-dsl": ("VCF Operations super metric DSL", "verified"),
}
CODEX_ONLY = {
    "vcfops-orchestration",
    "vcfops-preflight",
    "vcfops-validation",
    "vcfops-bundle",
    "vcfops-extract",
    "vcfops-release",
    "vcfops-publish",
}


def skill_text(root: Path, name: str) -> str:
    path = root / name / "SKILL.md"
    if not path.is_file():
        raise ValueError(f"missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    claude_root = ROOT / ".claude" / "skills"
    codex_root = ROOT / ".agents" / "skills"
    failures: list[str] = []
    for name, required in PAIRS.items():
        try:
            claude = skill_text(claude_root, name)
            codex = skill_text(codex_root, name)
        except ValueError as exc:
            failures.append(str(exc))
            continue
        if f"name: {name}" not in claude or f"name: {name}" not in codex:
            failures.append(f"{name}: missing matching name front matter")
        for phrase in required:
            if phrase not in codex:
                failures.append(f"{name}: Codex skill missing required contract: {phrase!r}")
    for name in CODEX_ONLY:
        try:
            skill_text(codex_root, name)
        except ValueError as exc:
            failures.append(str(exc))
    unexpected = sorted(
        path.parent.name
        for path in codex_root.glob("*/SKILL.md")
        if path.parent.name not in PAIRS and path.parent.name not in CODEX_ONLY
    )
    if unexpected:
        failures.append(f"unregistered Codex skill(s): {', '.join(unexpected)}")
    if failures:
        print("Codex skill parity: FAIL", file=sys.stderr)
        print("\n".join(f"- {failure}" for failure in failures), file=sys.stderr)
        return 1
    print(f"Codex skill parity: PASS ({len(PAIRS)} paired, {len(CODEX_ONLY)} Codex-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
