# API evidence map: vSphere canonical logical-unit identity

## Provenance

- **Authored by:** api-cartographer (independent E3.3 research context).
- **Target instance:** none; no VMware/Operations endpoints contacted.
- **Last updated:** 2026-10-15.
- **Update history:**
  - 2026-10-15 — Initial offline identity/descriptor map for CanonicalLun design.
- **Evidence basis:** cited Broadcom API/KB documentation, T10 public technical
  proposals/tutorials, existing sanitized repository findings. T10 proposals are
  historical primary explanatory sources, not claims of conformance certification.
- **Notes:** no raw lab inventory or private fixture files inspected; no code changes.

## vSphere fields and their limits

| Source field | Documented meaning / design consequence |
|---|---|
| `ScsiLun.uuid` | Cross-server LUN identity and join to other host storage views; preserve as an opaque UUID, not a guessed NAA encoding. [documented in S1] |
| `ScsiLun.canonicalName` | Optional disk name used by partition/extent references; its string alone does not establish designator association or assignment authority. [documented in S1; design inference] |
| `ScsiLun.descriptor[]` | IDs and quality indicators; hosts can expose different order/selection. Some descriptors are host-local. Do not pick index zero or treat all descriptors as global. [documented in S1, S2] |
| `durableName`, `alternateName[]` | Optional names derived from VPD pages 80h/83h. Preserve namespace and namespaceId separately. [documented in S1, S3] |
| `vendor`, `model`, `revision`, `serialNumber`, `displayName`, `lunType` | Descriptive data; optional fields can be absent. Display name is configurable/nonunique; serial is derived from page80 when available. No array-volume-name guarantee. [documented in S1] |
| `HostScsiDisk.capacity` | LBA dimensions; retain block count and block size and derive bytes with checked arithmetic, not an assumed sector size. [documented in S4, S5; design inference] |
| `deviceName`, `devicePath`, `operationalState`, `queueDepth`, `localDisk` | Host presentation/operational observations, not global ResourceKey fields. `localDisk` can be unknown. [documented in S1, S4; design inference] |

SCSI logical units are not necessarily external array volumes. Retain type/locality
evidence; unsupported local/unknown devices must not become purported external
volumes automatically. [inferred from docs S1, S4]

## Durable-name decoding prerequisite

`ScsiLunDurableName.data` contains a descriptor header **and** payload for page83,
but payload only for page80. `namespaceId` is ESXi's namespace byte, **not** the
SCSI designator-type field. Do not hex-encode the entire data array and call that
an NAA/WWN; do not interpret a page80 serial as a page83 descriptor. [documented
in S3; design inference]

For a supported page83 representation, validate its four-byte descriptor header,
declared payload length, binary code set, designator type, and association. LU
association `00b` is distinct from target-port `01b` and target-device `10b`.
NAA type `3h` and EUI type `2h` can describe any of these entities; a port WWN
must not merge all LUNs behind that port. [documented in S7, tables295–298]

Keep descriptor bytes unchanged as evidence; equality keys use the validated
type and complete payload bytes, excluding presentation/header differences.
Any signed-byte conversion preserves bits and byte order. Namespace-to-page
representation recognition still needs real vSphere examples and parser tests;
unrecognized structures remain unresolved. [proposed policy; unverified runtime]

## Conservative global identity policy recommendation

- Accept validated, LU-associated IEEE NAA2/5 (8 bytes) or NAA6 (16 bytes), or
  EUI designators with supported lengths 8/12/16 bytes. Include format and full
  length/payload in identity; never truncate EUI extensions. NAA3 is locally
  assigned: exclude it from unscoped global deduplication. [documented in S7–S9;
  proposed allowlist]
- An implementation may initially support a narrower tested subset (for example
  NAA5/6); other valid formats remain unresolved, not misclassified as invalid.
  [proposed policy]
- Compare canonical `naa.`/`eui.` hexadecimal payload to independently decoded LU
  descriptor bytes. Permit only representation-level hex case handling after
  strict syntax validation; never convert opaque SCSI UUID/VML strings into NAA.
  Reject partitions/path syntax for whole-LUN identity. [proposed policy; S10]
- MPX/runtime path, LUN number, VM UUID, disk key, host MOR, and vCenter UUID
  cannot establish global LU identity. T10 vendor-ID and page80 serial require
  additional assignment/scoping proof before support, not a blanket assertion
  that these standards are inherently nonglobal. [proposed conservative scope;
  S7, S10, S11]
- Different valid designators can be aliases of one LU. Co-observation on the
  same verified host LUN can support an alias set, but no substring, common
  vendor/model/capacity, namespace label, or name resemblance can. Conflicting
  overlapping alias groups require quarantine; do not transitively merge them
  or silently rekey an emitted resource. [proposed policy]

Standards-based uniqueness assumes conformant storage assignment. Replicas or
misconfigured/cloned devices can reuse identifiers: contradictory observations
must be reported, not papered over by adding host/vCenter scope to a resource
called global. Storage-administrator mapping from device ID to array volume
remains external confirmation, not an array API dependency. [design limitation]

## Existing evidence and minimum empirical gaps

The [lab record](../../designs/managementpacks/vsphere-rdm-topology-lab-validation.md)
and [E3.1 assessment](../reviews/rdm-topology-poc-e31-lun-identity-assessment.md)
establish exact RDM backing `lunUuid` → current-host `ScsiLun.uuid`, an NAA-class
canonical name, and NAA durable namespace. They do **not** establish parsed
LU-associated designator bytes, cross-host/cross-vCenter equality, or storage
administrator recognition. The current `_lun_view` in `scripts/rdm_lab_probe.py`
redacts bytes and does not retain namespaceId/association. [existing repository
evidence; offline inspection]

Before global-key implementation, obtain separately authorized read-only SOAP
observations of the matched current-host LUN: uuid/canonicalName, complete
durable/alternate names including namespaceId/data, descriptor IDs/quality,
vendor/model/display/type, LBA capacity, locality, observation time and source
scope. Decode in memory, emit only format/length/association, match booleans and
fingerprints. Secure raw evidence remains ignored/local. Repeat on a second
host, and if shared storage is actually presented there, a second vCenter;
repeat over time. Absence of such presentation is NOT a failed equivalence
test. [proposed minimum evidence plan; not executed]

Future VMFS join: `HostVmfsVolume.extent[].diskName` references the canonical
disk name; join within that host view, then reuse the same qualified global LU
identity. Preserve partition separately; a datastore can span several extents.
No datastore discovery is implemented here. [documented in S1, S12, S13; design]

## Primary sources

- **S1:** [ScsiLun](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.ScsiLun.html).
- **S2:** [ScsiLunDescriptor](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.ScsiLun.Descriptor.html).
- **S3:** [ScsiLunDurableName](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.ScsiLun.DurableName.html).
- **S4:** [HostScsiDisk](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.ScsiDisk.html).
- **S5:** [HostDiskDimensionsLba](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.DiskDimensions.Lba.html).
- **S7:** [T10/05-003r2, page83 designators](https://www.t10.org/ftp/t10/document.05/05-003r2.pdf), tables295–301, clauses7.6.3.1–7.6.3.6.
- **S8:** [T10/06-002r2, IEEE OUI tutorial for SCSI](https://www.t10.org/ftp/t10/document.06/06-002r2.pdf), clauses1.1–1.2 (format lengths/header layouts).
- **S9:** [T10/07-216r1, NAA locally assigned](https://www.t10.org/ftp/t10/document.07/07-216r1.pdf), NAA table and scope limitation.
- **S10:** [Broadcom KB316540, identifying disks](https://knowledge.broadcom.com/external/article/316540/identifying-disks-when-working-with-vmwa.html).
- **S11:** [Broadcom KB344351, storage visibility and identifier specifics](https://knowledge.broadcom.com/external/article/344351/cannot-see-some-or-all-storage-devices-i.html).
- **S12:** [HostScsiDiskPartition](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.ScsiDisk.Partition.html).
- **S13:** [HostVmfsVolume](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.VmfsVolume.html).
