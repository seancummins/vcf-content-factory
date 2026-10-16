# E3.4 — Independent read-only LUN identity probe review

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT findings.**
Adapted `framework-reviewer` contract, independent from the probe author.
Review date: 2026-10-15. Factory base: `f53bb603e0b112e4febe9acc09cb4d2c6b1f7315`;
review covers the uncommitted E3.4 work, not an approved release artifact.

## Scope and authorities

- `scripts/rdm_lun_identity.py`, E3.4 changes in `scripts/rdm_lab_probe.py`,
  `tests/test_rdm_lun_identity.py`, and the
  [qualification procedure](../../../designs/managementpacks/vsphere-rdm-topology-e34-identity-qualification.md).
- [Approved E3.3 architecture](../../../designs/managementpacks/vsphere-rdm-topology-e33-canonical-lun.md),
  [API identity evidence](../../api-maps/vsphere-canonical-lun-identity.md),
  RULE-001/002/008/016, the reviewer doctrine, and the existing read-only probe contracts.
- No live calls, credential-value inspection, raw lab files, adapter changes,
  PAK builds, installation, commits or pushes were used for this review.

## Independently verified behavior

The current-host RDM backing UUID joins exactly one SCSI LUN; another host's
match does not establish current-host visibility. Selected additional hosts are
explicit and bounded. Unreadable, missing or ambiguous data and changing VM
snapshots fail closed. Duplicate PropertyCollector objects/property names and
unexpected objects are rejected rather than silently overwriting evidence.

The decoder distinguishes opaque SCSI UUID, canonical name and independently
decoded designator bytes. It validates descriptor length/header/code set/type/
LU association and supports only complete NAA5/6 payloads. NamespaceId is
preserved as a byte, not interpreted as designator type. Signed byte conversion
preserves bits/order. Only strict hexadecimal prefix/case presentation differences
are accepted; UUID slicing, substring joins, padding and guessed conversions are absent.
Well-formed port/target designators are excluded, never mistaken for LU identity;
malformed NAA claims or multiple distinct eligible identities cannot qualify.

Cross-host equivalence requires actually captured hosts and equal qualified
payloads. UUID differences are not normalized or substituted. Capacity/vendor/
model/type contradictions block qualification. Capacity arithmetic is positive
and bounded; absent descriptive fields remain unknown. Cross-vCenter equivalence
and temporal stability are explicitly untested, not inferred from key syntax.

Raw evidence and the operator reference remain optional/required local ignored
owner-only files respectively; no storage-side value is embedded in code/tests/
documentation. Exclusive mode-0600 creation, no overwrite/symlink acceptance,
serialization-failure cleanup and cleanup after a subsequent write failure are
tested. CLI exception payloads, library output and warning/log paths are suppressed;
terminal output contains sanitized structural facts, booleans and fingerprints.
The default offline mode and double live-access acknowledgement remain intact;
the identity mode rejects non-development profiles before SOAP access.

## Independent checks

| Check | Result |
|---|---|
| Six RDM Python suites, final source | **262 passed, 5 skipped**; skips require unavailable SDK/Java-parser prerequisites in the review invocation. |
| Complete factory suite, earlier same-session snapshot | **2,396 passed, 19 skipped, 131 deselected, 1 failed**. The single failure is `tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`; independently reproduced alone. Relevant common setup source/test are untouched by E3.4. Final added identity tests were rerun in the focused suite above. |
| Changed-document validation and complete content validation | PASS, exit 0. |
| Codex skill parity | PASS: 5 paired, 7 Codex-only. |
| Path-reference audit | PASS, exit 0; six standing local-only-reference warnings, no dead references in scanned corpus. |
| `git diff --check` | PASS. |
| `.claude/`, `reference/`, adapter source diff | No E3.4 modifications. |

No renderer/build/package comparison is applicable: this increment adds a
read-only evidence probe, not installable content or adapter behavior.

## Disposition and remaining empirical boundary

**If shipped as-is:** an operator can explicitly capture the exact RDM/LUN
identity chain and obtain a sanitized, fail-closed qualification assessment,
without creating or changing VMware/Operations resources. Existing modes retain
their defaults; malformed/duplicate PropertyCollector results are now rejected.

This approval verifies offline implementation and documentation, **not live LU
identity qualification**. Actual evidence remains **BLOCKED pending operator
execution**. A successful narrow chain can justify **CONDITIONALLY QUALIFIED**
for a limited lab POC; it cannot establish collision-free global assignment,
cross-vCenter equivalence, longitudinal stability or deployed CanonicalLun topology.
The operator-supplied storage reference is not independently acquired array evidence.
