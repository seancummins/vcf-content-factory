---
name: vcfops-orchestration
description: Coordinate VCF Content Factory work across specialized roles, write boundaries, review gates, validation, and explicit approval checkpoints.
---

# VCF Content Factory orchestration

Read the role prompt under `.claude/agents/<role>.md` before assigning that
role. It remains authoritative for responsibilities, inputs, output, and write scope.

Use independent Codex subagents when the runtime offers delegation and the
work has a bounded, separable mandate. Give each subagent a single role, exact
write paths, and no authority to install, publish, or access a live system.
Keep dependent authors serial. Reviewers are independent/read-only and must
re-run evidence rather than repeat author claims.

Technical boundary status is documented in `knowledge/context/codex_orchestration.md`.
Shared filesystem and inherited tools mean role isolation is not a runtime
sandbox; deterministic validators, CI, approval gates, and reviewer reports
are mandatory backstops.
