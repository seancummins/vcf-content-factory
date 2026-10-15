# RDM topology POC E1.5 — independent governance and CI-readiness review

**Reviewer:** `sdk-adapter-reviewer` (independent Codex context)  
**Date:** 2026-10-14  
**Scope:** Offline review of the proposed first-release governance plan and
related local E1 records. No network, GitHub, CI, VMware endpoint, credential,
repository, remote, adapter-source, or package change was made.

## Binary verdict and recommendation

**APPROVE — 0 BLOCKING findings in the corrected governance plan.**

**Recommendation: NO-GO for execution; GO only for the documented setup-plan
state.** The B1 version-line defect is corrected in the plan. Remote creation,
tagging, CI release, publication, installation, and the E2 experiment remain
separately blocked pending the listed approvals and evidence.

## Authorities checked

- `knowledge/rules/pak-version-lines.md` (RULE-014): a `0.x` PAK is a local
  development preview and is never tagged or attached to a GitHub Release;
  the CI release line is `<adapter.yaml version>.<build_number>` and must be
  `1.x+`.
- `knowledge/rules/validate-before-install.md` (RULE-005): an MP requires
  `pak-compare` against a reference PAK with zero BLOCKING findings before
  installation.
- `knowledge/rules/release-gate-defects.md` (RULE-012), as indexed in
  `knowledge/rules/INDEX.md`: blocking defects gate a `v*` release.
- `knowledge/context/managed_paks.md`, “Hard rules” and “Naming convention”:
  SDK adapters are independent repositories, named
  `sentania-labs/vcf-content-factory-sdk-<name>`, mounted under
  `content/sdk-adapters/<name>/`, and registered only after their remote
  exists. The registry is SHA- and version-free.
- `knowledge/lessons/sdk-paks-independent-repos.md`: the official PAK is a
  tag-triggered CI build; a local build is never the shippable artifact.
- `src/vcfcf_managementpacks/buildkit.py:428-446` and
  `src/vcfcf_managementpacks/sdk_builder.py:309-351,2367-2395`: `--release`
  is CI-only and a release build fails closed without a reference PAK; local
  builds are stamped `0.0.0.<build_number>`.

## Independently verified findings

| Area | Result | Evidence and review finding |
|---|---|---|
| Repository separation and naming | PASS as a future-state plan | The plan names `sentania-labs/vcf-content-factory-sdk-rdm-topology-poc`, the prescribed factory mount, and `vcfcf_rdm_topology_poc`. This matches `managed_paks.md`. The local POC remains a separate Git repository at commit `4493ee2584f180be65a4472b0996f5207d8ee456` and has no configured `origin`; no remote was contacted or changed. |
| Registry timing | PASS as a future-state plan | The plan adds the registry entry only after remote creation and omits a binary, SHA, and release version. A local search found no current `rdm-topology` registry entry, which is correct while the remote does not exist. |
| First-release `pak-compare` disposition | PASS as a future-state plan; currently BLOCKED | The plan does not invent an exemption, self-baseline, or unrelated baseline. It correctly limits any accommodation to independently approved structural-reference selection. No `*.pak` exists in local `tmp/reference_paks/`; therefore no comparison has run and the gate remains blocked, consistent with RULE-005 and the release-build fail-closed implementation. |
| CI SDK strategy | ACCEPTABLE DESIGN, NOT YET IMPLEMENTED OR VERIFIED | A dedicated protected, non-public runner; externally provisioned licensed JAR; checksum verification; no PR execution; no lab reachability; no SDK upload; and sanitized outputs are a coherent non-redistributive strategy. It is correctly labeled a proposal requiring licensing and security-owner approval. The local POC has no `.github` workflow, so the strategy has not been implemented, exercised, or security reviewed. It cannot be treated as release evidence. |
| Local PAK non-promotion | PASS | The plan explicitly excludes `vcfcf_sdk_rdm_topology_poc.0.0.0.2.pak` from release/baseline promotion. This conforms to RULE-014 and the independent-repository lesson. |
| Readiness matrix | PASS as a future-state plan | It accurately leaves the reference PAK, remote, CI release workflow, first-release version line, official artifact, authorization, and E2 experiment blocked. |

## B1 re-review — resolved

The original B1 finding was that the plan directed a `v0.1.0.2` release while
the local POC declared `version: "0.1.0"` and `build_number: 2`. Such a
release would stamp a forbidden `0.x` PAK under RULE-014.

The corrected plan's operator step 8 now requires all of the following before
any tag: approval of a `1.x+` first-release version; an update of
`adapter.yaml` and `CHANGELOG.md` in the independent repository; the next
approved monotonic build number; and a protected tag exactly equal to the
approved version/build tuple. It explicitly states that the current `0.1.0`
metadata and derived `v0.1.0.2` are prototype-only and must never be tagged or
released. Its readiness matrix now contains a separate, BLOCKED
“First-release version line” gate requiring approved `1.x+` metadata,
changelog, and matching protected tag.

This satisfies RULE-014 at the planning level. It does not assert that the
future independent repository has already been updated, nor authorize a tag:
those remain explicit release prerequisites.

## Registry and policy checks

- **Defect registry:** no entry names `rdm-topology` or
  `rdm_topology`; this review records B1 as an unresolved release-plan finding,
  not as evidence that a release is allowed. Before any tag, the exact
  independent-repository defect-gate invocation must be run against the
  then-current registry and repository state per RULE-012.
- **Reference PAK:** absent locally; the plan correctly makes this BLOCKED
  rather than waived. A candidate must be legally available, provenance and
  checksum recorded, structurally justified, independently approved, and
  yield zero BLOCKING findings in CI.
- **Template/remote convention:** the intended name and mount conform to the
  factory convention, but there is no remote or generated repository workflow
  to validate. Creating/configuring either needs separate external-action
  authorization.
- **Local PAK hygiene:** the local preview PAK is not a promotion candidate.
  The future CI must upload only a fresh CI-built PAK, checksum sidecar, and a
  sanitized comparison report; neither SDK JAR nor lab evidence may enter an
  artifact, cache, repository, or release.

## Remaining prerequisites

1. Approve a `1.x+` release version/tag and revise the release plan, adapter
   metadata, changelog, and readiness matrix consistently in the independent
   repository.
2. Obtain separate authorization to create the sanctioned remote and then add
   its SHA-free, version-free managed-PAK registry entry.
3. Have security and licensing owners approve the protected-runner trust
   boundary, pre-provisioned SDK checksum mechanism, log/artifact controls,
   and no-secret PR workflow; implement and independently review that CI.
4. Select and approve a genuine structural reference PAK, record provenance
   and SHA-256, and obtain a zero-BLOCKING CI `pak-compare` result.
5. Run the defect gate, protected tag CI, artifact/checksum verification, and
   independent release review. Only then may a separate authorization consider
   deployment; relationship persistence still requires the explicitly
   authorized E2 experiment.

## Conclusion

The corrected governance direction is conservative in the right places: it
keeps the SDK non-redistributive, refuses a fabricated reference, keeps the
local PAK non-promotable, preserves independent-repository ownership, and
requires a `1.x+` version line before any tag. No live or external action is
approved by this review.
