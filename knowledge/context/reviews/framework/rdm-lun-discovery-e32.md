# E3.2 — independent read-only LUN-discovery review

**Verdict: APPROVE — zero BLOCKING, WARNING or NIT findings.** Approval covers
offline probe implementation, not native-LUN reuse or a live topology change.
Disposition remains **INSUFFICIENT EVIDENCE** pending operator execution.

Reviewed `scripts/rdm_lab_probe.py`, `scripts/rdm_lun_discovery.py`,
`tests/test_rdm_lun_discovery.py` and the
[operator procedure](../../../designs/managementpacks/vsphere-rdm-topology-e32-lun-discovery.md).
Review posture follows `.claude/agents/framework-reviewer.md` and
`knowledge/context/authoring/guide_reviewer_doctrine.md`; source remained
read-only to this reviewer. No credential values or raw lab artifacts were read,
and no live calls, adapter changes, builds, commits or pushes were performed.

## Independently verified

- Public GET census, resource-detail and direct property response shapes agree
  with `reference/docs/operations-api.json`. Caller-visible populated kinds are
  distinguished from supported kinds and global inventory coverage.
- SOAP requires one RDM, an exact current-host `lunUuid`/`ScsiLun.uuid` join,
  nonempty canonical identity and unchanged VM instance/configuration/host
  snapshots. Other-host visibility cannot qualify the source join.
- Kind-name hints and arbitrary exact-value occurrences are discovery evidence
  only. REUSE requires explicit operator-backed field/granularity semantics,
  exact storage identity and vCenter scope, one target, and a representable
  complete ResourceKey. UUID/canonical conflicts, competing unqualified matches,
  incomplete keys/properties and multiple matches fail closed.
- Complete keys preserve identifier ordering, values and flags; nonunique
  explicit empty strings survive, while null/omitted values and SDK-case-insensitive
  duplicate names block qualification. This follows the
  [SDK value contract](../../../designs/managementpacks/vsphere-rdm-topology-e22-empty-identifiers.md)
  and `knowledge/lessons/cross-mp-foreign-key-uniqueness-flags.md`.
- Existing modes retain their behavior; LUN capture is explicit and development
  profile only. Library/exception output is suppressed; diagnostics use fixed
  codes. Reports exclude raw identities. Optional private evidence and qualified
  handoff require ignored, untracked, owner-only scratch paths and exclusive
  `0600` creation; tested output failures remove newly created evidence.
- Collection uses reads only, apart from existing authentication acquire/release.
  Token cleanup does not obscure the primary result. No adapter or topology
  implementation was changed.

Two preliminary concerns were resolved before approval: competing unqualified
exact-value candidates now prevent false REUSE, and explicit secure candidate
evidence makes observed field names available without printing them or inventing
bindings. No findings were waived or reclassified.

## Independent checks

- Five probe suites with the legitimate local SDK supplied: **191 passed,
  1 skipped**. The skip protects an existing operator output file from testing.
  This includes **42** new discovery tests and actual existing Java-parser tests.
- The orchestrator's full-suite run was not wholly green: one unrelated failure
  in `tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`.
  Independently reproduced alone: **1 failed**, returning the conservative
  unknown Git-ignore verdict instead of the expected not-a-repository verdict.
  The setup implementation and its test are unchanged by this increment; no
  environmental cause is asserted as proven and no unrelated correction made.
- Full content validation (`scripts/validate-changed-content.sh --all`): PASS.
- Skill parity: PASS (5 paired, 7 Codex-only).
- Path-reference audit: PASS; six documented standing-exception warnings only.
- `git diff --check`: PASS.

## Limits and next decision

No live resource kinds, candidate counts or LUN endpoint were established here.
Inventory reads are bounded, permission-filtered and not an atomic platform
snapshot. Opaque kind names may require a subsequently documented explicit
binding. Operator assertions of physical-LUN semantics must be supported by
observed metadata/authoritative adapter documentation; the code cannot prove
those assertions. Array-only/global storage scope is deliberately unsupported,
not guessed. A missing or ambiguous endpoint remains INSUFFICIENT EVIDENCE,
never automatic justification for CanonicalLun.

If shipped as-is, the operator can securely gather candidate evidence and test
an explicit scoped interpretation without changing Operations inventory. Any
future foreign-child relationship still needs separate implementation approval
and deployed persistence verification; E2's existing VM-parent edge is preserved.
