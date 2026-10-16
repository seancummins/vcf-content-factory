# E3.5 — Minimal fixture-driven CanonicalLun POC

**Historical offline assessment: build 8 subsequently failed installation.**
The operator reported illegal flat attribute keys in its descriptor; build 6
remains registered. See the [E3.5.1 correction](vsphere-rdm-topology-e351-descriptor-compatibility.md).
Do not retry build 8. The results below preserve the original offline evidence,
not a claim that the rejected descriptor was platform-compatible.
This extends the [approved architecture](vsphere-rdm-topology-e33-canonical-lun.md)
using the [E3.4.1 conditionally qualified evidence](vsphere-rdm-topology-e341-integer-compatibility.md).
Single-host evidence does not establish global identity stability or production
deduplication. E2's live VM-parent proof remains distinct from this offline work.

## Implementation and compatible fixture contract

The independent adapter repository remains at
`content/sdk-adapters/rdm-topology-poc`, separate from the factory Git repository.
Its new `CanonicalLunIdentity.java`, versioned `RuntimeFixture.java`, adapter
collection code, descriptor/resources, tests and documentation implement:

`existing VMWARE::VirtualMachine → owned RdmMapping → owned CanonicalLun`

- Build-6 unversioned `{foreign_vm,mapping}` remains mapping-only, unchanged.
  Opt-in v2 uses `{"schema_version":"2","attachments":[...]}`. Each attachment
  contains the complete original `foreign_vm`, unchanged mapping tuple, and a
  `canonical_lun` evidence object. No synthetic values become runtime defaults.
- The sole unique LUN identifier is
  `identity_token=scsi-vpd83:naa:<complete-lowercase-NAA-payload>`: no vCenter,
  host, VM, virtual-disk key or adapter-instance scope. This is an unscoped key
  design, not proof of cross-instance/platform-wide resource merging.
- Complete binary VPD83 NAA5/6 descriptors must prove LU association, namespace,
  type and length; exactly one eligible identity must agree with canonical name
  and independently supplied storage reference. Backing UUID must exactly equal
  observed SCSI UUID. Port/target descriptors cannot qualify a LU. Malformed,
  missing, conflicting or ambiguous evidence fails before any resource emission.
- All attachments validate first. Duplicate mapping keys, contradictory VM
  identities, UUID/token conflicts and inconsistent same-token properties fail
  closed. Equivalent observations reuse one owned LUN key and discovery result.
- Existing foreign `parentForeign(...).build()` remains additive. Owned
  `parent(mapping,lun).buildDelta(false)` adds the local edge. No resource clears,
  relationship removals or VMware-owned resource emission are introduced.
- Only verified optional vSphere vendor/model/revision/serial/LUN/device-type
  and capacity properties are exposed, with fixture provenance. Capacity requires
  positive, bounded dimensions and product. No host presentation name, array
  endpoint, authentication, node-local runtime file or production discovery.

The adapter's `docs/canonical-lun-fixture.md` is the exact schema and synthetic
example. Existing parser limits still apply: at most eight attachments within
32,768 characters, 512 values, depth 12 and 4,096-character strings. Required
VMEntityVCID and VMEntityObjectID remain unique and vCenter-scoped; all other
Suite API identifiers and their supported value-presence semantics are retained.

The current docs generator models traversal declarations and cross-MP metadata,
not owned runtime-only edges. Hand-maintained overview/fixture documents and
post-generation landing/inventory supplements explicitly show the local edge;
the generated SVG does not. Restore those supplements after future builds.
No false cross-MP declaration or framework change was introduced. These final
source-checkout prose supplements do not change the build-8 PAK contents/hash.

## Secure offline operator preparation

The new factory helper `scripts/rdm_prepare_canonical_fixture.py` combines the
existing exact-key VM fixture, private E3.4 evidence and independent storage
reference. It checks exact vCenter/VM-instance/disk-key/MOID correspondence and
replays qualification, then validates the entire result with the actual Java
parser before exclusive output creation. No API calls or fingerprint reversal.

Run from the factory root, only with the existing approved local SDK and inputs:

```bash
VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
PYTHONPATH=src .venv/bin/python scripts/rdm_prepare_canonical_fixture.py \
  --vm-fixture tmp/rdm-lab-probes/rdm-fixture-vm-71.json \
  --lun-evidence tmp/rdm-lab-probes/lun-identity-private-vm-71.json \
  --storage-reference tmp/rdm-lab-probes/storage-reference.json \
  --output tmp/rdm-lab-probes/rdm-canonical-fixture-vm-71.json
```

Inputs must be ignored, untracked, owner-owned mode-0600 regular files directly
inside mode-0700 scratch. The independent reference has the existing private
`{"naa":"<operator-supplied-storage-reference>"}` shape; do not invent it.
Output must not exist; no overwrite, symlink or paths outside scratch. Failure
prints static stage labels, not payloads or exception values. No real fixture
was generated in E3.5. Stop on stale/missing/mismatched evidence rather than
guessing identifiers. Never print or commit the payload.
The helper has no age-based freshness gate: current evidence is an operator
responsibility. Parser validation proves internal consistency, not truthful
acquisition, authenticity or present-day inventory.

After separate installation/reconfiguration approval, supply its contents through
the existing Operations-managed `fixture_json` field, not appliance-node files.
Configuration storage is cluster-independent by design; failover is untested.
Do not retarget a running instance: obsolete-edge/resource reconciliation is
not implemented.

## Offline validation and artifact

Candidate: `dist/vcfcf_sdk_rdm_topology_poc.0.0.0.8.pak` in the independent
adapter repository; build 8 supersedes intermediate build 7, not an approved
release. SHA-256:

`de78efc3715244a1f2b101c721ff9ab70cdfd22a728cf84a9e4fca167e04d849`

Approved Synology v1.0.0.30 reference SHA-256:

`beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`

| Check | Result |
|---|---|
| Java topology/runtime/CanonicalLun deterministic tests | Passed; seven original topology tests, 42 invalid-runtime cases, 34 invalid-LUN cases and positive/convergence/conflict/idempotence/property matrices |
| Java 11 production compilation; validate-sdk | Passed |
| build-sdk, explicit pinned structural policy | Passed |
| Package integrity, credential-free descriptor, restricted SDK exclusion | Passed; only adapter/framework JARs, no SDK/test/fixture payload |
| Independent rebuild | All 73 recursively unpacked leaves identical; ZIP timestamps differ, not byte-reproducible archive hash |
| New offline helper tests, actual Java parser | 14 passed |
| Seven RDM probe/helper suites, SDK enabled | 319 passed / 1 skipped |
| Full factory suite, normal environment | 2463 passed / 20 skipped / 131 deselected / 1 unchanged failure |

The unchanged failure is
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`;
no unrelated correction was made. SDK descriptor-loader runtime test cannot run
without log4j-api; DOM metadata checks and actual SDK compilation pass.

Structural comparison: **0 BLOCKING / 3 WARNING / 23 INFO**, exit 0. W1: adapter
instance identifier count 1 vs 3; W2: TraversalSpecKind count 0 vs 1; W3: empty
TraversalSpecKinds vs populated reference. No findings suppressed or reclassified.
INFO comprises two valid optional-credential differences, three manifest values,
17 adapter-specific JAR/icon differences, and the two-vs-nine data-kind count.
Default legacy still produces its historical credential blockers; the approved
first-release gate explicitly uses structural/1, not a waived legacy result.

Independent reviews: [SDK implementation](../../context/reviews/rdm-topology-poc-e35-build-8.md)
and [offline fixture helper](../../context/reviews/framework/rdm-canonical-fixture-e35.md),
both APPROVE with zero implementation findings. Full content validation, skill
parity, diff checks and path audit passed; path audit retains six documented
standing exceptions. No staging,
commits, pushes, live requests, adapter configuration or installation occurred.

## Remaining controlled E3 experiment

Require separate explicit authorization for the identified artifact and a
securely prepared, current scoped fixture. Reuse the existing E2 baseline and
rollback procedure; this increment adds no release infrastructure.

1. Capture exact existing VM/mapping keys, resource counts and VMware-owned
   relationships privately before installation/configuration. Confirm the v2
   mapping key is identical to the E2 key.
2. Expect the same VM and mapping plus exactly one owned CanonicalLun and the
   additive mapping-parent → LUN-child edge. Check API acceptance, persisted
   relationship data and UI visibility as separate outcomes.
3. Repeat POC collection with timestamps: no duplicate owned resources/edges.
   Independently timestamp a later VMware collection and recheck both edges and
   preservation of all baseline VMware-owned topology.
4. Two synthetic mappings converge offline; live convergence requires separately
   qualified genuine observations. Cross-host, cross-vCenter, repeated identity,
   collision handling, collector failover and production lifecycle remain untested.
5. Stop on wrong VM/LUN, duplicate resources, missing/mutated VMware topology or
   contradictory evidence. Quiesce the POC and use conservative approved cleanup
   of owned resources/edges only; never delete VMware resources. Verify eventual
   cleanup, not assumed uninstall behavior. Additive collection does not remove
   obsolete edges automatically.
