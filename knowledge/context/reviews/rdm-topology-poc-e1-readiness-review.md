# RDM topology POC E1 — independent deployment-readiness review

**Reviewer:** `sdk-adapter-reviewer` (independent, offline gate)
**Scope:** E1 artifact audit and controlled-persistence experiment plan
**Binary verdict:** **APPROVE — 0 blocking defects in the offline audit or
experiment plan.**
**Deployment recommendation:** **NO-GO.**

The approval is limited to the accuracy and conservatism of the reviewed E1
artifacts. It is not installation approval. The plan correctly makes a real
reference-PAK comparison and an official CI-built candidate mandatory, and
neither exists yet. Proceeding with the local development PAK would violate
the plan, RULE-005, and the independent-SDK-pak release model.

## Independent artifact verification

| Claim | Independent result |
|---|---|
| Factory revision / branch | **Verified:** `feature/rdm-topology-mp` at `b3fbbc4c95821e9cd89f6cf54bff318c8d597c91`; only the two E1 documents are uncommitted factory work. |
| Adapter revision / branch | **Verified:** independent worktree at `content/sdk-adapters/rdm-topology-poc`, branch `main`, HEAD `4493ee2584f180be65a4472b0996f5207d8ee456`, clean. It has Git metadata of its own, is ignored by the factory, and has no configured remote. |
| Assessed PAK | **Verified:** `dist/vcfcf_sdk_rdm_topology_poc.0.0.0.2.pak`, mode `0644`, size **78,312 bytes**, SHA-256 **`101063028f09845f849cd23b9e0139f787116b75b1fd7d3d33e4fe6c21827ac8`**. |
| PAK metadata | **Verified:** manifest version `0.0.0.2`, adapter kind `vcfcf_rdm_topology_poc`, entry class `com.vcfcf.adapters.rdmtopologypoc.RdmTopologyPocAdapter`. |
| Package hygiene | **Verified:** one POC adapter JAR, `describe.xml`, resources/icons, and `vcfcf-adapter-base.jar`; no `vrops-adapters-sdk`/Broadcom SDK JAR, credentials, token/session files, or raw lab report were found. |
| Repository separation | **Verified:** the POC is an independent Git repository rather than a factory submodule or tracked factory child. The factory does not contain the adapter repository’s Git metadata. This meets the separation model in `knowledge/lessons/sdk-paks-independent-repos.md`. |

The artifact-audit statements are therefore accurate. Its caution that this is
a local development artifact—not a reproducible, published release—is also
accurate: the POC has no configured remote and no CI-release artifact.

## Reference-PAK disposition

**Blocked, not passed.** There is no `*.pak` under `tmp/reference_paks/` or
the repository reference locations. The builder’s development path may log
and skip a missing comparison, but its release path fails closed when no
reference PAK exists (`src/vcfcf_managementpacks/sdk_builder.py` lines
2367–2395 and 3390–3417). An empty reference directory is an unavailable
comparison, not a successful comparison.

The audit and experiment plan correctly refuse to fabricate a baseline or use
an unrelated PAK. That is required by RULE-005
[`knowledge/rules/validate-before-install.md`](../../rules/validate-before-install.md)
and by the `vcfops-sdk-adapter` validation loop. No comparison result can be
claimed until an approved, structurally relevant SDK reference PAK is supplied
through the normal local reference mechanism and produces zero BLOCKING
findings.

## Experiment-plan review

The plan is fit for a future, separately approved E2 experiment:

- **Identity safety:** it requires a unique real `VMEntityObjectID` plus
  `VMEntityVCID` identity with the returned uniqueness flags preserved; bare
  MOID and display-name matching are explicitly forbidden. This matches
  `knowledge/lessons/stitch-moid-not-unique-across-vcenters.md` and
  `knowledge/lessons/cross-mp-foreign-key-uniqueness-flags.md`.
- **Baseline safety:** it captures the complete selected-VM relationship set,
  POC resource/instance counts, endpoint fingerprints, and a pre-install
  identity recheck. Missing/incomplete/ambiguous proof is a stop condition.
- **Persistence test:** it separates platform acceptance, API persistence,
  and UI visibility. It requires one mapping and one edge after collection,
  then tests a second POC cycle and a subsequent VMWARE cycle. This properly
  treats a UI-only observation as insufficient.
- **Topology protection:** it requires all baseline VMware-owned
  relationships to remain unchanged and stops immediately on a missing or
  changed endpoint. This is consistent with the additive foreign-parent
  mechanism documented in
  `knowledge/lessons/cross-mp-stitch-cp-identity-and-edge-mechanics.md`.
- **Rollback:** it is conservative: baseline again before removal; remove only
  the POC instance; never delete/repair a VMWARE resource; verify both POC
  counts and the exact VM relationship baseline after reconciliation; stop
  and escalate rather than manually repair any anomaly.
- **Secret/artifact safety:** it keeps raw UUID handoffs, responses, and
  credentials outside Git and preserves sanitized-only evidence, consistent
  with RULE-008 [`knowledge/rules/no-secrets-on-disk.md`](../../rules/no-secrets-on-disk.md).

The plan correctly states that the local PAK cannot establish foreign-edge
persistence, retention, or UI direction. No live endpoint, installation,
credential retrieval, commit, push, remote creation, or source modification
occurred during this review.

## Registry check

`knowledge/context/defects.md` was checked. No open defect has an `Affects:`
value for `rdm-topology-poc`, `rdm`, or `vcfcf_rdm_topology_poc`. No closure
is proposed and no registry was modified, satisfying RULE-012
[`knowledge/rules/release-gate-defects.md`](../../rules/release-gate-defects.md).

## Conditions that change NO-GO to conditional GO

All of the following require re-verification before any installation request:

1. An approved, structurally relevant SDK reference PAK is placed by the
   sanctioned mechanism; `pak-compare` is rerun against it with zero
   BLOCKING findings and documented reference relevance.
2. The POC has an operator-approved commit, an appropriately configured
   independent release workflow, and an official CI-built release candidate.
   The local `0.0.0.2` PAK must not be substituted for that artifact.
3. A named development-lab change, maintenance window, fixture VM, and
   rollback plan receive explicit administrator approval.
4. The pre-install read-only identity proof returns exactly one VM candidate
   with the expected real identity tuple and actual uniqueness flags, and the
   operator captures the documented sanitized baseline.
5. An authorized lab administrator—not this review process—has the scoped
   install/removal authority and a secure non-Git evidence location.

Only then is the correct recommendation **CONDITIONAL GO** for the bounded E2
experiment—not for production rollout. A post-experiment reviewer must still
evaluate API persistence, UI visibility, duplicate behavior, and cleanup
against the plan before a production design decision.
