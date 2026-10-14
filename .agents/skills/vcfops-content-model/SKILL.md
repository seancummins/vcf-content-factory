---
name: vcfops-content-model
description: Use when planning, authoring, or reviewing VCF Operations super metrics, views, dashboards, groups, symptoms, alerts, reports, and their dependencies.
---

# VCF Operations content model

Model dependencies before writing: super metric → view → dashboard; symptom
→ alert; view/dashboard → report. Stable UUID-bearing types retain their YAML
`id`; server-assigned types resolve by exact name. Author bottom-up and
serially where references depend on prior objects.

Read `knowledge/context/authoring/uuids_and_cross_references.md` and the
relevant content authoring guide. Dashboard work additionally requires the
RULE-011 wireframe, HTML mock, and plan-mode approval gate.

The complete Claude-compatible skill remains at
`.claude/skills/vcfops-content-model/SKILL.md`; parity is checked by
`scripts/check_skill_parity.py`.
