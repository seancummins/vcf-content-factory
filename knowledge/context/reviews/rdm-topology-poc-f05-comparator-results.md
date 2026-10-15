# F0.5 — schema-aware comparator implementation and artifact results

Date: 2026-10-14. Status: implementation and independent reviews complete.
Factory base revision: `95cc4b7df575f704fed4ee965e807c91edf621e0`;
implementation is an uncommitted working-tree change.

## Approved inputs and checksum verification

| Input | SHA-256 verified before comparison |
|---|---|
| Synology `vcfcf_sdk_synology_diskstation.1.0.0.30.pak` | `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1` |
| RDM POC `vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak` | `5354acc09b4afa5a2fad5aed9429adebd8fe0f0e751b0b64b909c59854381d61` |

Reference selection and release provenance remain those approved in
`knowledge/context/reviews/rdm-topology-poc-f01-reference-selection-review.md`.
The official release is
[v1.0.0.30](https://github.com/sentania-labs/vcf-content-factory-sdk-synology/releases/tag/v1.0.0.30).
The POC is a local-only development artifact, not reproducible from a factory
checkout alone; all assessment findings are summarized here. Neither PAK was
regenerated or altered during F0.5. Existing F0.3 adapter changes remain
outside the factory Git repository and are not part of this implementation.

## Comparison commands

Both commands use `PYTHONPATH=src .venv/bin/python -m
vcfcf_managementpacks pak-compare` with these positional inputs:

```text
content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak
tmp/reference_paks/vcfcf_sdk_synology_diskstation.1.0.0.30.pak
```

The first command supplies no policy flag, exercising the unchanged default.
The second adds:

```text
--policy structural --reference-sha256 beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1
```

These are offline comparisons against exact local inputs. Scratch paths above
identify execution inputs, not durable corpus dependencies; the release,
checksums and full results provide the audit evidence.

## Default legacy result

Exit status: **1**. All historical severities remain unchanged.

```text
pak-compare gate: FAIL (2 BLOCKING finding(s) against closest reference vcfcf_sdk_synology_diskstation.1.0.0.30.pak)

=== PAK COMPARE: vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak vs vcfcf_sdk_synology_diskstation.1.0.0.30.pak ===

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

## Explicit structural result

Exit status: **0**. Valid D1/D6 credential-presence
differences receive the approved structural policy evaluation after independent
contract validation. The original legacy report remains intact.

```text
pak-compare gate: PASS (0 BLOCKING against closest reference vcfcf_sdk_synology_diskstation.1.0.0.30.pak)

=== PAK COMPARE: vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak vs vcfcf_sdk_synology_diskstation.1.0.0.30.pak ===

Policy: structural/1
schema-contract: describeSchema 6.3.0 bounded credential contract; cleanroom-spec/02a Pass 10
candidate-sha256: 5354acc09b4afa5a2fad5aed9429adebd8fe0f0e751b0b64b909c59854381d61
candidate-identity: vcfcf_rdm_topology_poc
reference-sha256: beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1
reference-identity: synology_diskstation

WARNING (may cause issues):
  [W1] D8: describe.xml: adapter instance identifier count: factory=0, reference=3
  [W2] D23: describe.xml: TraversalSpecKind count: factory=0, reference=1
  [W3] D25: describe.xml: factory has empty TraversalSpecKinds, reference has entries

INFO (semantic or cosmetic differences):
  [I1] D1: describe.xml: CredentialKinds presence: factory has no <CredentialKinds>, reference has <CredentialKinds>; /AdapterKind/CredentialKinds or /AdapterKind/ResourceKinds/ResourceKind/@credentialKind: both independent credential contracts valid; optional declarations differ; candidate kinds=0, bindings=0, required=False; reference kinds=1, bindings=1, required=True
  [I2] D6: describe.xml: adapter instance (type=7): factory no credentialKind attr, reference credentialKind="synology_credentials"; /AdapterKind/CredentialKinds or /AdapterKind/ResourceKinds/ResourceKind/@credentialKind: both independent credential contracts valid; optional declarations differ; candidate kinds=0, bindings=0, required=False; reference kinds=1, bindings=1, required=True
  [I3] M7: manifest.txt: description differs: factory='Fixture-only proof of the VCF Operations Java SDK mechanics for an additive relationship from an existing VMWARE VirtualMachine to a pack-owned RdmMapping resource. This POC has no live vCenter or VCF Operations API collection, no CanonicalLun resource, and no production lifecycle behavior.', reference='Monitors Synology DiskStation NAS devices via the DSM Web API. Discovers storage pools, volumes, disks, iSCSI LUNs, NFS exports, and UPS. Collects capacity, performance, and health metrics. Cross-endpoint joining merges IO metrics onto the correct storage objects (Tier 2 trigger: complex data-model joining). Framework v2 (SPI: VcfCfTester/VcfCfCollector over AdapterBase; collect-path discovery via enumerateResources + discoverOnCollect, §22).'
  [I4] M7: manifest.txt: display_name differs: factory='VCF Content Factory RDM Topology POC', reference='VCF Content Factory Synology DiskStation'
  [I5] M7: manifest.txt: name differs: factory='VCF Content Factory RDM Topology POC', reference='VCF Content Factory Synology DiskStation'
  [I6] A1: adapters.zip: 'conf/images/AdapterKind/vcfcf_rdm_topology_poc.svg' present in factory, absent from reference
  [I7] A1: adapters.zip: 'conf/images/ResourceKind/RdmMapping.svg' present in factory, absent from reference
  [I8] A1: adapters.zip: 'conf/images/ResourceKind/vcfcf_rdm_topology_poc.svg' present in factory, absent from reference
  [I9] A1: adapters.zip: 'vcfcf_rdm_topology_poc.jar' present in factory, absent from reference
  [I10] A2: adapters.zip: 'conf/images/AdapterKind/synology_diskstation.svg' present in reference, absent from factory
  [I11] A2: adapters.zip: 'conf/images/ResourceKind/SynologyDisk.svg' present in reference, absent from factory
  [I12] A2: adapters.zip: 'conf/images/ResourceKind/SynologyDiskstation.svg' present in reference, absent from factory
  [I13] A2: adapters.zip: 'conf/images/ResourceKind/SynologyIscsiLun.svg' present in reference, absent from factory
  [I14] A2: adapters.zip: 'conf/images/ResourceKind/SynologyNfsExport.svg' present in reference, absent from factory
  [I15] A2: adapters.zip: 'conf/images/ResourceKind/SynologySsdCache.svg' present in reference, absent from factory
  [I16] A2: adapters.zip: 'conf/images/ResourceKind/SynologyStoragePool.svg' present in reference, absent from factory
  [I17] A2: adapters.zip: 'conf/images/ResourceKind/SynologyUps.svg' present in reference, absent from factory
  [I18] A2: adapters.zip: 'conf/images/ResourceKind/SynologyVolume.svg' present in reference, absent from factory
  [I19] A2: adapters.zip: 'conf/images/ResourceKind/SynologyWorld.svg' present in reference, absent from factory
  [I20] A2: adapters.zip: 'conf/images/ResourceKind/synology_diskstation.svg' present in reference, absent from factory
  [I21] A2: adapters.zip: 'synology_diskstation.jar' present in reference, absent from factory
  [I22] D17: describe.xml: data kind count: factory=1, reference=9

Score: 0 BLOCKING, 3 WARNING, 22 INFO
Gate: PASS
```

## Validation and review

The implementation changes these factory files; the independent adapter
repository and both comparison artifacts are unchanged:

| File | Change |
|---|---|
| `src/vcfcf_managementpacks/pak_compare.py` | Default-preserving policy dispatch, bounded credential validation on both inputs, native-Java/identity checks, upgrade regression checks, explicit reference digest and versioned audit reports. |
| `src/vcfcf_managementpacks/cli.py` | Public compare policy/digest options and build-gate configuration. |
| `src/vcfcf_managementpacks/buildkit.py` | Equivalent generated standalone buildkit CLI options and propagation. |
| `src/vcfcf_managementpacks/sdk_builder.py` | Same policy/reference/digest passed through the automatic gate; explicit new policies fail when evaluation cannot run. |
| `scripts/verify-tier2-sdk.sh` | Optional exact-reference/policy/digest invocation alongside historical two-argument usage. |
| `src/vcfcf_managementpacks/README.md` | Document policy scope, options, and gate requirements. |
| `tests/managementpacks/test_pak_compare_policy.py` | Synthetic matrix, CLI/build-gate propagation and isolated copied-buildkit checks. |

Interfaces:

```text
compare_paks(candidate, reference, *, policy="legacy", reference_sha256=None)
pak-compare CANDIDATE REFERENCE --policy structural --reference-sha256 SHA256
build-sdk PROJECT --pak-compare-policy structural --pak-compare-reference REFERENCE --pak-compare-reference-sha256 SHA256
```

The new policies reject invalid credential declarations, unresolved bindings,
implicit required credentials without a binding, invalid input/identity and
unsupported packaging. Structural mode requires an exact reference and digest;
it cannot select a lower-scoring reference from a directory. Upgrade mode
detects credential configuration regressions even when counts are unchanged.
All twenty former INFO findings and all three WARNING findings are retained.
Only valid D1/D2/D6 differences receive the approved structural INFO semantics;
there is no adapter-specific exemption or generic finding suppression.

Focused comparator tests report **129 passed, 3 skipped**. The independent
full factory suite (including slow tests, with `--override-ini="addopts="
-m ""`) reports **2298 passed, 14 skipped, 1 failed, 1 error**. It is not
reported as green:

- Failure: `tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`.
  This environment has `/tmp/.git`, an ancestor of pytest's temporary
  directories. The test assumes no such ancestor exists. The reviewer loaded
  the unchanged HEAD `setup_credentials` module and reproduced the same
  verdict as current code: its directory's Git safety cannot be determined.
  Neither the tested code nor the test changed in F0.5. No external Git
  metadata was removed to make the test pass.
- Setup error: `tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path`.
  The isolated wheel-build backend attempted to obtain missing setuptools
  build dependencies while network access was unavailable. Required local
  backend packages were absent; no dependency was installed and no test was
  weakened. This unrelated wheel-isolation check requires a suitably
  provisioned environment for a conclusive result.

Full content validation, Codex skill parity (5 paired, 7 Codex-only), path
reference audit and whitespace checks pass. Path audit emits only the existing
documented TVS and downstream `defects.local.md` standing-exception warnings.
The independent reviewer also compared the original HEAD comparator directly
with the current default: finding codes, order, severity, messages and formatted
legacy report match exactly for the supplied artifacts.

The framework implementation review is **APPROVE — 0 BLOCKING / 0 WARNING /
0 NIT implementation findings**, recorded in
`knowledge/context/reviews/framework/pak-comparator-modes-f05.md`. It records
the full-suite limitations explicitly and does not claim a green full suite.
The bounded SDK review is **APPROVE**, recorded in
`knowledge/context/reviews/rdm-topology-poc-f05-sdk-findings-review.md`.

The passing local structural result satisfies the local comparison sub-check
for the exact build-4 PAK. RULE-005 itself remains unchanged. E1.5 additionally
requires the pinned reviewed buildkit and the same explicit policy/reference/
digest in the automatic gate for the actual CI-built release artifact. That
official CI comparison and release-infrastructure gates remain pending.
Successful local comparison does not authorize installation or prove foreign
relationship persistence, instance creation, or UI topology visibility.

Recommendation: **CONDITIONAL GO for release-infrastructure preparation**.
Before any actual release,
repeat the full suite in an environment with the wheel backend dependencies
and without the unrelated Git-ancestor fixture conflict. F0.5 authorizes no
external GitHub action. Release and deployment remain NO-GO until their
remaining prerequisites and explicit authorizations are met.

