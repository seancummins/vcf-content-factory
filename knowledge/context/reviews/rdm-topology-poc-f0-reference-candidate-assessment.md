# RDM topology POC F0 — reference PAK candidate assessment

**Date:** 2026-10-14  
**Scope:** Offline local-artifact discovery only. No VMware endpoint, GitHub,
CI, installation, build, package comparison, or adapter-source change occurred.

## Governing disposition

The E1.5 governance plan and its independent review remain controlling: there
is no first-release exemption from RULE-005. The permitted accommodation is a
reviewed **reference-selection** exception, not a comparison exception. A
selected reference must be provenance-traceable and legally available, use the
same native Java SDK PAK family and relevant Operations line, be justified by
an independent reviewer, enter through the buildkit reference mechanism, and
produce zero BLOCKING findings in CI. This assessment does not select a
reference and did not invoke `pak-compare`.

## Local inventory and ranking

| Rank | Candidate / artifact | Local path and SHA-256 | Source repository and version evidence | Packaging relevance | Status / approval gap |
|---|---|---|---|---|---|
| 1 (prospective) | Synology DiskStation | No `*.pak` exists in the checkout; checksum and PAK version are therefore unavailable. | `content/sdk-adapters/synology/`, `origin` = `sentania-labs/vcf-content-factory-sdk-synology`; checked-out `main` commit `06cce33f8b6f3e5be917cdf68ba46d90c61a119c`; `adapter.yaml` declares Tier 2, version `1.0.0`, build `30`, native entry class `com.vcfcf.adapters.synology.SynologyAdapter`. | Strongest prospective source family: native Java SDK layout and a declared additive, foreign-parent VMWARE datastore-to-local-resource stitch. A built artifact is required before its manifest, `adapters.zip`, `describe.xml`, entry point, resource declarations, dependency layout, and SDK exclusion can be inspected. | **Not an available PAK candidate.** Obtain the exact released PAK through an approved, legal source; record checksum/provenance; then obtain independent structural-relevance approval. |
| 2 (prospective) | UniFi Controller | No `*.pak` exists in the checkout; checksum and PAK version are therefore unavailable. | `content/sdk-adapters/unifi/`, `origin` = `sentania-labs/vcf-content-factory-sdk-unifi`; checked-out `main` commit `1824f5751c518e462076194154e22f32fb532a25`; `adapter.yaml` declares Tier 2, version `1.1.0`, build `13`, native entry class `com.vcfcf.adapters.unifi.UniFiAdapter`. | Same native Java SDK family and useful as a secondary structural comparator, but the checked source gives less direct evidence of the POC's foreign-parent relationship pattern than Synology. Its produced package has not been inspected. | **Not an available PAK candidate.** Same artifact, provenance, and independent-relevance approvals are required. |
| 3 (rejected) | RDM topology POC build 2 | Local-only `content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.2.pak`; SHA-256 `101063028f09845f849cd23b9e0139f787116b75b1fd7d3d33e4fe6c21827ac8`. | Independent local POC repository, commit `4493ee2584f180be65a4472b0996f5207d8ee456`; package metadata version `0.0.0.2`. | Its manifest declares `vcfcf_rdm_topology_poc`; `adapters.zip` contains that adapter JAR, `describe.xml`, and `vcfcf-adapter-base.jar`. No proprietary Broadcom SDK JAR was found in the archive. | **Rejected.** It is the candidate under test, a hand-built `0.x` preview, and cannot be its own comparison baseline. |

The only other local PAK is POC build 1,
`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.1.pak`
(SHA-256 `c9fc0a946cc689aa588028a7fd8e9254578c0edad255d088aeba90f9ff968056`).
It is likewise a self-artifact and rejected. No PAK was present in
`tmp/reference_paks/`.

The two POC paths above are local-only, gitignored development artifacts and
are **not reproducible references**. Their relevant inspection findings are
fully summarized here to comply with RULE-015; this record does not rely on
those paths as an input to a future fresh checkout.

## Packaging comparison outcome

The available evidence establishes that Synology and UniFi source trees are
Tier 2 native SDK projects with independently versioned GitHub origins. It
does not establish the structure of a produced Synology or UniFi PAK: neither
artifact exists locally, so no manifest, adapter-directory layout,
`describe.xml`, runtime-library inventory, or SDK-exclusion check can be
truthfully compared. The POC inspection establishes only its own normal
native-SDK package shape and SDK exclusion; it supplies no independent
baseline evidence.

## Recommendation and required next steps

**NO-GO for reference selection or release gating.** There is no qualified,
locally available reference PAK.

If an approved artifact is later made available, nominate the released
Synology PAK first because its documented native-SDK, cross-management-pack
foreign-parent stitching is closest to the POC's structural concern. Before
using it, the release owner must:

1. Record the exact legal source, PAK version, SHA-256, producing repository
   revision/tag, and Operations compatibility.
2. Inspect its manifest, `adapters.zip`, adapter directory, `describe.xml`,
   resource declarations, entry point, runtime libraries, and SDK exclusion.
3. Have an independent reviewer approve its structural relevance and enumerate
   semantic differences that `pak-compare` cannot validate.
4. Place only the approved reference through the buildkit/reference mechanism,
   then run the real CI `pak-compare` gate. It must have zero BLOCKING
   findings; this remains a prerequisite rather than proof of relationship
   persistence.

Until then, the E1.5 reference-PAK, CI-release, and deployment gates remain
blocked.
