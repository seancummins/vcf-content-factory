# F0.5 — independent framework comparator implementation review

Date: 2026-10-14. Reviewer: `framework-reviewer`, independent Codex context.
Factory base revision: `95cc4b7df575f704fed4ee965e807c91edf621e0`.
Scope: the uncommitted comparator, factory CLI, generated buildkit CLI,
automatic SDK gate, verification script, documentation and synthetic tests.
Review writes were confined to this report; no implementation was edited by
the reviewer.

## Verdict

**APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT implementation findings.**
The approved F0.4 policy is implemented without adapter-specific exceptions,
finding suppression, a RULE-005 change or a change to default legacy results.
The full factory suite is **not green** in this environment: its unrelated
failure and backend error are recorded below, with independent baseline
evidence. Approval applies to this implementation's correctness and
regression evidence; it does not claim those environment checks passed.

If shipped as-is, existing callers retain legacy findings and exit behavior;
explicit new policies validate each credential contract before accepting
schema-valid optional differences. The exact development POC passes its local
structural comparison. **GO for release-infrastructure preparation**, subject
to recording the remaining test-environment limitations; **NO-GO for release
or deployment** until E1.5's CI, official-artifact and approval prerequisites
are satisfied.

## Independent inspection and schema evidence

I read the authoritative framework reviewer contract, shared reviewer
doctrine, rules, lessons, approved F0.4 design/review, F0.1 selection record
and F0.2/F0.3 evidence. I inspected every changed framework Python file in its
caller context and searched all source, scripts and tests for comparator and
SDK-builder callers. The global-default and key-collision escape anchors
`00d3382` and `6c59f6b` informed the compatibility review. No dashboard/view
renderer, template or assembly implementation changed; their render
regression coverage ran as part of the full suite.

The durable schema authority is
`knowledge/context/cleanroom-spec/spec/02a-describe-xsd-canonical.md` and the
credential model digest. Direct read-only inspection of the locally available
legacy XSD corroborated: credential-kind key/nameKey and field
key/nameKey/dispOrder are required; field type is optional; boolean omission
has a default only where documented; enum field children are legitimate.
That supporting XSD is local-only and not reproducible from a factory clone;
its relevant findings are summarized here in full. The validator correctly
labels explicit-false/no-binding and empty-container rules as factory policy,
rather than attributing those cross-field constraints to XSD grammar.

| Surface | Independently checked result |
|---|---|
| Default behavior | Loaded the comparator from factory `HEAD` directly and compared its actual POC/Synology results with the changed module: identical finding codes, messages, severities, ordering and formatted report. Default remains `legacy`. |
| Contract validator | Each side is independently checked; malformed references cannot qualify a candidate. XML booleans use XML whitespace, raw string keys retain identity, valid integer lexical type-7 forms normalize correctly, requiredness omission is effective true only where documented, and no credential values/defaults enter reports. |
| Package eligibility | Single native Java descriptor, matching manifest/directory/descriptor identity and matching type-7 kind are required. Duplicate members, ambiguity, unsupported families/namespaces and malformed inputs fail closed. Native Java assets named after Docker do not trigger a family rejection. |
| Upgrade policy | Same adapter identity is mandatory. Removal/rename, type changes, new required fields, increased requiredness and masking loss block, including equal-count changes. Optional field addition retains the existing warning. |
| Structural policy | Different identities and one exact digest-pinned reference are mandatory. Valid D1/D2/D6 differences remain visible as INFO with contract evidence. Other comparison rules remain active. Directory selection and digest mismatch fail. |
| Entry points | Factory API/CLI, copied isolated buildkit CLI, copied buildkit automatic gate, factory build dispatch and release gate propagate the explicit policy/reference/digest. Unknown policies and absent references cannot skip new-policy evaluation. Release warn-only is rejected; failed release artifacts are removed by the existing gate. |
| Scope | No RDM adapter, approved PAK, `.claude/`, immutable reference, renderer or RULE-005 change is included. No SDK binary or secret was added. |

Review identified and returned three intermediate issues to tooling: broad
Docker filename rejection, lexical integer type recognition and trimming of
string declaration keys. Tooling corrected them and added deterministic
regressions before this verdict. The reviewer independently reproduced the
initial failures and inspected the final corrections without editing them.

## Tests and validation independently rerun

```text
PYTHONPATH=src .venv/bin/python -m pytest tests/managementpacks/test_pak_compare.py tests/managementpacks/test_pak_compare_gate.py tests/managementpacks/test_pak_compare_policy.py -q --tb=short --override-ini='addopts=' -m '' -p no:warnings
129 passed, 3 skipped
```

These cover credentialed/no-auth comparisons in both directions, default-true
and explicit-false requiredness, optional authentication, multiple kinds,
dangling/empty/duplicate bindings, malformed declarations, namespaced XML,
upgrade regressions, unsupported/ambiguous/duplicate archives, digest and
policy errors, legacy gate behavior and isolated buildkit propagation. The
isolated buildkit automatic gate also rejects a malformed reference.

```text
PYTHONPATH=src .venv/bin/python -m pytest tests/ -q --tb=short --override-ini='addopts=' -m ''
1 failed, 2298 passed, 14 skipped, 333 warnings, 1 error in 125.24s
```

The two nonpassing checks are outside this increment's changed paths:

- `tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`
  assumes the temporary directory has no Git ancestor. This environment has
  `/tmp/.git`, so the unchanged implementation correctly reports unknown.
  A targeted rerun reproduced the failure. Loading `HEAD`'s
  `setup_credentials.py` independently reproduced exactly the same verdict
  as the working-tree module with Git exit 128; this is not an F0.5 regression.
- `tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path`
  errors in its wheel-build fixture: isolated pip build requires
  `setuptools>=64`, and the restricted network cannot fetch it. The local
  virtual environment has neither setuptools nor wheel installed. No
  dependency was installed or downloaded, no network retry was authorized,
  and this backend-dependent check remains unverified.

`scripts/validate-changed-content.sh --all` passed.
`scripts/path_reference_audit.sh` passed with only its documented TVS and
downstream `defects.local.md` standing-exception warnings. `git diff --check`
and `bash -n scripts/verify-tier2-sdk.sh` passed. These successes do not erase
the full-suite limitations above.

## Actual immutable-artifact comparisons

Both SHA-256s were independently verified before the public CLI runs:

| Artifact | SHA-256 |
|---|---|
| RDM POC `vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak` | `5354acc09b4afa5a2fad5aed9429adebd8fe0f0e751b0b64b909c59854381d61` |
| Approved Synology `vcfcf_sdk_synology_diskstation.1.0.0.30.pak` | `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1` |

Synology provenance is the approved official
[v1.0.0.30 release](https://github.com/sentania-labs/vcf-content-factory-sdk-synology/releases/tag/v1.0.0.30)
and `knowledge/context/reviews/rdm-topology-poc-f01-reference-selection-review.md`.
The POC is a local-only development artifact, not reproducible from the
factory checkout alone; required findings are summarized here and fully
recorded in `knowledge/context/reviews/rdm-topology-poc-f05-comparator-results.md`.
Neither artifact was built or modified by this reviewer.

| Public CLI invocation | Actual findings | Exit |
|---|---|---|
| No policy flag | 2 BLOCKING / 3 WARNING / 20 INFO | 1 |
| Explicit `--policy structural --reference-sha256` with the digest above | 0 BLOCKING / 3 WARNING / 22 INFO | 0 |

Legacy D1/D6 remain BLOCKING. In the new explicit structural report they are
INFO after both independent contracts pass. All prior twenty INFO findings
and warnings D8 (instance identifier count), D23 (traversal count) and D25
(empty/populated traversal difference) remain visible. No finding was manually
suppressed or waived.

RULE-005's exact-artifact local structural comparison sub-check is satisfied.
Its future automatic CI comparison must use the same explicit reviewed
policy/reference/digest against the actual CI artifact. This local pass does
not promote the `0.x` POC, satisfy all pre-install checks, establish appliance
acceptance or relationship persistence, or authorize publication/deployment.
