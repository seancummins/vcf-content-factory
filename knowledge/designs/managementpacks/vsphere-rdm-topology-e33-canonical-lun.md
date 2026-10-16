# E3.3 — CanonicalLun and global storage identity

**Decision proposal:** retain Tier 2 and design a pack-owned logical-unit endpoint,
qualified by storage identity rather than VM/host/vCenter scope. **Not ready for
global-key implementation:** actual LU designator bytes remain an empirical
prerequisite. No adapter/probe changes, builds or live requests in this increment.

## Basis and limits

Source of API semantics and primary-source citations:
[canonical-LUN API map](../../context/api-maps/vsphere-canonical-lun-identity.md).
Repository evidence: [E2 closeout](vsphere-rdm-topology-poc-deployment-experiment.md#e2-closeout--operator-confirmed-live-result),
[lab-validation record](vsphere-rdm-topology-lab-validation.md),
[E3.1 assessment](../../context/reviews/rdm-topology-poc-e31-lun-identity-assessment.md),
and [E3.2 discovery contract](vsphere-rdm-topology-e32-lun-discovery.md).

- **Lab verified:** RDM backing `lunUuid` equals current-host `ScsiLun.uuid`;
  canonical name is NAA-class and durable namespace is NAA. Exact VM scope/key
  and VM → RdmMapping UI topology are proven; persistence was observed without
  timestamped cycle counts or independently confirmed VMware collection ordering.
- **Operator-confirmed E3.2:** 16 storage candidates examined, zero exact scoped
  matches, no directly matching native LUN kind in caller-visible inventory.
  Property semantics/coverage remain incomplete: Operations does not categorically
  lack LUN objects. No fingerprints are reversed into raw identifiers.
- **Documented, not lab verified:** VPD83 encoding/association semantics and
  global-assignment formats described in the API map. Existing sanitized probes
  did not retain descriptor bytes/namespaceId sufficient to qualify a global key.
- **Proposed:** CanonicalLun is a vendor-independent vSphere-visible logical unit,
  not an assertion about an array's internal object model. The user now requests
  this portable endpoint architecture independently of native-inventory coverage;
  its justification is not an inferred absence of native resources. This design
  neither changes the installed POC nor selects between future native/owned modes.

## Identity and conservative deduplication

`ScsiLun.uuid` remains an opaque source join identifier, not a key derived by
UUID↔NAA conversion. `canonicalName` is a whole-device reference, not by itself
proof of assignment authority or LU association. Preserve both as observations.

1. Recognize a documented VPD83 representation before decoding. Durable-name
   page83 data includes descriptor header and payload; page80 has different
   representation. `namespaceId` is not the SCSI designator type. Preserve byte
   order/bits when converting signed bytes. Unknown encoding is unresolved.
2. Validate the complete header and declared length, binary code set (`1`),
   LU association (`0`), and designator type (NAA `3`, EUI `2`). Port/target-device
   WWNs never identify a LUN. A namespace label alone is insufficient.
3. **Initial proposed support: IEEE NAA5 (8-byte payload) or NAA6 (16-byte payload),**
   with matching type nibble and nonzero, complete valid payload. Compare with
   strictly parsed whole-device `naa.` canonical payload. Only hexadecimal
   presentation case may change; no prefix stripping from arbitrary strings,
   partition/path truncation, byte reordering or synthetic padding.
4. NAA2 and EUI (8/12/16-byte forms) are documented global-assignment families,
   but initial support is deferred until their actual vSphere representation and
   deterministic tests are available. NAA3 is locally assigned and ineligible
   for unscoped deduplication. T10 vendor-ID/page80 serial formats require further
   assignment/scope proof; do not declare them inherently nonglobal. MPX, VML,
   LUN numbers and host paths are not substitute global keys.
5. Require exactly one distinct eligible identity per observation. Duplicate
   presentations of the identical descriptor are one identity; two different
   eligible payloads are ambiguous even if co-observed. Do not choose the first,
   lexicographically smallest or highest-priority member of a changing set.
6. Proposed token: `scsi-vpd83:naa:<full-lowercase-payload-hex>`; payload length
   and NAA nibble distinguish supported forms. This is a **new pack contract**,
   not an existing vendor identifier. Equivalence means exact validated token
   equality, never substring, display name, vendor/model/capacity similarity or
   arbitrary UUID conversion. Retain original representations as evidence.
7. Co-observed alternate designators are evidence, not automatic merge aliases.
   No transitive alias bridging, silent token promotion/rekeying or merging of
   previously emitted resources. A later broader identity policy requires an
   explicit migration design, not a new candidate-selection preference.

Standards-based uniqueness assumes conformant storage assignment. Clones,
replicas or misconfiguration may reuse identifiers. Incompatible simultaneous
observations quarantine the affected identity/association; adding vCenter/host
to the key would hide the conflict rather than create a global logical unit.
Same opaque SCSI UUID with different qualified tokens, or one qualified token
with incompatible LU observations, is quarantined—not split/merged by a winner.
Missing/conflicting identity leaves RdmMapping unresolved, not attached to a
guessed CanonicalLun. Preserve the already-proven VM parent.

## ResourceKey and properties

Proposed owned adapter kind: existing `vcfcf_rdm_topology_poc`; new resource kind:
`CanonicalLun`. Exactly one uniqueness-bearing identifier, `identity_token`,
contains the qualified token. **Exclude** vCenter UUID, VM UUID, disk key, host,
path, LUN number, collector and adapter-instance ID. Display name may show the
full recognizable `naa.<payload>`; it is nonunique presentation, not identity.
The existing RdmMapping identity remains vCenter UUID + VM instance UUID + disk key.

All keys below are **proposed new pack-owned properties**, not assertions of
existing Operations property/stat keys. Source fields are documented in the map.
Scalar metadata is string-valued; capacity is a checked integer byte count.
Multi-observation lists require a deterministic string serialization contract
before implementation; this design does not assert native list-valued properties.

| Proposed property | Source / handling |
|---|---|
| `identity|format` | Validated `naa5` or `naa6`; immutable for an emitted key. |
| `identity|canonical_name` | Full validated whole-LU canonical name, recognizable to storage administrators. |
| `identity|observed_scsi_uuids` | Provenance-tagged exact `ScsiLun.uuid` values; opaque aliases, not automatic equivalence. |
| `identity|alternate_designators` | Validated type/association/payload plus raw-evidence provenance; no automatic merge authority. |
| `storage|vendor`, `storage|model`, `storage|revision` | Optional SCSI descriptive fields; publish consensus only, otherwise explicit conflict/unknown. |
| `storage|serial_number` | Optional page80-derived serial; not a substitute for identity. |
| `storage|lun_type`, `storage|device_type` | Distinct `ScsiLun.lunType` and inherited `HostDevice.deviceType`; neither substitutes identity. |
| `storage|capacity_bytes` | HostScsiDisk LBA blocks × blockSize with checked positive arithmetic; unknown if unavailable, conflict if inconsistent. |
| `identity|assessment` | Qualified, incomplete or conflict; never convert failed reads to a healthy/empty value. |

Keep host-specific display name, deviceName/devicePath, descriptor quality,
runtime host, LUN number, paths, operational state, queue depth and locality in
provenance-tagged presentation observations, not a single asserted global value
or a ResourceKey. Capacity/vendor/model are logical-unit descriptions observed
through hosts, not guaranteed immutable consensus: capacity expansion is possible;
an unexplained simultaneous mismatch requires investigation, not automatic split.
Do not claim a local/unknown-type device is an external array volume. Preserve
locality/type uncertainty. Array volume/pool names and array serial numbers are
not guaranteed by vSphere; customer recognition is through full NAA/other
qualified designators. No array endpoint, authentication or SDK is required.

## Relationship direction, ownership and repeated discovery

```text
Existing VMWARE::VirtualMachine → owned RdmMapping → owned CanonicalLun
                   many VM attachments converge on one qualified logical unit
```

Preserve the existing foreign VM ResourceKey exactly and its additive
`parentForeign(vm, mapping).build()` mechanism. For the **two owned kinds**, use
`parent(mapping, lun).buildDelta(false)` on a separate builder. `childForeign`
is unnecessary. `parent(...).build()` would replace that parent's child set;
it is not the additive variant. Source:
`src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/stitch/RelationshipBuilder.java`.

Register each unique owned key once and explicitly deduplicate `(parent, child)`
edges per complete collection. The helper caches single-ID keys but appends
children to lists; it does not deduplicate all repeated edges. Bound output
before emitting; do not treat relationship-cap truncation as successful complete
topology. Same token/input must yield identical keys/edges over repeated cycles.
Local-additive persistence and multiple-parent convergence still require a
separately authorized deployed test; E2's foreign-parent result is not that proof.

## Multi-host, multi-vCenter and lifecycle

- Join RDM to current-host LUN using exact backing lunUuid → ScsiLun.uuid first;
  a matching UUID on another host does not prove current-host accessibility.
  Decode that host observation; different hosts/vCenters converge only on the
  same qualified global token. Source scopes remain provenance, not identity.
- Start with **one logical inventory authority** covering approved sources,
  aggregating before emission. Do not launch eight independent per-vCenter
  writers for one shared global endpoint. Operations cross-instance resource
  deduplication/ownership and multi-writer behavior are unproven; no instance ID
  is added to disguise them. Collector relocation must use durable Operations
  configuration/state, never node-local identity files.
- Missing host, inaccessible LUN, partial PropertyCollector result or failed
  source is **unknown**, not removed. Retain last-known association with stale
  evidence and no new wrong edge. Conflicting observations block new attachment
  to the affected identity; surface conflict rather than silently picking a host.
  Visibly mark retained associations stale/unresolved; they do not prove current
  host accessibility or present attachment availability.
- Future reconciliation needs complete successful snapshots, durable last-seen
  ownership, a conservative grace period and exact owned-edge removal. SDK
  `buildDelta(true)` supports explicit removals statically; runtime behavior,
  ordering and cleanup are untested. Never replace VMware-owned relationship sets.
  Attachment removal/retargeting must eventually remove obsolete mapping→LUN
  edges, not merely add the new one. Shared LUNs are not deleted because one
  mapping disappears; no automatic CanonicalLun garbage collection in the next POC.

## Future VMFS reuse

HostVmfsVolume extent `diskName` joins the same host's canonical disk name;
retain partition separately, then resolve the qualified global token. A datastore
can span multiple extents/LUNs and one LUN may have several consumers: design
many-to-many associations, not one-LUN-per-datastore identity. CanonicalLun remains
independent of consumer kind. No datastore collector/relationships are implemented.
Future native-LUN stitching can retain the owned identity bridge if a complete,
uniquely resolvable native key is proven; no duplicate-free native inventory claim.

## Minimum next validation and recommendation

1. Separately authorize fresh read-only SOAP capture of exactly the proven
   current-host RDM LUN: complete durable/alternate namespace, namespaceId/data,
   descriptor IDs/quality, canonical name, UUID, type/locality, descriptive fields
   and LBA dimensions. Decode in memory; keep raw evidence ignored/owner-only.
2. Prove header representation, LU association, binary code set, payload type/
   length and canonical-payload equality. Sanitized output: format/length,
   association, equality booleans, completeness/conflict and fingerprints only.
   Reject malformed, port-associated, NAA3, conflicting and unsupported samples.
3. Repeat on another host seeing the same LUN, and another vCenter **only if the
   same storage is actually presented there**; repeat timestamped observations.
   Verify positive convergence and negative distinct-LUN cases. An unavailable
   shared presentation is NOT a failed equivalence test; cross-vCenter empirical
   proof remains pending. Have the storage administrator recognize the designator
   without requiring an array API. Never infer equivalence from fingerprints.
4. After evidence qualifies the narrow policy, propose a minimal synthetic/runtime
   fixture CanonicalLun POC: two mappings→one LUN, stable repeated output, strict
   conflict rejection, no duplicate keys, additive local edges, unchanged VM edge.
   Separately test deployed acceptance, UI/API topology and controlled cleanup.

**Recommendation:** next increment is read-only designator qualification and
deterministic decoder tests, not a production collector. Global CanonicalLun
implementation is **BLOCKED on actual VPD representation/association proof**;
cross-host/cross-vCenter and stability claims remain explicitly untested. No
adapter modification or live action is authorized by this architecture.
