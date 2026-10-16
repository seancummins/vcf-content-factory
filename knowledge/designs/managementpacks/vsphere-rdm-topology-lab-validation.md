# VCF Operations vSphere RDM topology — lab validation plan

## Status and scope

**Status:** read-only identity chain verified; the development build-6 POC's
foreign VM-parent edge is now operator-confirmed in topology and remained
visible at subsequent checks. Strict cycle/API persistence, failover and
cleanup are not yet verified. See the
[E2 closeout and acceptance matrix](vsphere-rdm-topology-poc-deployment-experiment.md#e2-closeout--operator-confirmed-live-result).

The read-only probe phases below validate source facts for the proposed Tier 2
`RdmMapping` and `CanonicalLun` resources; the probes do not create Operations
resources or relationships. The separately operated E2 POC installation did
create one mapping and its VM-parent edge. This update is documentation-only.

The target model remains:

```text
VMWARE::VirtualMachine --(additive foreign edge)--> RdmMapping --> CanonicalLun
```

`RdmMapping` is one association per virtual disk. `CanonicalLun` is a
pack-owned resource, not an assumed first-party VMWARE resource. A future
foreign LUN stitch is conditional on separate evidence for the target kind
and its real Suite API identity.

## Increment C evidence update (2026-10-14)

The approved read-only lab run verified the following facts for the initial
physical-mode RDM fixture (`vm-71`):

- `VirtualDiskRawDiskMappingVer1BackingInfo.lunUuid` exactly matched the
  hosting ESXi `ScsiLun.uuid`.
- The resolved host LUN had an NAA-class canonical name and an NAA
  durable-name namespace.
- The Operations VM resource was uniquely identified by the exact
  `VMEntityObjectID` (MOID) plus `VMEntityVCID` (vCenter
  `about.instanceUuid`) pair; both identifier flags were uniqueness-bearing.
- The RDM virtual disk matched one existing Operations virtual-disk metric
  instance through controller/unit, disk label, and backing filename, at high
  confidence. There were zero unmatched RDM mappings.

These read-only findings prove the source and identity chain only. A metric
instance is not an independently addressable topology resource. The later
E2 live topology observation is separate evidence for the SDK VM-parent edge,
not a reinterpretation of metric-instance correlation as topology. The
separate POC decision record is
`knowledge/designs/managementpacks/vsphere-rdm-topology-sdk-poc.md`.

## Provenance

- **Authored by:** Codex orchestration, API cartography, and independent SDK
  design review.
- **Evidence basis:** repository describe cache and cleanroom investigations;
  Broadcom vSphere Web Services and Virtual Infrastructure JSON API docs.
- **Vendor API evidence:**
  - `VirtualDiskRawDiskMappingVer1BackingInfo` exposes `lunUuid`,
    `deviceName`, and `compatibilityMode`; `fileName` is inherited from file
    backing. See [Web Services API](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.vm.device.VirtualDisk.RawDiskMappingVer1BackingInfo.html).
  - `HostStorageDeviceInfo.scsiLun[]` supplies the host LUN inventory, and
    `ScsiLun.uuid` is documented for identifying a LUN across servers. See
    [HostStorageDeviceInfo](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.StorageDeviceInfo.html)
    and [ScsiLun](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.ScsiLun.html).
  - The VIM JSON API documents the same RDM backing structure, but parity of
    its VM-config retrieval on the target release is deliberately unproven.
    See [VIM JSON RDM backing](https://developer.broadcom.com/xapis/virtual-infrastructure-json-api/latest/data-structures/VirtualDiskRawDiskMappingVer1BackingInfo/).
- **Factory evidence:**
  `knowledge/context/adapter_describe_cache/VMWARE/VirtualMachine.json`,
  `knowledge/context/authoring/recon_metric_keys.md`,
  `knowledge/lessons/cross-mp-stitch-cp-identity-and-edge-mechanics.md`, and
  `knowledge/lessons/cross-mp-foreign-key-uniqueness-flags.md`.

## Safety contract

The probe harness is [rdm_lab_probe.py](/home/scummins/Documents/vcf-content-factory/scripts/rdm_lab_probe.py).

- It defaults to an offline plan; network activity requires both `--execute`
  and `--allow-read-only-lab`.
- Secrets are accepted only from environment variables or the existing
  profile resolver. No password, token, or session cookie is accepted on the
  command line.
- It sends only authentication and read operations: SOAP
  `RetrievePropertiesEx` / `ContinueRetrievePropertiesEx`, VIM JSON `GET`,
  and Suite API token/read/release calls.
- It neither writes raw responses nor prints raw VM names, MOIDs, filenames,
  LUN identifiers, URLs, tokens, or credentials. Output uses deterministic
  fingerprints, presence flags, and counts. An optional report is created
  mode `0600`; it is still lab inventory and must remain untracked.
  The separate explicit `fixture-export` mode writes raw validated identities
  only to its fixed ignored `0600` local handoff, never a report or terminal;
  see the [E2.2 contract](vsphere-rdm-topology-e22-empty-identifiers.md).
- The operator supplies a small fixture set through environment variables;
  the probe never inventory-scans an entire vCenter.

## Fixture set

Choose explicitly authorized test VMs in one vCenter:

1. One VM with a physical-compatibility RDM.
2. One VM with a virtual-compatibility RDM.
3. Two VMs sharing one RDM, if the lab has a supported fixture.
4. One VM without an RDM as a negative control.
5. An intentionally inaccessible/masked LUN fixture only if it already
   exists; the probe must not create one.

Set selected VM MOIDs in `RDM_PROBE_VCENTER_VM_MOIDS`; do not supply names.
Set selected Operations VM resource UUIDs in `RDM_PROBE_OPS_RESOURCE_IDS`
only after they have been chosen by the lab operator. Values remain in the
environment and are fingerprinted in output.

## Required access

Exact RBAC labels are target-version-dependent and must be confirmed by the
administrator. The effective minimum is:

| System | Read requirement |
|---|---|
| vCenter | Selected VM configuration/hardware and runtime host; selected host `config.storageDevice.scsiLun`; service-instance about data. |
| VCF Operations | Token acquisition plus read access to VMWARE `VirtualMachine` resources and their ResourceKeys, plus selected resources, statkeys, bounded stats, properties, and relationships. |

Permission denial is a probe result at the affected phase. It must not cause
a fallback join or a claim that a LUN is absent.

## Probe phases

### A. SOAP baseline

Use one SOAP session and bounded `RetrievePropertiesEx` pages.
Every requested VM, requested property path, and selected host response must
be present and readable. A `missingSet`, VIM fault, absent object, or absent
required path is an incomplete probe result, not an empty inventory or a
zero-RDM finding.

| Object | Requested property paths | Required extraction |
|---|---|---|
| Selected `VirtualMachine` MORs | `config.hardware.device`, `runtime.host`, `config.changeVersion` | For an exact RDM backing type: virtual-disk key, controller key, unit number, label, `lunUuid`, `deviceName`, `fileName`, `compatibilityMode`. |
| Current `HostSystem` MORs only | `config.storageDevice.scsiLun` | `uuid`, `canonicalName`, `deviceName`, descriptor, durable-name, and alternate-name evidence. |
| Selected VMs, end check | `runtime.host`, `config.changeVersion` | Mark `snapshot_unstable` when host/config changes during the snapshot. |

Primary correlation hypothesis: normalized `backing.lunUuid == ScsiLun.uuid`
within one vCenter. The report distinguishes a UUID observed anywhere among
the collected VM hosts from a UUID visible on the VM's current ESXi host. A
global match does not establish current-host accessibility. `deviceName` is
host-local diagnostic evidence only.
`canonicalName`, descriptors, and durable names are preserved as opaque
evidence. No namespace is called a WWN without a separate proof.

Expected global join statuses are `exact_uuid_one_host_lun`,
`exact_uuid_multiple_host_views`, `missing_rdm_lunUuid`,
`no_host_lun_match`, `canonical_conflict`, and `snapshot_unstable`.
Current-host visibility is reported independently as `visible_on_current_host`,
`not_visible_on_current_host`, `current_host_canonical_conflict`, or the
corresponding missing/unstable status.
`no_host_lun_match` is unresolved: it can include masking or an inaccessible
LUN, but the probe deliberately does not claim it can distinguish those
causes without further source evidence.

### B. Operations resource and metric-instance observation

For each selected Operations VM resource, use only public Suite API reads:

1. `GET /resources/{id}`: capture identifier type names and actual
   uniqueness flags. This is the future foreign VM-key source.
2. `GET /adapterkinds/VMWARE/resourcekinds/VirtualMachine/statkeys`: capture
   declared `virtualDisk|*` fields and instance type.
3. `GET /resources/{id}/stats?begin=<one-hour-epoch-ms>&end=<epoch-ms>`:
   discover realized `virtualDisk:<instance>|<leaf>` keys.
4. `GET /resources/{id}/properties`: observe only `virtualDisk:` properties
   and RDM/VMDK counts. The cleanup `POST /api/auth/token/release` releases
   only the authentication token; it does not alter monitored inventory.
   A cleanup failure is reported separately and never replaces the primary
   collection result.
5. `GET /resources/{id}/relationships?relationshipType=ALL`: summarize
   existing resource topology only.

The test candidates are controller bus + unit number to `scsi<bus>:<unit>`,
then vCenter disk key, label, backing filename, LUN UUID, and corresponding
realized Operations property values. These comparisons occur only in memory;
the report carries the matching method, confidence, and fingerprints—not raw
identifiers. A candidate is accepted only when uniquely matched across the
fixture data and repeated in a second collection. It is not a resource
identity.

There is no evidence that a metric instance has a `ResourceKey` or can be a
relationship endpoint. The adapter will create relationships to the resolved
VM resource, not to a disk metric instance.

### B.2 Combined SOAP-to-Operations disk correlation

`--mode soap-ops` runs the existing SOAP phase and the existing Operations
phase sequentially, without the VIM JSON phase or its session-header
requirement. The SOAP phase keeps each raw RDM mapping only in memory and
passes it directly to `_ops_probe(profile, mappings=...)`.

Before comparing an Operations `virtualDisk:<instance>` metric with a SOAP
disk, the harness requires the Operations resource's exact
`(VMEntityObjectID, VMEntityVCID)` pair to equal the SOAP VM MOID and the
SOAP service-instance UUID. This prevents disk-key collisions across VMs or
vCenters from becoming correlations. A resource with incomplete identity or
no matching SOAP VM is reported as such and receives no disk comparison.

For each RDM of a correctly identified VM, the sanitized report records
matches with method, confidence, disk-key fingerprint, instance fingerprint,
and observed metric leaves. It also records unmatched RDM mappings and
unmatched Operations disk instances. `missing_instance_data` means no
`virtualDisk:` metric instance was present; `no_candidate_identifier_matched`
means instances were present but none matched a SOAP disk identifier. Neither
outcome is a zero-RDM finding.

After explicit approval for a lab read, the operator supplies the existing
selected VM and Operations-resource environment values, then uses:

```bash
.venv/bin/python scripts/rdm_lab_probe.py --execute --allow-read-only-lab \
  --mode soap-ops --profile devel \
  --output tmp/rdm-lab-probes/soap-ops-sanitized.json
```

### B.1 Operations VM discovery and identity proof

The environment has multiple vCenters, so a VM MOID such as `vm-71` is only
a candidate locator. It is never a VM identity by itself, and a display name
is never proof.

The explicit opt-in discovery mode uses only documented, read-only SOAP and
public Suite API operations:

1. The existing authenticated SOAP session reads
   `ServiceInstance.RetrieveContent().about.instanceUuid` in memory. This is
   the target vCenter discriminator; it is fingerprinted in the report and
   never printed.
2. `GET /api/resources?adapterKind=VMWARE&resourceKind=VirtualMachine&page=<n>&pageSize=1000` pages every matching VM resource. Each response must have a consistent `pageInfo.totalCount` and a complete `resourceList`; pagination or shape failures stop as incomplete.
3. For every returned resource, inspect `resourceKey.resourceIdentifiers[]`
   in memory, retaining the identifier name, value, and
   `isPartOfUniqueness` flag. The sanitized report carries identifier names,
   flags, and value fingerprints only.
4. Prove a candidate only when both exact, raw values match: supplied target
   MOID equals `VMEntityObjectID`, and the vCenter service-instance UUID
   equals `VMEntityVCID`. The harness does not parse, normalize, or otherwise
   assume the format of `VMEntityVCID`; the live response supplies that
   evidence.

An optional `RDM_PROBE_TARGET_VM_DISPLAY_NAME` is a discovery aid: matching
names are returned as candidates but cannot promote a result to `unique`.
The result is one of `unique`, `ambiguous`, `absent`, or `incomplete`.
`unique` is the only state eligible for a handoff. The report never prints
the actual Operations resource UUID or raw identifier values.

For the approved lab run, ensure the existing vCenter and Operations profile
environment variables are present, then set the selected VM MOID (for the
current fixture, `RDM_PROBE_TARGET_VM_MOID=vm-71`) and run:

```bash
RDM_PROBE_TARGET_VM_MOID='vm-71' \
.venv/bin/python scripts/rdm_lab_probe.py --execute --allow-read-only-lab \
  --mode ops-vm-discovery --profile devel \
  --output tmp/rdm-lab-probes/ops-vm-discovery-sanitized.json \
  --handoff-output tmp/rdm-lab-probes/ops-vm-resource-id.json
```

The optional handoff file is created only for one explicit `unique` match,
under the existing scratch-directory guard, with exclusive creation and mode
`0600`. It contains only `RDM_PROBE_OPS_RESOURCE_IDS` for the operator to
load locally into the later read-only metric probe; it is neither printed nor
tracked. A token release is still a `POST /api/auth/token/release` cleanup
only: it releases authentication state and does not modify monitored
inventory.

### C. VIM JSON parity

With the same selected VMs and a version explicitly supplied by the operator,
retrieve the documented VIM JSON VM configuration representation. For every
SOAP RDM disk, assert that JSON retains an RDM backing discriminator and
equal presence/value fingerprints for `lunUuid`, `deviceName`, `fileName`,
and `compatibilityMode`. The probe recognizes the documented
`hardware.device` array and its boxed `_value` array form only; any other
device/backing representation is `unsupported_or_unrecognized`, never a
zero-RDM result. Any HTTP/auth/schema error, missing subtype, or
field mismatch leaves SOAP as the transport baseline.

## Decision criteria

| Decision | Pass condition | Consequence if it fails |
|---|---|---|
| SOAP source | Typed RDM backing and required fields on physical and virtual fixtures | Stop; no adapter source contract yet. |
| Canonical LUN correlation | Exact `lunUuid`/`ScsiLun.uuid` join and canonical-name consistency across host views | Keep `RdmMapping` unresolved; do not create `CanonicalLun`. |
| VM metric association | One unique, repeatable metric-instance association per disk across two samples | Use only as UI/diagnostic correlation; never as a topology endpoint. |
| VIM JSON transport | 100% field/subtype parity over all fixtures | JSON may be selected later; otherwise SOAP remains baseline. |
| VM relationship mechanism | A later devel SDK proof persists an additive edge using the Suite API-returned real VM ResourceKey | Do not create relationships. |

## Follow-up gates

After a successful read-only run, record only the sanitized result and
decision in a reviewable design/update artifact. Before implementation,
obtain a dedicated SDK review of mapping lifecycle (removed disk, backing
replacement, shared LUN, vMotion) and the adapter's additive foreign-edge
path. Adapter creation, build, installation, and any configuration change
remain separate explicit approvals.

## Next proposed increment — RDM-to-LUN identity

The offline [E3.1 assessment](../../context/reviews/rdm-topology-poc-e31-lun-identity-assessment.md)
records **INSUFFICIENT EVIDENCE**, the observed storage-related kinds and exact
additional read-only evidence needed; it does not approve live access or
CanonicalLun creation.

The [E3.2 operator procedure](vsphere-rdm-topology-e32-lun-discovery.md) adds an
explicit read-only LUN-discovery mode. Its offline implementation does not
establish live LUN inventory or authorize any topology modification.

The [E3.3 CanonicalLun architecture](vsphere-rdm-topology-e33-canonical-lun.md)
records the subsequently operator-reported discovery outcome and proposes global
logical-unit identity. Actual LU-designator qualification remains a prerequisite;
the design neither proves native LUN absence nor changes the installed POC.

The [E3.4 qualification procedure](vsphere-rdm-topology-e34-identity-qualification.md)
adds operator-initiated SOAP descriptor/reference comparison and bounded
cross-host observation. Live identity qualification remains BLOCKED pending
capture; no CanonicalLun or new topology is emitted.

The existing VM → `RdmMapping` edge is the proven starting point. The missing
storage endpoint is **not yet an established Operations LUN resource kind**.
Neither a related Datastore nor a Virtual Disk metric instance proves that a
LUN object exists; metric instances are not independent relationship endpoints.

Prefer reusing an existing native or third-party Operations LUN **if** its
actual kind, complete ResourceKey/flags and storage identity yield one exact,
unambiguous match. That avoids duplicate LUN representations and reuses the
storage pack's existing topology. No suitable existing kind or unique binding
has been established; lack of evidence is not proof that none exists.

The previously approved pack-owned `CanonicalLun` remains the fallback/initial
design target, not an assertion that such a native kind exists. Its stable
identity must be supported before implementation; do not create one per VM,
host or RDM mapping for the same proven LUN merely for convenience.

Proposed sequence, for a later separately authorized technical increment:

1. Inspect available resource-kind documentation/describe evidence, then, only
   with read authorization, inventory candidate Operations LUN objects. Record
   ownership and exact identity semantics, not guessed kind/attribute keys.
2. Reuse the verified SOAP `backing.lunUuid == current-host ScsiLun.uuid` join
   and its NAA canonical/durable-name evidence. Correlate those opaque source
   identities to candidate LUN resources without guessed normalization.
   NAA-class evidence does not establish arbitrary WWN equivalence or global
   uniqueness across arrays/vCenters. Do not join by display name, bare MOID,
   host-local device name or LUN number alone.
3. If exactly one existing LUN is proven, propose an additive
   `RdmMapping → existing LUN` edge while preserving that resource's ownership,
   full key and existing topology. Verify the relevant foreign-LUN relationship
   mechanism independently; the foreign-VM-parent proof does not establish it.
4. Otherwise retain an explicit unresolved mapping. If no suitable existing
   resource is established and identifiers are validated, propose the planned
   local `RdmMapping → CanonicalLun` edge. Never choose the first ambiguous
   candidate, fabricate a storage ID or create a duplicate as an ambiguity fix.

The resulting logical chain is `existing VM → RdmMapping → verified LUN`,
where the endpoint is either an existing resource **or** the justified
adapter-owned canonical resource, not automatically both. Shared RDMs should
converge on one validated LUN endpoint. Cross-host/vCenter identity stability,
vMotion, inaccessible LUNs and array identity conflicts remain design/test
questions; an absent read is unresolved, not evidence of storage deletion.

Next-increment acceptance should require unique LUN correlation (or explicit
unresolved status), no duplicate endpoint for a shared fixture, unchanged
VM/foreign topology and repeatable additive links. Discovery/authentication,
production lifecycle, timestamped persistence and cleanup still need their
own technical work; none is implemented or executed by this closeout.
