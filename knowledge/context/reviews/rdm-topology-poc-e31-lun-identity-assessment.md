# E3.1 — existing Operations LUN identity assessment

**Disposition: INSUFFICIENT EVIDENCE.** Prefer reuse if one suitable existing
LUN is proven; neither REUSE nor creation of `CanonicalLun` is justified yet.
No live calls, adapter changes, builds or topology operations were performed.

## Evidence and inventory coverage

Basis: the [E2 closeout](../../designs/managementpacks/vsphere-rdm-topology-poc-deployment-experiment.md#e2-closeout--operator-confirmed-live-result),
[lab-validation record](../../designs/managementpacks/vsphere-rdm-topology-lab-validation.md),
existing probe source and offline inspection of saved sanitized reports.
The local-only reports `soap-first-run.json`, `soap-ops-vm-71.json` and
`ops-vm-71.json` under ignored scratch storage are not registry-fetchable or
reproducible repository evidence; their relevant findings are summarized here
without raw identifiers or fingerprint values.

| Question | Existing evidence | Confidence / limit |
|---|---|---|
| Which source LUN backs the RDM? | One VM, one RDM, one collected host and one matching current-host LUN view; `backing.lunUuid` equals `ScsiLun.uuid`; status `visible_on_current_host`. | High for the captured source join; not a fresh inventory check. |
| Canonical/durable identity available? | Matching LUN canonical-name class `naa`; durable namespace `NAA`, data present; three descriptor-ID fingerprints and nine alternate-name entries. | NAA identity evidence exists. Raw values/encodings were not retained in these reports; arbitrary WWN equivalence is unproven. |
| Backing identifiers available? | RDM `deviceName` and backing `fileName` present, fingerprinted only. | Diagnostic/context evidence, not globally unique LUN identity. |
| What storage-related Operations resources are observed? | Both saved VM-scoped reports contain related-kind counts `Datastore: 1` and `HostSystem: 1`. Other related kinds are network/status objects. | Observed related-kind labels only; the summary does not retain their adapter keys, complete ResourceKeys or properties. A Datastore is not proof of a LUN resource. |
| Is a native/third-party LUN kind populated in this lab? | No complete storage-kind census or candidate LUN resource capture exists in the inspected evidence. Cached VMWARE describe files are a subset, not an inventory census. | Unknown, not zero. No native LUN kind is assumed. |
| Does exactly one Operations resource match? | No candidate LUN key or candidate identity-property values are available. | Not assessed, not an absent/ambiguous match result. No display-name association is treated as proof. |

The VM-to-disk metric match and E2's observed VM → mapping edge remain valid
separate evidence. Neither proves a LUN endpoint. The secure runtime fixture's
documented schema contains the VM ResourceKey and RDM stable tuple only, not
the backing LUN UUID/canonical name. No raw identifiers were reconstructed from
fingerprints, and the private fixture was not copied into this record.

## Minimum additional evidence — requires separate read-only approval

Source requirements are grounded in `scripts/rdm_lab_probe.py` and the local
vendor specification `reference/docs/operations-api.json`. Suite API paths
below use base `/suite-api`; placeholders are real values held only in memory.
Do not execute these reads as part of this assessment.

1. **Reacquire one source identity in memory:** use the selected VM's owning
   vCenter `about.instanceUuid`, VM `config.instanceUuid`,
   `config.hardware.device`, `runtime.host`, `config.changeVersion`, and the
   current host's `config.storageDevice.scsiLun`. Select exactly the fixture's
   scoped VM/disk and one exact RDM backing; retain `lunUuid`, `deviceName`,
   `fileName`, matching host LUN `uuid`, `canonicalName`, namespaced durable
   name, descriptors and alternate names. Reuse the probe's completeness and
   end-snapshot checks; inaccessible/missing/unstable data is unresolved.
2. **Establish actual inventory coverage:** a complete paginated
   `GET /api/resources?page=<n>&pageSize=<bounded-size>` census, grouped by
   returned `resourceKey.adapterKindKey` and `resourceKindKey`, establishes
   populated kinds. Process in memory and retain only counts plus plausible
   storage candidates, not a raw whole-inventory dump. Enforce consistent
   `pageInfo.totalCount`, no repeated resources, no missing pages and explicit
   permission failures. If approval bounds the scan to a subset, record that
   limit rather than claiming an inventory-wide absence of LUNs.
3. **Inspect actual candidate kinds and objects:** use
   `GET /api/adapterkinds` and paginated
   `GET /api/adapterkinds/{key}/resourcekinds` as needed for discovered kind
   semantics/identifier definitions. These show supported kinds, not populated
   inventory. For plausible kind pairs use filtered
   `GET /api/resources?adapterKind=<actual>&resourceKind=<actual>&page=<n>&pageSize=<bounded-size>`,
   then `GET /api/resources/{id}` and `/api/resources/{id}/properties` for
   selected candidates. Inspect every identifier name, value/presence and
   uniqueness flag, plus the actual returned storage-identity properties;
   do not guess property keys or search by display name as final proof.
4. **Prove scope and granularity:** compare full source/candidate values
   directly in memory, preserving namespaces and any demonstrated array,
   vCenter or host scope. A name/NAA-looking label is not a direct identity
   match. A matching property can correlate the physical LUN, but does not
   replace the complete Operations ResourceKey needed for targeting. Distinguish
   a physical LUN from a host presentation, storage volume or datastore. Multiple
   host presentations or duplicate collectors may legitimately expose one LUN
   as several resources; never silently pick one as the canonical endpoint.
   Read the selected candidate's paginated
   `GET /api/resources/{id}/relationships?relationshipType=ALL` only if needed
   to establish that scope/ownership. Record timestamps and readable snapshot
   completeness; no guessed normalization or UUID↔NAA/WWN conversion.

Privileges: existing read-only VM/host/about access plus Operations resource,
kind, property and selected-relationship reads; no inventory write privilege
is required. Reuse the established token acquire/release lifecycle; release
changes authentication state only. Any later raw identity handoff must be
minimal, ignored, owner-only (`0700` directory / exclusive `0600` file), with
no overwrite, secrets, raw-response logging or fixture data committed. Reports
should contain completeness/scope, counts, fingerprints, match method and
confidence—not raw values. Direct equality, not fingerprint reconstruction,
is the identity test.

## SDK feasibility and recommended architecture

Conditional preferred model: **existing VM → RdmMapping → existing LUN**.
The POC owns only `RdmMapping`; the storage/VMware pack retains ownership of
the foreign LUN and all its definitions, metrics and existing topology.
Shared RDMs should converge on one proven LUN endpoint, not duplicate LUNs
per VM/host. The E2 VM-parent implementation remains unchanged.

Repository-backed mechanism: `RelationshipBuilder.childForeign(mappingKey,
lunKey)` supports a local parent/foreign child; use explicit
`buildDelta(false)` for additive output. **Do not infer additive semantics
from `childForeign(...).build()`**: its own-adapter mapping parent receives
`setRelationships` by default. Evidence:
`src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/stitch/RelationshipBuilder.java`.
No such call is added or executed here. E2 validates the VM foreign-parent
case, not candidate-specific foreign-LUN-child resolution or persistence.

Targeting requires the candidate's real adapter kind, resource kind and full
ResourceKey with actual flags; never hardcode VM identifier names onto a LUN.
Apply the [SDK value-preservation contract](../../designs/managementpacks/vsphere-rdm-topology-e22-empty-identifiers.md):
supported nonunique empty strings survive, but null/omitted entries cannot be
silently dropped or converted. Candidate key representability, uniqueness and
cross-collector persistence must still be established. No candidate currently
has that proof.

**Decision conditions:** REUSE only after one appropriately scoped/granular
resource has direct identity evidence and an exactly representable unique key.
If a complete authorized investigation establishes no suitable reusable object,
the planned adapter-owned `CanonicalLun` is justified only after validating
its stable storage identifiers and deduplication scope. Missing privileges,
partial inventory, ambiguous host views or conflicting IDs remain INSUFFICIENT
EVIDENCE—not reasons to manufacture a duplicate canonical object.

Independent technical review: **APPROVE, zero blocking findings**. The reviewer
independently checked the API paths against the local vendor specification and
additive builder behavior against framework source; no live access or builds.
Changed-document and full content validation passed; path-reference audit
passed with six documented standing warnings, and `git diff --check` passed.
No implementation or new live authorization follows from this report.
