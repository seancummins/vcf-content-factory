# RDM topology POC F0.1 — independent Synology reference-selection review

**Reviewer:** `sdk-adapter-reviewer` (independent Codex context)  
**Date:** 2026-10-14  
**Scope:** Read-only, offline inspection of the nominated Synology release
artifact and the local RDM POC preview package. One read-only GitHub Release
API request verified published-release metadata and its recorded asset digest.
The asset binary was not independently re-downloaded in this environment.
No `pak-compare`, build,
installation, live VMware/VCF Operations access, source change, or GitHub
mutation occurred.

## Verdict

**APPROVE — 0 BLOCKING findings for selection of the exact Synology artifact
as a structural comparator.**

This approval satisfies the E1.5 *reference-selection* review prerequisite;
it does **not** satisfy RULE-005's comparison, release, or installation gates.
The reference is approved only as the exact SHA-256-qualified release artifact
below, after it is supplied to the buildkit reference mechanism. A future CI
`pak-compare` must still report zero BLOCKING findings. It must report all
WARNING and INFO findings unchanged.

**If treated as a release or deployment approval:** an operator would be
misled. This review establishes packaging-family relevance only; it neither
executes the comparison nor demonstrates cross-management-pack relationship
persistence.

## Exact candidate and provenance

| Item | Independently verified evidence |
|---|---|
| Artifact | `vcfcf_sdk_synology_diskstation.1.0.0.30.pak` |
| Local inspection input | `tmp/reference_paks/vcfcf_sdk_synology_diskstation.1.0.0.30.pak` (local-only staging path; not a durable corpus citation) |
| SHA-256 | `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1` |
| Integrity | 106,491 bytes; `unzip -t` completed with no archive errors. |
| Published release | `sentania-labs/vcf-content-factory-sdk-synology` release [`v1.0.0.30`](https://github.com/sentania-labs/vcf-content-factory-sdk-synology/releases/tag/v1.0.0.30), published 2026-08-18 by `github-actions[bot]`. The read-only GitHub Release API named the same asset, size, and `sha256:beaa…480a1` digest. The release binary was not independently re-downloaded here; this is a metadata-to-local-digest match, not fresh-download proof. |
| Source/tag evidence | Local registered Synology repository tag `v1.0.0.30` resolves to commit `6ebc82c046b74fcf0b6daf2695a2078dac620e62`; its `adapter.yaml` declares `synology_diskstation`, version `1.0.0`, build `30`, and `released: true`. `knowledge/context/managed_paks.md` registers this public repository as the Synology adapter remote. |

The release URL plus full digest makes the artifact deterministically
re-fetchable. The scratch path itself is not an enduring dependency; all
inspection findings required to reproduce this decision are recorded here, in
accordance with RULE-015.

## E1.5 prerequisite assessment

| E1.5 selection requirement | Result | Evidence |
|---|---|---|
| Traceable, legally available provenance and recorded SHA-256 | **PASS, bounded** | Official public Sentania Labs GitHub Release, registered repository, published asset name/size/digest, and local digest match above. Direct asset re-download was unavailable in this environment, so this is not an independent download verification. No unsigned checksum sidecar or GitHub artifact attestation was available in the inspected release, so provenance is release/digest evidence rather than a reproducible independent rebuild. |
| Same native Java SDK PAK family and Operations line | **PASS** | Both artifacts are Linux VA PAKs with `vcops_minimum_version: 8.0.0`, a top-level `adapters.zip`, and the conventional adapter directory plus application JAR and `vcfcf-adapter-base.jar`. Synology declares version `1.0.0.30`; the RDM POC is deliberately a local `0.0.0.2` preview under RULE-014. |
| Relevant manifest, adapter archive, `describe.xml`, and runtime layout | **PASS** | Synology manifest has adapter kind `synology_diskstation`; `adapters.zip` contains `synology_diskstation.jar`, `synology_diskstation/conf/describe.xml`, `conf/version.txt`, resources, images, and `lib/vcfcf-adapter-base.jar`. The POC has the same layout for `vcfcf_rdm_topology_poc`. The framework-base JAR hashes differ, which is expected across buildkit/framework builds and is a legitimate future comparison finding rather than a reason to substitute or alter either artifact. |
| Structural relevance to foreign-parent relationship mechanics | **PASS, with bounded scope** | Synology's released `describe.xml` includes traversal paths from local `SynologyIscsiLun` and `SynologyNfsExport` to `VMWARE::Datastore::~child`; its tagged `adapter.yaml` declares additive `parent_foreign` edges from a foreign VMWARE Datastore to each local resource. This is the closest currently available approved-family example of a foreign VMWARE parent with a pack-owned child. The POC's target is instead `VMWARE::VirtualMachine` → local `RdmMapping`; matching identity, relationship persistence, and topology semantics remain a deployment proof, not a structural-comparison claim. |
| SDK is excluded from the distributable | **PASS, archive-scope** | The Synology adapter archive contains only its application JAR and `vcfcf-adapter-base.jar`; neither contains nested JARs or SDK/vendor-named class entries. The POC has the same two-JAR pattern. This verifies no separately bundled Broadcom SDK JAR in either PAK; it is not a license audit of all compiled bytecode. |
| Approved-reference handling and real comparison | **NOT YET EXECUTED** | Per E1.5, the release owner must put this exact release artifact into the buildkit/reference mechanism, not the POC adapter repository, then run the designated CI `pak-compare`. This review intentionally did not run it. |

## Packaging and resource-model observations

The Synology package declares its adapter instance plus nine local resource
kinds: `SynologyWorld`, `SynologyDiskstation`, `SynologyStoragePool`,
`SynologyVolume`, `SynologyDisk`, `SynologyIscsiLun`, `SynologyNfsExport`,
`SynologyUps`, and `SynologySsdCache`. Its relevant LUN identity is the
required `lun_uuid` resource identifier. The RDM POC instead declares only
the adapter instance and `RdmMapping`, whose required identity tuple is
`vcenter_instance_uuid`, `vm_instance_uuid`, and `virtual_disk_key`.

Those are intentional semantic differences. A structural comparator can test
the native-SDK PAK envelope, manifest, adapter layout, XML shape, and runtime
library treatment; it cannot certify the POC's VM foreign-key values,
uniqueness flags, additive call behavior, idempotence, or relationship
persistence. The latter remain governed by the approved E2 deployment
experiment and the cross-MP identity lessons.

## Policy and registry check

- **RULE-005** (`knowledge/rules/validate-before-install.md`) still requires
  `pak-compare` with zero BLOCKING findings before install. This selection
  approval is not a waiver.
- **RULE-014** (`knowledge/rules/pak-version-lines.md`) still prohibits
  promoting the POC's hand-built `0.x` artifact. The Synology `1.0.0.30`
  release is an appropriate prior CI-release structural reference, not a
  template for promoting the POC preview.
- **RULE-015** (`knowledge/rules/cited-artifacts-reproducible.md`) is met by
  recording the public release URL and full checksum; the temporary local
  path is explicitly non-authoritative.
- **Defect registry:** all defects whose `Affects:` value is `synology`
  (DEF-001, DEF-003, DEF-005, and DEF-006) are **closed**. No open defect
  affects `rdm-topology-poc` (which is not yet a managed release scope). No
  open-registry defect blocks this selection review.

## Required next step and remaining limitations

1. The release owner must record this exact URL/digest in the approved
   buildkit reference facility and obtain any required release-owner approval
   for that addition; do not copy it into the independent adapter repository
   or fabricate a baseline.
2. Run the existing CI `pak-compare` against the RDM POC package only after
   that staging is approved. Preserve every BLOCKING, WARNING, and INFO result
   verbatim in the release review; zero BLOCKING is required to clear the
   comparison gate.
3. A clean comparison remains insufficient for release or deployment until
   the independent repository, protected SDK handling, CI-built `1.x+`
   artifact, defect gate, administrator approval, and separately authorized
   E2 persistence experiment are complete.

No new defect-registry entry is proposed: this review found no unresolved
WARNING-or-worse defect in the reference-selection decision itself.
