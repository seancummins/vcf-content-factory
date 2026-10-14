---
name: vcfops-sdk-adapter
description: Use when planning, writing, reviewing, or validating a Tier 2 Java SDK VCF Operations management-pack adapter, its describe.xml, or its pak build.
---

# Tier 2 Java SDK adapter

Read `knowledge/context/tier2_architecture.md`, the Tier 2 cleanroom handoff,
and relevant lessons before work. A Tier 2 adapter is an independent repository
under `content/sdk-adapters/`; do not treat it as factory Python code.

Use the cheap local loop before any install request:

```bash
scripts/verify-tier2-sdk.sh content/sdk-adapters/<adapter> <reference-pak-dir>
```

This runs `validate-sdk`, `build-sdk`, and `pak-compare`; zero BLOCKING
findings are the install gate. Respect classloader isolation, use stable
cross-vCenter identity for stitching, and treat unreadable data as unknown,
not compliant. Never install or contact vCenter without explicit approval.

The complete Claude-compatible playbook remains at
`.claude/skills/vcfops-sdk-adapter/SKILL.md`; parity is checked by
`scripts/check_skill_parity.py`.
