---
name: vcfops-preflight
description: Inspect local VCF Content Factory readiness before work, without automatically installing dependencies, cloning remotes, or accessing VMware systems.
---

# Codex preflight

Run `scripts/codex-preflight.sh`. It reports Python, dependency, local
bootstrap, and credential readiness by exception and does not expose secret
values. It does not install anything or contact VMware. Run
`scripts/codex-preflight.sh --bootstrap` only after the user explicitly
approves registered Git-remote bootstrap activity.
