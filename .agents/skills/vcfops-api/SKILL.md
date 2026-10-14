---
name: vcfops-api
description: Use when planning, implementing, or troubleshooting VCF Operations Suite API access, content import/export, authentication, or wire-format behavior.
---

# VCF Operations API

Use only repository-backed API evidence. Check both public and internal API
specifications before asserting capability. Credentials stay in profile
environment variables and must never appear in source, shell arguments, or transcripts.

For content import/export and live operations: validate first, preserve UUID
contracts, verify server results rather than assuming a successful HTTP task
means content materialized, and require explicit user approval before any live
access. Internal endpoints are unsupported and must be identified as such.

Read `knowledge/context/api-surface/`, `knowledge/context/wire-formats/`, and
the immutable vendor sources relevant to the request. The complete
Claude-compatible skill is `.claude/skills/vcfops-api/SKILL.md`; parity is
checked by `scripts/check_skill_parity.py`.
