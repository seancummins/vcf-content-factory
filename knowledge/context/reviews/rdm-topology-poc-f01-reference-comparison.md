# RDM topology POC F0.1 — approved Synology reference comparison

**Date:** 2026-10-14  
**Scope:** Offline PAK inspection and structural comparison only. No adapter
source, package, VMware system, VCF Operations system, GitHub release, or
installation was changed.

## Reference-selection disposition

The independent `sdk-adapter-reviewer` approved the exact published Synology
artifact as a **structural comparator only** in
`knowledge/context/reviews/rdm-topology-poc-f01-reference-selection-review.md`.

| Field | Recorded value |
|---|---|
| Release | [`v1.0.0.30`](https://github.com/sentania-labs/vcf-content-factory-sdk-synology/releases/tag/v1.0.0.30) |
| Artifact | `vcfcf_sdk_synology_diskstation.1.0.0.30.pak` |
| SHA-256 | `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1` |
| Local integrity check | 106,491 bytes; outer and nested ZIP integrity checks passed. |
| Source/tag | `sentania-labs/vcf-content-factory-sdk-synology`, tag `v1.0.0.30` → commit `6ebc82c046b74fcf0b6daf2695a2078dac620e62`. |
| Candidate POC | `vcfcf_sdk_rdm_topology_poc.0.0.0.2.pak`; SHA-256 `101063028f09845f849cd23b9e0139f787116b75b1fd7d3d33e4fe6c21827ac8`. |

The reviewer verified that GitHub Release API metadata named the same asset,
size, and SHA-256 digest as the local artifact. It did not independently
re-download the binary. The local staging path (`tmp/reference_paks/...`) is
not a durable corpus citation; the public release URL and checksum above are
the reproducible provenance record required by RULE-015.

The reference is relevant because both packages use the native Java SDK PAK
envelope for Operations 8.0+, with `adapters.zip`, an application JAR,
generated `describe.xml`, and `vcfcf-adapter-base.jar`. Synology additionally
provides the closest available released example of an additive, foreign
VMWARE-parent-to-local-resource relationship. It does not prove the POC's VM
identity, relationship persistence, or UI topology behavior.

## `pak-compare` result

Command executed after the independent selection approval:

```text
PYTHONPATH=src python -m vcfcf_managementpacks pak-compare \
  content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.2.pak \
  tmp/reference_paks/vcfcf_sdk_synology_diskstation.1.0.0.30.pak
```

**Result: FAIL — 2 BLOCKING, 3 WARNING, 20 INFO.** Findings are reproduced
without suppression or reclassification:

```text
BLOCKING (will likely cause install failure):
  [B1] describe.xml: CredentialKinds presence: factory has no <CredentialKinds>, reference has <CredentialKinds>
  [B2] describe.xml: adapter instance (type=7): factory no credentialKind attr, reference credentialKind="synology_credentials"

WARNING (may cause issues):
  [W1] describe.xml: adapter instance identifier count: factory=0, reference=3
  [W2] describe.xml: TraversalSpecKind count: factory=0, reference=1
  [W3] describe.xml: factory has empty TraversalSpecKinds, reference has entries

INFO (cosmetic, unlikely to affect install):
  [I1] manifest.txt: description differs: factory='Fixture-only proof of the VCF Operations Java SDK mechanics for an additive relationship from an existing VMWARE VirtualMachine to a pack-owned RdmMapping resource. This POC has no live vCenter or VCF Operations API collection, no CanonicalLun resource, and no production lifecycle behavior.', reference='Monitors Synology DiskStation NAS devices via the DSM Web API. Discovers storage pools, volumes, disks, iSCSI LUNs, NFS exports, and UPS. Collects capacity, performance, and health metrics. Cross-endpoint joining merges IO metrics onto the correct storage objects (Tier 2 trigger: complex data-model joining). Framework v2 (SPI: VcfCfTester/VcfCfCollector over AdapterBase; collect-path discovery via enumerateResources + discoverOnCollect, §22).'
  [I2] manifest.txt: display_name differs: factory='VCF Content Factory RDM Topology POC', reference='VCF Content Factory Synology DiskStation'
  [I3] manifest.txt: name differs: factory='VCF Content Factory RDM Topology POC', reference='VCF Content Factory Synology DiskStation'
  [I4] adapters.zip: 'conf/images/AdapterKind/vcfcf_rdm_topology_poc.svg' present in factory, absent from reference
  [I5] adapters.zip: 'conf/images/ResourceKind/RdmMapping.svg' present in factory, absent from reference
  [I6] adapters.zip: 'conf/images/ResourceKind/vcfcf_rdm_topology_poc.svg' present in factory, absent from reference
  [I7] adapters.zip: 'vcfcf_rdm_topology_poc.jar' present in factory, absent from reference
  [I8] adapters.zip: 'conf/images/AdapterKind/synology_diskstation.svg' present in reference, absent from factory
  [I9] adapters.zip: 'conf/images/ResourceKind/SynologyDisk.svg' present in reference, absent from factory
  [I10] adapters.zip: 'conf/images/ResourceKind/SynologyDiskstation.svg' present in reference, absent from factory
  [I11] adapters.zip: 'conf/images/ResourceKind/SynologyIscsiLun.svg' present in reference, absent from factory
  [I12] adapters.zip: 'conf/images/ResourceKind/SynologyNfsExport.svg' present in reference, absent from factory
  [I13] adapters.zip: 'conf/images/ResourceKind/SynologySsdCache.svg' present in reference, absent from factory
  [I14] adapters.zip: 'conf/images/ResourceKind/SynologyStoragePool.svg' present in reference, absent from factory
  [I15] adapters.zip: 'conf/images/ResourceKind/SynologyUps.svg' present in reference, absent from factory
  [I16] adapters.zip: 'conf/images/ResourceKind/SynologyVolume.svg' present in reference, absent from factory
  [I17] adapters.zip: 'conf/images/ResourceKind/SynologyWorld.svg' present in reference, absent from factory
  [I18] adapters.zip: 'conf/images/ResourceKind/synology_diskstation.svg' present in reference, absent from factory
  [I19] adapters.zip: 'synology_diskstation.jar' present in reference, absent from factory
  [I20] describe.xml: data kind count: factory=1, reference=9

Score: 2 BLOCKING, 3 WARNING, 20 INFO
```

## Gate status

| Gate | Status | Reason |
|---|---|---|
| Reference selection | **SATISFIED** | Independent reviewer approved the exact Synology release artifact as a structural comparator. |
| Comparison / RULE-005 | **NOT SATISFIED** | The approved comparison completed but returned B1 and B2. No finding was waived, suppressed, or reclassified. |
| First release / deployment | **NO-GO** | A clean comparison, CI-built `1.x+` artifact, remote/CI controls, approvals, and the separately authorized persistence experiment remain required. |

The blocking differences are evidence to investigate, not authorization to
change the POC. Whether the fixture-only POC should acquire a credential kind,
adapter-instance identifiers, or a traversal specification requires a separate
design decision and explicit implementation authorization.
