# Codex orchestration and boundary model

Codex support is additive. Claude Code continues to use .claude/agents/,
.claude/skills/, .claude/commands/, and .claude/settings.json unchanged.
Codex uses AGENTS.md plus the independent .agents/skills/ skills.

## Delegation

When the selected Codex runtime exposes subagent collaboration, the
orchestrator delegates bounded role work to an independent subagent. The
subagent receives the relevant .claude/agents/<role>.md contract, a precise
task, and the allowed write paths. This is independent execution and separate
context, not merely a prompt section in the coordinator's context.

Use delegation for independent research and review. Keep authoring serial when
objects depend on each other's identifiers or names. A reviewer must remain
read-only and independently reproduce validation evidence.

## Boundary status

| Boundary | Status | Backstop |
|---|---|---|
| Repository write permission | Technically enforced by the execution sandbox | Workspace policy |
| Immutable reference/** | CI-enforced for modifications/deletions; instruction-enforced locally | scripts/immutability_guard.sh, CI |
| Role-specific write path | Instruction-enforced | Role prompts, review, changed-file inspection |
| Role-specific tool access | Runtime-dependent; not encoded by repository skills | Sandbox/tool policy and explicit approval |
| Live VMware/install/publish | Approval-enforced in the active runtime and instructions | Explicit user confirmation, CLI boundaries |
| Content syntax/cross references | Deterministically enforced | validate-changed-content.sh, full validators, CI |
| Framework and SDK review | Governance-enforced with recorded evidence | Reviewer report, CI reminder, human review |

Codex subagents can share a filesystem and inherited tools. They are not
separate filesystem sandboxes solely because they have separate contexts. Do
not claim stronger isolation than the runtime actually provides.

## Supported execution shapes

- Interactive Codex clients may expose collaboration tools directly.
- Agents API / Responses multi-agent can create independent subagents, but
  they inherit configured tools and share an attached environment.
- This repository does not add an API client, MCP server, or custom agent
  runtime in Increment A. Those would introduce credentials and deployment
  policy beyond this foundation.

## Hook replacement

Codex foundation does not depend on lifecycle hooks. The explicit,
deterministic replacements are:

| Claude behavior | Codex foundation |
|---|---|
| SessionStart bootstrap + doctor | scripts/codex-preflight.sh; bootstrap is opt-in |
| PostToolUse content validation | scripts/validate-changed-content.sh <path> |
| Session curation reminder | manual/CI-invoked scripts/curation_staleness_check.sh |

Optional trusted Codex plugin hooks may be evaluated later, but they cannot be
the sole enforcement point because availability and trust are client-specific.
