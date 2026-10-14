# VCF Operations vSphere RDM topology — lab validation plan

## Status and scope

**Status:** proposed, approved for read-only lab validation only.

This plan validates the source facts needed for the proposed Tier 2
`RdmMapping` and `CanonicalLun` resources. It does not create an adapter
repository, an adapter instance, a VCF Operations resource, a relationship,
or a vCenter configuration change.

The target model remains:

```text
VMWARE::VirtualMachine --(additive foreign edge)--> RdmMapping --> CanonicalLun
```

`RdmMapping` is one association per virtual disk. `CanonicalLun` is a
pack-owned resource, not an assumed first-party VMWARE resource. A future
foreign LUN stitch is conditional on separate evidence for the target kind
and its real Suite API identity.

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
| VCF Operations | Token acquisition plus read access to selected resources, their ResourceKeys, statkeys, bounded stats, properties, and relationships. |

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
