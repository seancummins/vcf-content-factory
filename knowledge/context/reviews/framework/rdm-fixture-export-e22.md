# E2.2 — independent secure fixture-export review

Verdict: **APPROVE — zero implementation BLOCKING findings.** This approves
the offline-reviewed exporter, not a generated real fixture or a live
installation. If shipped as-is, the exporter either validates one exact scoped
VM/RDM fixture and writes its fixed private handoff, or fails without claiming
success. Actual capture remains **BLOCKED** by unavailable designated credentials
reported by the orchestrator; the reviewer accessed neither credentials nor raw
lab artifacts and made no live calls.

## Scope and authority

Reviewed `scripts/rdm_lab_probe.py`, `scripts/RdmFixtureValidate.java` and
`tests/test_rdm_fixture_export.py`, against the actual independent adapter
`RuntimeFixture`/`ForeignVmIdentity`/`RdmMappingIdentity` sources and the
[E2.1 configuration contract](../../../designs/managementpacks/vsphere-rdm-topology-e21-runtime-fixture.md).
Authorities: RULE-001 repository evidence, RULE-005 validation, RULE-008
diagnostic/credential confidentiality; lessons
`stitch-moid-not-unique-across-vcenters.md`,
`cross-mp-foreign-key-uniqueness-flags.md` and
`unenumerated-exit-status-is-not-a-verdict.md`. No adapter, framework, comparator,
release policy, immutable vendor material or existing reporting mode was changed.

## Verified controls

- Both explicit live acknowledgements remain required. Export is a separate
  development-profile mode, restricted to `vm-71`, rejecting alternate report or
  handoff destinations. It does not depend on VIM JSON or request collection,
  adapter installation, resource mutation or connection validation.
- SOAP reads the actual service-instance UUID, VM instance UUID and typed RDM
  disk key. Missing properties, changed VM configuration/instance/host snapshots,
  invalid disk keys, absent LUN identity and zero/multiple RDMs fail closed.
- Complete paginated VMWARE/VirtualMachine inventory is inspected in memory.
  Selection requires exactly one exact VMEntityObjectID + VMEntityVCID pair,
  both explicitly uniqueness-bearing. Duplicate resources, duplicate identifier
  names, missing flags, malformed responses or ambiguous matches fail closed.
  Same MOID on another vCenter and duplicate display names do not prove identity.
- Every identifier entry, name, value and boolean flag is retained without
  normalization. Nonidentity API metadata such as links is deliberately projected
  away to fit the parser's exact object shape; no identifier is dropped.
  The official `reference/docs/operations-api.json` resource-key,
  resource-identifier and resource-identifier-type schemas support this
  distinction. Omitted uniqueness flags are rejected, not guessed.
- The actual E2.1 Java parser is compiled locally without copying the proprietary
  SDK. Fixture bytes travel only through subprocess stdin; diagnostics are
  captured, and a fixed `VALID` response is required before writing. Tests prove
  acceptance and conflicting-scope/noncanonical-disk rejection using that parser.
- Output is fixed to local scratch. Explicit Git-ignore and untracked checks fail
  closed on unexpected statuses. Owner-owned mode-0700 directory, directory-FD
  anchoring, O_EXCL/O_NOFOLLOW creation, mode 0600, fsync/readback verification,
  no overwrite and inode-checked failure cleanup protect the handoff.
- The export path suppresses third-party logging/stdout/stderr/warnings and emits
  only a generic failure or non-sensitive success summary. No raw payload appears
  in argv, test fixtures, reports or reviewer output. Authentication token release
  and SOAP disconnect remain best-effort cleanup, not inventory mutations.

## Independent execution

- Existing probe plus export tests: **55 passed**, with an explicit legitimately
  available local SDK path, including actual Java-parser validation.
- Full factory suite: **2203 passed / 15 skipped / 131 deselected / 1 failed**.
  The sole failure is unchanged
  `tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
  this environment has an existing `/tmp/.git` ancestor, so the implementation
  correctly reports unknown rather than the test's assumed no-repository state.
  Neither that source nor test changed; no destructive environment workaround
  was attempted. The optional Java test skipped in this full run without its SDK
  environment setting, but passed in the explicit-SDK focused run above.
- Full changed-content validation chain: **exit 0**.
- Skill parity: **PASS** (5 paired / 7 Codex-only).
- Path-reference audit: **clear**, six existing documented standing warnings.
- Diff whitespace validation: **clean**.

Render regression and PAK comparison are not applicable: no renderer, adapter
source, descriptor, package or comparison policy changed. No actual fixture,
connectivity, API response or live identity was validated by this review.

Reviewed probe SHA-256:
`13d66120a80cd8d72b7e9c99aeb5b23cb96f9f4a60e262bf9ed78833ac39f7e1`.
Final export-only SOAP/Operations 30-second request timeouts were inspected;
the focused 55 tests independently passed again after this change.
No commits, staging, pushes, deployments or live operations were performed.
