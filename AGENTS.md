
# VCF Content Factory — Codex Instructions

This is a VCF Operations content-authoring framework. Codex support is
additive: `.claude/` remains the Claude Code implementation and must not be
removed, renamed, or weakened.

## Non-negotiable governance

- Read `knowledge/rules/INDEX.md` before work; its rules are absolute.
- Consult `knowledge/lessons/INDEX.md` before taking a seemingly obvious path.
- Use `knowledge/HOW_IT_WORKS.md` for architecture and `STRUCTURE.md` for
  ownership and mutability.
- Never invent endpoints, metric keys, attributes, resource identifiers, or
  vendor behavior.
- Never edit `reference/**`; it is immutable vendor material.
- Never expose credentials in files, commands, output, or chat.
- Never access a live VMware environment, install a management pack, publish,
  push, or perform a destructive action without the user's explicit approval.

## Codex workflow

- Use the relevant `.agents/skills/` skill before acting in its domain.
- Run `scripts/codex-preflight.sh` for session/setup work. It is read-only;
  `--bootstrap` is explicit and may access registered Git remotes.
- After content changes, run `scripts/validate-changed-content.sh <path>`;
  before an install or release gate, run the complete validation chain.
- `.claude/agents/<role>.md` remains the authoritative role contract. When
  delegating, use an independent subagent if the Codex runtime exposes one;
  give it the role prompt, exact task, and permitted write paths. Do not run
  content authors in parallel when their cross-references can race.
- Codex subagents share the workspace and inherited tools. Role write scopes
  are therefore governance instructions plus review/CI evidence, not a
  filesystem sandbox. See `knowledge/context/codex_orchestration.md`.
- `src/vcfcf_*/` remains tooling-only and requires the framework-reviewer gate.
  Tier 2 Java adapter changes require the sdk-adapter-reviewer gate.

## Tier 2 routing

For a Tier 2 Java SDK management pack, use `vcfops-sdk-adapter` and follow:

`api-cartographer → mp-designer → approved design → sdk-adapter-author →
validate-sdk → build-sdk → sdk-adapter-reviewer → pak-compare → explicit
install approval`.

Tier 2 adapter repositories under `content/sdk-adapters/` are independent,
gitignored repositories. Do not create or modify one unless that work is
explicitly requested.
