# F1 — independent RDM POC protected CI readiness review

Date: 2026-10-15. Role: independent `sdk-adapter-reviewer`, with the shared
reviewer doctrine. Scope: local CI preparation and repository isolation, not
runner provisioning, release execution or deployment.

## Verdict

**APPROVE — zero remaining BLOCKING implementation findings.** The prepared
workflow and helper satisfy the approved E1.5/F0.5 contract for offline
preparation. **CONDITIONAL GO for separately approved repository/CI setup;
NO-GO for tagging, publication or deployment.** Release enablement is false,
dependency approval pins are unset and external protections remain unverified.

If shipped as-is, hosted source checks can run without the SDK; the protected
candidate builder refuses execution. It cannot produce an official release
until the listed approval/configuration prerequisites are completed. There is
no release-publication step or `contents: write` permission.

## Independently inspected scope and evidence

Factory base: `b4be5a9dbb60c949d35c6def59286edf50145113`, branch
`feature/rdm-topology-mp`. Independent adapter base:
`cb2292db90d5d0a8da530e9c187986307daf0d2b`, branch `main`, no remote. Reviewed
adapter changes are its `.github/workflows/`, `ci/`, `.gitignore`, README link
and framework-JAR override in `scripts/run-tests.sh`. Java, `describe.xml`,
`adapter.yaml` and `CHANGELOG.md` are unchanged. Version remains prototype
`0.1.0`, build 4. No submodule or tracked factory adapter entry was introduced.

The adapter checkout and preview PAK are local-only artifacts, not reproducible
from a factory clone alone; the relevant findings are summarized here in full.
The proposed remote/registration and required external setup are documented in
`knowledge/designs/managementpacks/vsphere-rdm-topology-f1-protected-ci-preparation.md`.

| Control | Independent assessment |
|---|---|
| Source trust | Release workflow requires the exact repository, protected tag push, repository enablement, protected environment and isolated runner group. Helper verifies exact approved source SHA, clean checkout, main ancestry and strict 1.x+ tag/version/build/artifact agreement. Environment approval and runner admission remain external requirements. |
| Untrusted PR isolation | Source workflow uses only hosted runners and no SDK/secrets. Release workflow has no PR, workflow-run or manual-dispatch trigger. Restricting runner access to the approved workflow is explicitly required outside YAML; labels alone are not claimed as enforcement. |
| Proprietary dependency | Administrator supplies the SDK outside workspace, Git ancestry (including worktrees), scratch and upload roots. Realpath and approved digest are checked before SDK validation, Java tests or compilation. SDK is never fetched or copied by the helper. |
| Dependency provenance | Full published buildkit tag/version/archive digest, vendored gate digest, SDK digest and approved Python/Java/javac/PyYAML identities are required. Archive integrity precedes extraction/execution; unsafe archive paths, links/devices and duplicates are rejected. Unset approval pins fail closed. |
| RULE-012/005 gates | Release wrapper requires the exact registry header, a recognized historical DEF section and no HTML envelope before the unchanged vendored parser reads current factory registry DATA. Defect, validation, tests, automatic structural gate and explicit structural comparison must all succeed before output creation. Exact Synology filename and digest propagate to both comparator entry points; no warning-only switch or adapter exemption is used. |
| Artifact handling | Expected PAK filename/count, ZIP integrity, outer/inner members, permitted JARs/class namespaces, descriptor credential-free contract and embedded versions are checked. Only PAK, SHA sidecar, sanitized comparison and provenance enter upload output. All comparator findings remain visible. |
| Failure/cleanup | Failed gates prevent upload; temporary build context is removed. Existing output is refused. Diagnostics redact raw and resolved SDK/source/build paths while retaining finding text. Cancellation/host failure additionally requires external ephemeral-runner teardown. |
| Reproducibility claim | Source and dependency identities are traceable. Bit-identical cross-run PAK output is explicitly unproven; no local preview is promoted to an official artifact. |

The approved reference remains Synology release `v1.0.0.30`; no network request
was made during this review. Independently recomputed immutable artifact hashes:

| Artifact | SHA-256 |
|---|---|
| Existing RDM preview `vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak` | `5354acc09b4afa5a2fad5aed9429adebd8fe0f0e751b0b64b909c59854381d61` |
| Approved Synology `vcfcf_sdk_synology_diskstation.1.0.0.30.pak` | `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1` |

Audited helper SHA-256:
`c3eccf04a31eb83f37dc6d79512b5809828c449b318daef2c92ef0b85f4062d2`.
Audited release-workflow SHA-256:
`44a1b38eaf57c7efb9da91f3e5daf1b35ed133d85b38e93704803aba4e8d3a90`.

## Independent reruns and resolved review findings

- Offline release tests: **23 passed** using stdlib unittest. Real orchestration
  runs against synthetic local dependencies; SDK/reference/defect/validation/
  Java-test/automatic-comparison/direct-comparison failures prevent output.
  Success checks exact output membership, sidecar, provenance and sanitization.
  The temporary synthetic ZIP named `1.0.0.5` is a test fixture, not a compiled
  PAK or release candidate; it is destroyed with the test directory.
- Registry envelope follow-up: empty/unrecognized/HTML/header-only downloads
  are rejected; a mocked invalid response stops before the parser, SDK
  validation, compilation and output. Independently checked the actual local
  factory registry through both envelope validation and the unchanged vendored
  gate: **PASS**, no open blocking RDM defect. Vendored parser SHA remains
  `b58e6cce671669c1de366638ae337abe3ee92fdea68fd8c481403511f9619501`.
- Supplied-SDK `validate-sdk`: **PASS**, with the existing javac source/target
  11 module-path warning. Focused Java tests: **7 passed**.
- New package inspector against unchanged real build-4 PAK: **PASS**. No new
  real PAK was built or release metadata changed.
- Public exact-reference structural comparison: **exit 0; 0 BLOCKING,
  3 WARNING, 22 INFO**, unchanged from F0.5. D8, D23 and D25 remain visible:
  instance-identifier count and missing traversal declarations. F0.5's detailed
  findings disposition remains authoritative; none is suppressed or waived.
- Shell syntax and adapter whitespace checks: **PASS**. Direct invocation of
  the disabled real helper: **exit 1**, with no release-output directory.
- Full changed-content validation: **PASS**, independently rerun with
  `scripts/validate-changed-content.sh --all`. Path-reference audit: **clear**,
  with only six existing TVS/downstream-local-registry standing-exception
  warnings. Factory whitespace check: **PASS**.

The review caught namespace-blind descriptor queries, an overly broad inner
archive surface and incomplete SDK-scope/log-scrub handling. The author corrected
these before approval: QName normalization and namespaced regressions; exact
inner payload allowlist; independent Git/worktree ancestor rejection; and raw
plus resolved path redaction with preserved comparator text. This reviewer made
no implementation edits. These resolved findings trace to the SDK skill's
build-hygiene/gap-honesty requirements, RULE-008 and the explicit E1.5 SDK and
artifact-isolation contract.

The orchestrator subsequently identified that the vendored parser can accept
an empty/unrecognized response as zero entries. Review was reopened; the author
added the release-wrapper envelope guard described above, and this reviewer
independently reran all 23 tests and the real local registry checks before
reaffirming APPROVE. The parser, its hash and RULE-012 policy are unchanged.
The guard intentionally assumes the current canonical header and retained
historical DEF entries: a legitimate future empty registry or format change
requires review of this wrapper and fails closed until then. The envelope check
does not replace the parser's entry validation or claim to authenticate registry
semantics beyond the approved download source.

## Remaining external prerequisites and governance

Repository creation/visibility, actual main/tag rulesets, a valid CODEOWNERS
owner/team, required checks, protected environment reviewers/prevention of
self-review, exact-source approval, runner admission and network isolation,
licensed SDK provisioning, image acquisition provenance and all dependency pins
remain **unverified and disabled**. A full published F0.5-capable buildkit with
the approved reference must be selected and approved. No GitHub infrastructure
was queried or changed. Local YAML and mocked tests cannot establish those
controls or prove an actual protected CI build.

RULE-005 and RULE-014 remain unchanged. The local build-4 structural comparison
passes its sub-check; the actual official CI artifact still owes the same gate,
release review and explicit publication authorization. Runtime relationship
acceptance/persistence, VMware-edge preservation and UI visibility remain the
separately authorized deployment experiment. The known F0.5 full-factory-suite
environment limitations must also be resolved before claiming a green release
baseline; this review does not relabel that suite as passed.

Registry check: `knowledge/context/defects.md` contains no open
`Affects: rdm-topology-poc` defect. No new surviving WARNING-or-higher
implementation defect is proposed. The existing F0.5 comparison warnings and
unproved runtime behavior remain documented limitations.

This reviewer used local inspection, supplied-SDK compilation/tests and offline
artifact comparison only. No SDK binary was copied, no real PAK regenerated,
no credentials retrieved, no Git write/remote/tag/release performed and no
VMware system contacted. Writes were confined to this review report.
