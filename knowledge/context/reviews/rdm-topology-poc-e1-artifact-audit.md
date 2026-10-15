# RDM topology POC — E1 offline artifact audit

**Assessment date:** 2026-10-14  
**Scope:** local, offline examination only. No VMware or VCF Operations
endpoint was contacted, and no installation, configuration, mutation, commit,
push, remote creation, or publication occurred.

## Repository separation and revisions

| Repository | Location | Branch | HEAD | Remote / status |
|---|---|---|---|---|
| Factory | repository root | `feature/rdm-topology-mp` | `b3fbbc4c95821e9cd89f6cf54bff318c8d597c91` | tracks `origin/feature/rdm-topology-mp`; E1 documentation is uncommitted work | 
| POC adapter | `content/sdk-adapters/rdm-topology-poc` | `main` | `4493ee2584f180be65a4472b0996f5207d8ee456` | no remote configured; clean at assessment time |

The adapter directory has its own `.git` worktree and is ignored by the
factory repository. It is not a submodule, and neither repository contains
the other repository's Git metadata. This preserves the independent-versioned
adapter model required by `knowledge/lessons/sdk-paks-independent-repos.md`.

## Assessed development artifact

| Field | Value |
|---|---|
| Artifact | `content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.2.pak` |
| SHA-256 | `101063028f09845f849cd23b9e0139f787116b75b1fd7d3d33e4fe6c21827ac8` |
| Size | 78,312 bytes |
| Manifest version | `0.0.0.2` (development preview) |
| Declared adapter version / build | `0.1.0` / `2` |
| Adapter kind | `vcfcf_rdm_topology_poc` |
| Entry class | `com.vcfcf.adapters.rdmtopologypoc.RdmTopologyPocAdapter` |

This is a local development artifact, not an official release artifact. Per
`knowledge/lessons/sdk-paks-independent-repos.md` and RULE-014, a local `0.x`
PAK must not be published or represented as the CI release artifact.

The artifact path above is **local-only and not reproducible from a fresh
factory clone**: the independently versioned POC repository has no configured
remote or published release. The checksum is recorded to identify this
assessment input, while the structural findings are summarized in this report
so no later decision depends on retrieving the local file (RULE-015).

## Static content findings

- `describe.xml` declares one pack-owned `RdmMapping` resource kind and the
  expected stable identifiers: `vcenter_instance_uuid`, `vm_instance_uuid`,
  and `virtual_disk_key`.
- The adapter fixture constructs a foreign `VMWARE::VirtualMachine` key from
  its supplied identifier collection, preserving each identifier's actual
  uniqueness flag. It requires uniqueness-bearing `VMEntityObjectID` and
  `VMEntityVCID`; it does not select by display name or bare MOID.
- The compiled relationship helper calls only
  `RelationshipBuilder.parentForeign(foreignVm, localMapping)`. The framework
  implementation emits that foreign-parent edge with additive
  `Relationships.addRelationships`, not `setRelationships`.
- The package contains the POC adapter JAR, `describe.xml`, resources/icons,
  and `vcfcf-adapter-base.jar`. It does **not** contain
  `vrops-adapters-sdk-2.2.jar` or another Broadcom SDK JAR.
- Offline scanning found no credentials, tokens, sessions, or raw lab
  inventory. The deterministic test fixture's `vm-71` value is a synthetic
  identity test value, not a captured report or credential.

The audit proves package structure and emitted-call intent only. It does not
prove Suite API acceptance, topology persistence, or UI rendering.

## Reference-PAK disposition

`pak-compare` is **blocked, not passed**. No approved reference PAK is
available under `tmp/reference_paks/`, and an empty reference directory exits
as an unavailable comparison rather than a successful result.

The builder permits a development build to log-and-skip comparison when the
factory checkout has no reference PAK, but
`src/vcfcf_managementpacks/sdk_builder.py::_run_pak_compare` makes absence a
hard failure for release builds. RULE-005 likewise requires comparison against
the closest reference PAK before installation. No documented new-adapter
baseline exception authorizes an installation without a real comparison.

Do not fabricate a PAK or compare against an unrelated adapter. Resolution
requires an approved, structurally relevant SDK reference PAK placed through
the normal local reference mechanism, followed by a real comparison with zero
BLOCKING findings and recorded human approval of that reference's relevance.
