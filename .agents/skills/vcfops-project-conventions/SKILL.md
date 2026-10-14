---
name: vcfops-project-conventions
description: Apply VCF Content Factory naming, provenance, recon, cross-reference, and validation conventions when authoring or reviewing repository content.
---

# VCF Content Factory conventions

Read `knowledge/rules/INDEX.md`, `knowledge/lessons/INDEX.md`, and
`knowledge/context/README.md` before authoring. Rules override all other guidance.

- Content names use `[VCF Content Factory] `; management-pack display names
  use `VCF Content Factory ` without brackets.
- Ground all metric/property/attribute/API names in repository evidence,
  vendor material, or explicitly supplied user data. Never guess.
- Recon and reuse precede new content. Capture approved intent in the relevant
  `knowledge/designs/` artifact before authoring.
- Keep UUIDs stable and use names—not hand-written identifiers—for content
  cross references.
- Report any unsupported requirement as a `TOOLSET GAP`; never silently downgrade.

Run the seven-package validation chain after an authoring round:

```bash
python3 -m vcfcf_supermetrics validate &&
python3 -m vcfcf_dashboards validate &&
python3 -m vcfcf_customgroups validate &&
python3 -m vcfcf_symptoms validate &&
python3 -m vcfcf_alerts validate &&
python3 -m vcfcf_reports validate &&
python3 -m vcfcf_managementpacks validate
```

For the complete Claude-compatible convention text, compare with
`.claude/skills/vcfops-project-conventions/SKILL.md`; parity is checked by
`scripts/check_skill_parity.py`.
