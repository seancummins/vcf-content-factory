# E3.3 — independent CanonicalLun architecture review

**Verdict: APPROVE — zero BLOCKING findings.** Design-only review, adapted from
the SDK reviewer contract; not adapter implementation, build, deployment or
production-readiness approval. Reviewed 2026-10-15 in an independent context.

Scope: [architecture](../../designs/managementpacks/vsphere-rdm-topology-e33-canonical-lun.md)
and [API evidence map](../api-maps/vsphere-canonical-lun-identity.md). Authority:
SDK skill sections *ARIA_OPS stitching identity* and *Gaps — name them*,
RULE-001/002 (grounded semantics), RULE-008 (evidence safety), RULE-015/017
(provenance), and the shared reviewer doctrine.

## Independently verified

- Broadcom's [ScsiLun documentation](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.ScsiLun.html)
  describes cross-server UUID correlation, optional canonical names and variable
  descriptor selection. The design preserves UUID as opaque evidence rather
  than guessing a conversion to NAA. Final source-precision revisions were
  rechecked: lunType/deviceType are separate, property serialization is not
  invented, conflicting UUID/token observations quarantine and retained stale
  associations do not claim current accessibility.
- [ScsiLunDurableName](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.ScsiLun.DurableName.html)
  distinguishes page83 header/payload from page80 data; namespaceId is not a
  substitute for decoding association/type. The cited T10 page83 proposal's
  tables 295–298 distinguish LU, target-port and target-device designators.
  Narrow NAA5/6 support, full payload equality, no host-local/global fallback,
  no changing-set preference and no automatic alias merging are conservative.
- The proposed sole unique token excludes VM, host, path and vCenter; unchanged
  RdmMapping identity retains its vCenter/VM/disk scope. Missing or conflicting
  evidence cannot create a guessed endpoint. Descriptive values are not keys.
- Framework source
  `src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/stitch/RelationshipBuilder.java`
  confirms `parent(mapping, lun).buildDelta(false)` emits additive local edges;
  `parent(...).build()` instead emits a full child set. `childForeign` is not
  needed for two owned kinds. The existing adapter's foreign-parent mechanism
  is preserved. The helper does not deduplicate child-list entries itself.
- One logical inventory authority, unresolved cross-instance ownership,
  conflict quarantine and explicit future removal avoid pretending a global
  key alone proves safe multi-writer behavior. Additive output is not cleanup.
- E2 observations are not promoted to timestamped/API/failover proof. The
  operator-confirmed E3.2 counts do not establish categorical native-LUN
  absence. VMFS extent integration remains future work, not implemented behavior.

## Prerequisites, not newly discovered defects

Global-key implementation remains **BLOCKED** on actual durable-name bytes,
recognized representation, decoded LU association and canonical-payload equality.
Cross-host/cross-vCenter convergence, repeated stability, customer recognition,
local-edge deployed persistence and lifecycle cleanup remain empirical gaps.
The document names them and proposes minimum separately authorized evidence.
No relevant open RDM defect was found in `knowledge/context/defects.md`; no
registry closure or severity change is proposed.

## Offline checks and consequence

Independently ran changed-content checks for both reviewed documents and the
complete content chain: exit 0. Path-reference audit: exit 0, six existing
documented standing warnings. No Java tests/builds/PAK comparisons are claimed
or applicable to this documentation-only increment. No raw local lab evidence,
credentials or VMware endpoints were accessed.

**If used as-is:** a subsequent author receives a bounded, evidence-first global
identity contract, not permission to emit CanonicalLun resources immediately.
Proceed to separately approved read-only designator qualification and deterministic
decoder tests; do not change the installed POC from this review.
