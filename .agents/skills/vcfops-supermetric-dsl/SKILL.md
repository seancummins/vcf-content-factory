---
name: vcfops-supermetric-dsl
description: Use when designing, authoring, reviewing, or debugging VCF Operations super metric formulas and their resource-kind bindings.
---

# VCF Operations super metric DSL

Use only verified metric/property keys and established formula grammar. Confirm
the metric exists and is usable before authoring; never substitute an inferred
key. Preserve the super-metric UUID contract and validate formula references
against the complete content corpus.

Read `knowledge/context/authoring/supermetric_authoring.md` and existing
supermetrics for grammar and conventions. The complete Claude-compatible skill
is `.claude/skills/vcfops-supermetric-dsl/SKILL.md`; parity is checked by
`scripts/check_skill_parity.py`.
