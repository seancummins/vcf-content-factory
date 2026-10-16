# E3.5 — Independent offline fixture-helper review

**Verdict: APPROVE — zero BLOCKING, WARNING or NIT findings.**

Scope: new `scripts/rdm_prepare_canonical_fixture.py` and
`tests/test_rdm_canonical_fixture.py`; only the E3.5 supporting changes to
`scripts/rdm_lab_probe.py`: explicit `CanonicalLunIdentity` compilation dependency
in `_fixture_validator`, and optional bounded input size in `_lun_local_path`.
Earlier E3.2/E3.4 worktree changes are not newly approved by this review.
Independent Java adapter/relationship review is a separate gate.

## Verified behavior

- The helper has no VMware/array API access. It consumes ignored, untracked,
  owner-owned mode-0600 files directly under mode-0700 local scratch; default
  probe input limit remains 8192 bytes. Explicit larger offline inputs remain
  capped at 1 MiB.
- It reuses the E3.4.1 descriptor analyzer, requires conditional qualification,
  checks exact mapping vCenter/VM-instance/disk-key equality and VM MOID evidence,
  and retains the complete supplied VMware ResourceKey and uniqueness flags.
  It does not reconstruct identifiers from fingerprints.
- LU-associated descriptor proof and exact canonical/storage-reference agreement
  precede fixture projection. Conflicting identities are rejected, not hidden by
  selecting one descriptor. Only existing approved signed-byte/hex presentation
  handling is used.
- The actual Java RuntimeFixture parser validates the complete projected v2
  fixture over stdin before output creation. It remains the final gate for
  foreign-key type/uniqueness/scope and descriptor/schema validation; this helper
  alone is not an alternative fixture validator.
- Duplicate JSON members fail closed. Errors expose static stage labels only;
  inventory payloads, Java diagnostics and arbitrary exception messages do not
  reach terminal output. No real private evidence was read for this review.
- Output uses the existing exclusive mode-0600 writer with no overwrite or
  symlink acceptance; inherited writer tests exercise partial serialization
  cleanup. Java validation failure produces no output fixture.

Authorities: RULE-001/002 (verified SDK/schema rather than invented APIs),
RULE-007 (stable identity), RULE-008 (sanitized failures), RULE-005 (independent
validation); E3.3 identity policy and E3.4.1 qualification limits. The helper
does not touch framework renderers/builders, immutable references, release CI,
adapter scheduling or installed topology.

## Independently rerun evidence

| Check | Result |
|---|---|
| New helper suite, with explicitly supplied legitimate local SDK | 14 passed, including actual Java legacy/v2 parser acceptance |
| Seven RDM probe/helper suites, SDK enabled | 319 passed / 1 protective skip |
| Six additional synthetic final-gate adversarial cases | All rejected: wrong uniqueness, foreign-vCenter conflict, empty unique value, duplicate identifier, wrong adapter, null nonunique value |
| Full factory suite, normal environment | 2463 passed / 20 skipped / 131 deselected / 1 failed |
| Isolated setup suite | 88 passed / the same one failed |
| Full content validation chain | Passed |
| Codex skill parity | Passed: 5 paired / 7 Codex-only |
| Path-reference audit | Clear; six documented standing warnings |
| Diff whitespace check | Passed |

The full-suite failure is the previously documented, unchanged
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
the implementation reports inability to determine ignore status, while the test
expects the old reassuring not-a-repository message. No fix was made outside
scope. Normal full-suite execution did not opt into the local SDK; the targeted
SDK-enabled run separately exercised actual parser compilation.

If shipped as-is: an operator can prepare one exact-key qualified v2 attachment
offline in a restrictive local file, or receive a sanitized failure without a
success claim. This approval does not prove live local-edge persistence,
multi-host/cross-vCenter equivalence, or production/global deduplication.
No live requests, real fixture generation, adapter edits, PAK builds, installs,
commits or pushes were performed by this reviewer.
