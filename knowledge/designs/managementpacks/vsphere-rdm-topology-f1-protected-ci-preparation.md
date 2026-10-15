# F1 — RDM topology repository and protected CI preparation

Date: 2026-10-15. Scope: local preparation, offline validation and independent
review only. This record grants no authority to create a remote, push, tag,
provision a runner, publish or deploy.

## Audited repository and release conventions

| Item | Audited state / convention |
|---|---|
| Factory | `feature/rdm-topology-mp`, base `b4be5a9dbb60c949d35c6def59286edf50145113`, existing `origin`; clean at F1 start. |
| Independent POC | `content/sdk-adapters/rdm-topology-poc`, `main`, base `cb2292db90d5d0a8da530e9c187986307daf0d2b`; clean at F1 start, no remote. Its `.git` remains independent. |
| Canonical repository name | Proposed `sentania-labs/vcf-content-factory-sdk-rdm-topology-poc`, matching `knowledge/context/managed_paks.md`. |
| Visibility | Propose public source, consistent with existing Synology/UniFi adapter repositories. Requires owner approval; no proprietary SDK or customer inventory is part of that source. The release runner remains private and isolated regardless of repository visibility. |
| Development/release branches | Proposed protected `main` with reviewed feature branches/PRs; no tag from an unmerged branch. |
| Version contract | `adapter.yaml version` plus monotonic `build_number` must equal the full `v<major>.<minor>.<patch>.<build>` tag at its target commit. Release major must be at least 1. |
| Artifact | `vcfcf_sdk_rdm_topology_poc.<major>.<minor>.<patch>.<build>.pak` and `<pak>.sha256` in sha256sum format; official output is CI-built. |
| Comparator | Explicit `structural` policy with the approved exact Synology reference and digest in both the automatic build gate and reported direct comparison. |

Sources inspected: the locally registered Synology, UniFi and compliance
repositories' `.github/workflows/build-pak-on-tag.yml`, compliance's
`.github/workflows/tests.yml`, factory `.github/workflows/publish-buildkit.yml`,
`knowledge/lessons/sdk-paks-independent-repos.md`,
`knowledge/lessons/stacked-squash-merge-needs-retarget.md`, and the E1.5/F0.5
records. Registered adapter checkouts are fetchable through the existing
managed-pak registry; the RDM checkout remains local-only, not reproducible
from a factory clone alone. Its relevant state and contract are summarized
here; its future remote has not been created or registered.

The legacy templates use a floating `sdk-buildkit-v1`, retrieve the SDK from
a private Git runtime repository and grant release-workflow write access.
Those are not the approved E1.5 dependency strategy for this POC. F1 prepares
an isolated protected build with an externally provisioned SDK, exact tooling
pins and read-only repository access. Existing templates are left intact.

## Local CI preparation contract

The independent adapter repository carries the workflow, helper code,
deterministic tests, dependency/approval configuration and operator setup
instructions. The factory owns this audit/readiness record and independent
review. No submodule, flattened history or factory ownership of adapter files
is introduced.

The build path must enforce these controls before it can emit a candidate:

1. Exact repository allowlist, push-of-protected-tag context and strict 1.x+
   version/tag/artifact-name agreement. Tag target must be on protected main
   and equal the separately approved source SHA.
2. A protected release environment and dedicated ephemeral self-hosted runner
   group with access limited to the reviewed release workflow/repository.
   PR checks execute only on GitHub-hosted runners with no SDK or secrets.
3. Release enablement disabled until the administrator approves the runner,
   SDK checksum/provisioning and actual toolchain pins. Unset pins fail closed.
4. SDK file provisioned outside Git checkouts, build scratch and upload roots;
   resolve the real path, verify the approved SHA-256 before compilation and
   never copy it into a buildkit, cache, workspace, artifact or release.
5. Full published buildkit version and approved tarball SHA-256. It must
   contain the F0.5 comparator modes; a floating major tag, factory branch or
   unpublished local checkout is not the release toolchain.
6. The sanctioned vendored defect gate executes local reviewed code against
   current factory registry DATA. Record the registry digest. Missing/bad
   registry, blocking defect, failed test, failed compilation or comparator
   failure prevents artifact emission. A wrapper rejects empty/unrecognized
   downloads before the unchanged parser runs: the current header and retained
   DEF history are required. A legitimate future registry format change needs
   review rather than silently treating unrecognized data as no defects.
7. Exact Synology reference through the buildkit facility:
   `vcfcf_sdk_synology_diskstation.1.0.0.30.pak`, SHA-256
   `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.
   No reference substitution, directory scoring or warning-only gate.
8. Inspect the built PAK, preserve all comparator WARNING/INFO findings,
   verify SDK exclusion and emit only the named PAK, checksum and sanitized
   comparison/provenance evidence. No directory-wide upload or SDK path in
   evidence. Remove ephemeral build data after success/failure.

This is a reproducible-input/provenance contract: source, toolchain, SDK and
reference identities are recorded. Bit-identical cross-run output has not
been established; timestamped ZIP/JAR output and actual runner builds must be
assessed before claiming that stronger property. A local preview is never
promoted to an official release artifact.

Prepared adapter-local files (not factory-tracked files):

- `.github/workflows/check-source.yml`: no-SDK, no-secret hosted checks.
- `.github/workflows/build-pak-on-tag.yml`: protected candidate build only,
  `contents: read`, no release-publication step.
- `ci/release.py`, `ci/release-policy.json`, `ci/tests/test_release.py`:
  fail-closed orchestration, disabled approval configuration and offline tests.
- `ci/defect_gate.py`: hash-pinned vendored factory-managed CI convention.
- `ci/README.md`: administrator setup and operator verification procedure.
- `.gitignore`: excludes SDK JARs, local configuration and generated outputs;
  root `README.md` points operators to the protected-CI instructions.
- `scripts/run-tests.sh`: optional `VCFCF_FRAMEWORK_JAR` override so standalone
  CI uses the pinned buildkit framework, retaining the factory-local default.

The repository/org variable `RDM_RELEASE_ENABLED` gates job scheduling; it
cannot be supplied only as an environment-scoped variable. SDK path,
`RDM_RUNNER_APPROVED` and `RDM_APPROVED_SOURCE_SHA` are supplied by the protected
`rdm-release` environment. The reviewed policy file is a second enablement
gate. Both enablement gates remain disabled/unconfigured. CODEOWNERS is not
created with invented owners: selecting valid owner/team identities and adding
that file are explicit setup prerequisites.

## Proposed registry entry — inactive

The active `knowledge/context/managed_paks.md` is intentionally unchanged.
Only after repository creation is approved and completed should the
orchestrator add this SHA-free, version-free entry:

```markdown
### rdm-topology-poc

- **Remote:** https://github.com/sentania-labs/vcf-content-factory-sdk-rdm-topology-poc
- **Target:** `content/sdk-adapters/rdm-topology-poc/`
- **adapter_kind:** vcfcf_rdm_topology_poc
- **Owner:** sentania-labs. Public repository (subject to owner approval).
- **Notes:** Fixture-only Java SDK RdmMapping foreign-VM relationship POC;
  no live collection, no CanonicalLun, no approved deployment.
```

Adding the entry before the remote exists would violate the registry timing
rule. The quoted entry is a proposal and is not consumed by bootstrap.

## Minimum first-release metadata proposal

Current metadata remains `version: 0.1.0`, `build_number: 4`, `released: false`.
Propose `version: 1.0.0`, next build `5`, a matching changelog entry and
`v1.0.0.5` only after explicit release-owner approval. Expected first candidate
would then be `vcfcf_sdk_rdm_topology_poc.1.0.0.5.pak`. These are proposed
values, not an approved version, tag or produced artifact. Re-evaluate the
next build number if intervening development builds occur.

No Java collection or relationship behavior needs changing for this metadata
transition. The existing additive VM parent and credential-free type-7
descriptor remain the reviewed POC behavior. No `0.x` artifact may be tagged,
published or used as the permanent baseline.

## External configuration and release-readiness checklist

The following controls cannot be proved by local YAML or synthetic tests:

| Requirement | Current status / required owner evidence |
|---|---|
| Repository name/visibility and access | PROPOSED. Owner must approve creation, org/team ownership and admin access. |
| Main protection | UNCONFIGURED. Require PR approvals, CODEOWNER review for workflows/CI/release pins, required no-secret CI checks, no force push/deletion and no unreviewed bypass. |
| Tag rules | UNCONFIGURED. Restrict creation/update/deletion of release `v*` tags to named release maintainers; forbid retargeting; enforce 1.x+ syntax in CI. |
| Protected environment | UNCONFIGURED. Required independent reviewers, prevent self-review, selected protected release tags only; release source SHA and approvals checked before SDK use. Verify plan/visibility supports the required protection features. |
| Runner group | UNPROVISIONED. Dedicated ephemeral group restricted to this repository and approved workflow; no untrusted PR jobs, no VMware routes, no cross-job persistent workspace/cache, administrator-controlled SDK mount. Labels alone do not enforce isolation. |
| Licensed SDK | PENDING security/licensing approval. Admin supplies the JAR outside Git and build/upload roots, approves its checksum and read permissions. Never upload it to GitHub or create a private SDK Git repo for this workflow. |
| Toolchain | UNPINNED. Approve a full published F0.5-capable buildkit version/hash and pinned/provisioned Java, Python and PyYAML inputs; exercise in the actual isolated runner. |
| Approved reference | PASS selection/local comparison. CI must verify the exact Synology digest and repeat structural comparison on its actual output. |
| First release version/source | PROPOSED. Approve 1.0.0/build5 (or then-current next build), review and commit source after separate authorization, then verify tag matches merged metadata. |
| Full factory test baseline | F0.5 recorded an unrelated `/tmp/.git` fixture conflict and missing wheel-build backend. Resolve test-environment readiness before claiming all release prerequisite tests green. |
| Candidate/provenance | NOT BUILT in F1. First protected CI run must pass all gates, emit the PAK/sidecar/evidence allowlist, and prove no SDK leak. |
| Publication | NOT AUTHORIZED. Independently download and verify CI artifact with `sha256sum -c`; compare release/source/toolchain/reference provenance, then obtain separate publication approval. |
| Deployment/persistence | NOT AUTHORIZED. Follow the existing controlled experiment with its separate change approval and rollback procedure. |

## Exact external actions requiring separate approval

1. Create the proposed org repository with approved visibility and controls.
   Preserve the independent local Git history; do not create a submodule.
2. Configure repository/team permissions, main/tag rulesets, CODEOWNERS,
   required checks and protected release environment/reviewers. Approve the
   dedicated runner group/workflow restrictions and network boundary.
3. Provision/register the isolated runner and licensed SDK; supply approved
   digests/toolchain values and environment source-approval configuration.
   No secret retrieval is part of F1.
4. Publish or select an approved full buildkit release containing F0.5 and
   record its digest; first complete its own factory governance if a new
   tooling release is needed.
5. After repository existence, add the approved remote to the local adapter,
   add the active factory registry entry, commit reviewed changes to their
   respective repositories, and push only after explicit authorization.
6. After protected PR checks and version/source approval, create and push the
   approved 1.x+ release tag to start CI. Independently verify the CI PAK,
   sidecar and provenance; approve publication separately. Never reuse a
   local `0.x` PAK or clobber a published asset/tag.

## Offline validation and artifact retention

| Check | F1 outcome |
|---|---|
| Adapter CI tests | PASS, 23 stdlib tests. Mocked pipeline success and failure cases cover SDK/reference checks, bad registry response, defect gate, SDK validation, Java tests and both comparator stages. Failures do not create the upload output. Tests also cover namespace-aware descriptors, SDK realpath/Git scope, vendor-bytecode exclusion and raw/resolved SDK-path redaction. |
| Focused Java tests | PASS, 7; independent reviewer used the existing authorized local SDK. |
| `validate-sdk` | PASS; existing javac source/target-11 warning only. |
| Existing build-4 package inspection | PASS, read-only. No PAK regenerated and no official candidate produced. Temporary synthetic test ZIPs are not release artifacts. |
| Existing artifact structural comparison | Independent rerun: exit 0, 0 BLOCKING / 3 WARNING / 22 INFO. All findings retained; this remains local build-4 evidence, not the future CI candidate gate. |
| Full seven-package content validation | PASS, `scripts/validate-changed-content.sh --all`. |
| Codex skill parity | PASS, 5 paired and 7 Codex-only skills. |
| Path-reference audit | Clear; 6 existing standing-exception warnings (TVS and downstream local defect registry). No policy exception added. |
| Workflow YAML / shell / whitespace | Both workflows parse; `bash -n scripts/run-tests.sh` and both repositories' `git diff --check` pass. GitHub Actions execution is not validated by parsing. |
| Scope/isolation | Factory tooling, `.claude/`, immutable reference material and active adapter registry unchanged. Adapter Java, descriptor, metadata/version and fixtures unchanged. Both repositories retain their original HEADs and independent Git boundaries; adapter still has no remote. Nothing staged or committed. |

Retained SHA-256 identities:

- POC `vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak`:
  `5354acc09b4afa5a2fad5aed9429adebd8fe0f0e751b0b64b909c59854381d61`.
- Approved Synology `vcfcf_sdk_synology_diskstation.1.0.0.30.pak`:
  `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.

The unchanged factory's complete pytest suite was not rerun for these
documentation/independent-adapter CI changes. The F0.5 environment failures
remain explicitly unresolved above; F1 does not claim a green full pytest
baseline. No installation, dependency download or live access occurred.

## Recommendation

Independent `sdk-adapter-reviewer` verdict: APPROVE for offline preparation,
zero remaining implementation blockers. The review record is
`knowledge/context/reviews/rdm-topology-poc-f1-ci-readiness-review.md`.
The SDK skill and reviewer contract drove the isolated dependency path,
package-inspection regressions and explicit distinction between local checks
and externally enforced release controls.

CONDITIONAL GO for separately authorized repository/CI setup, subject to the
checklist and independent review. NO-GO for release-tag execution,
publication or deployment now: approval pins are intentionally unset,
release enablement is disabled, external protections/runner admission are
unconfigured and no first CI-built candidate exists. A completed offline
implementation is not evidence that GitHub enforces those controls.

No command in this record has been executed against GitHub, a CI runner or
VMware. F1 stops here; none of the external actions listed above is authorized
by this assessment.
