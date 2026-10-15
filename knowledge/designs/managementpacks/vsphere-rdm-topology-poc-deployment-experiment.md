# RDM topology POC — first controlled persistence experiment

## Status and decision

**Status:** E2 live POC mechanics demonstrated in the development lab,
operator-confirmed. The qualified closeout below is the current result;
the E1 procedure is retained as the original, stricter experiment plan.
This documentation update authorizes no further live activity.

## E2 closeout — operator-confirmed live result

Source: the operator's E2 closeout report in this conversation. No new live
API calls, log collection or screenshot inspection were performed for this
record. Exact collection timestamps/counts and the Operations build were not
supplied; no experiment date/window is reconstructed.

Installed **VCF Content Factory RDM Topology POC**, version **0.0.0.6**,
SHA-256 `0e77f1837cef68d6c40883fc5ff2359211307ef600940dd2ee140e25449aafc2`.
The operator used the development environment's unsigned-PAK installation
option. The package appeared in the Operations repository. This remains a
local development preview, not a production release.

The configuration UI exposed Runtime Fixture JSON. One Operations-managed
`fixture_json` held the exact Suite API-derived VM ResourceKey with
vCenter/MOID scope, credential-free configuration and one RDM mapping fixture.
Validate Connection succeeded; the instance displayed **Collecting** and
**Data Receiving**. The POC has no remote tester, vCenter discovery or authentication
code: Validate Connection is a UI observation, not proof of authenticated
vCenter collection or a separate identity-validation test.

The operator observed exactly one `RdmMapping`, with the existing VMware VM
as its parent in Operations topology. Existing VMware-owned topology remained
visible. The edge remained visible at subsequent checks after additional
elapsed collection time, and no duplicate mapping resources appeared. Lab
display names and raw identity values are intentionally omitted here.

```text
Existing VMWARE::VirtualMachine --(additive foreign-parent edge)--> RdmMapping
```

This is the first live confirmation of this POC's cross-management-pack
VM-parent mechanism. It demonstrates topology beyond a disk metric instance;
it is **not** a pass of every original persistence/cleanup criterion below.

### Acceptance matrix

PASS means the bounded observation stated, not a stronger inferred result.
NOT TESTED includes checks not independently verified or not recorded.

| Criterion | Result | Evidence / qualification |
|---|---|---|
| Scoped VM identity and exact ResourceKey fixture | PASS | Prior read-only identity proof retained; operator confirms exact key and vCenter/MOID configuration. Display names are not matching evidence. |
| Package acceptance and repository presence | PASS | Operator-confirmed installation of the checksum-pinned build using the lab unsigned option. |
| Runtime configuration field and credential-free instance acceptance | PASS | Field exposed, fixture configured, Validate Connection succeeded, Collecting/Data Receiving displayed. No remote-authentication claim. |
| Exactly one pack-owned mapping | PASS | One mapping observed; no duplicate mapping resources at later checks. |
| Existing VM is the mapping's parent in topology UI | PASS | Operator-confirmed foreign-parent edge; source implementation remains additive. |
| Existing VMware topology remains visible | PASS | Visual observation only, not a complete before/after relationship-set audit. |
| Relationship remains visible across subsequent checks | PASS | Observational persistence; exact elapsed time and completed-cycle counts not recorded. |
| Second completed POC collection preserves resource UUID and exact edge set | NOT TESTED | No cycle timestamps, resource-UUID comparisons or duplicate-edge API audit supplied. No duplicate resources were visually observed. |
| Edge survives a subsequent independently timestamped VMware adapter collection | NOT TESTED | VMware collection completion/order not independently verified. |
| Independent Suite API edge persistence and complete baseline topology/count comparison | NOT TESTED | No timestamped API before/after evidence supplied for this closeout. |
| Collector relocation/failover delivers the same fixture | NOT TESTED | Not exercised. |
| Mapping deletion, edge cleanup and return to baseline | NOT TESTED | Not exercised; installed resources are not claimed removed. Original rollback procedure remains unexecuted guidance. |
| Production vCenter discovery/authentication, LUN resource correlation and CanonicalLun | NOT TESTED | Not implemented in this POC. |

**Disposition:** successful initial live topology proof with qualified observed
persistence. Cycle-verified persistence, API verification and cleanup remain
open technical uncertainties, not failures concealed by the observed success.
No production-readiness claim is made.

### Evidence handling

The operator reports a topology screenshot in the conversation. No local
screenshot archive was verified and no screenshot file was created or cited.
If the operator wishes to retain it, a proposed local-only destination is
`e2-topology-redacted.png` in the ignored `tmp/rdm-lab-probes/` scratch area,
with owner-only permissions. This is a suggested future archive, not an
existing evidence artifact or reproducible repository citation. Redact raw
IDs, names where sensitive and unrelated inventory before sharing; do not
commit raw ResourceKeys, fixture JSON, credentials, tokens or inventory captures.

### Next technical milestone

Propose **RDM mapping to verified LUN identity**, retaining the proven
VM → mapping edge. See the
[lab-validation follow-up](vsphere-rdm-topology-lab-validation.md#next-proposed-increment--rdm-to-lun-identity)
for conditional reuse of an existing Operations LUN versus a pack-owned
`CanonicalLun`. No new collector or relationship work is authorized here.

## Original E1 experiment plan — retained for provenance

The preconditions and procedure below are the original plan, not a claim that
all were executed. The [E2-P lab-only evaluation](vsphere-rdm-topology-e2p-lab-evaluation.md)
documents the narrower development-preview path; this closeout adds no release
infrastructure or new governance requirements.

The first experiment is intentionally narrower than the production RDM design.
It tests whether the fixture-driven POC can create and retain exactly this
runtime edge:

```text
VMWARE::VirtualMachine --(additive relationship)--> vcfcf_rdm_topology_poc::RdmMapping
```

It does not test live RDM discovery, `CanonicalLun`, LUN correlation, metric
instances as topology endpoints, or production lifecycle/removal behavior.

The accepted identity prerequisite is a uniquely resolved existing Operations
VM carrying the real Suite API `VMEntityObjectID` and `VMEntityVCID`
identifiers, with their returned `isPartOfUniqueness` values preserved. The
same-MOID multi-vCenter case must never be resolved by MOID or display name
alone.

## Preconditions — all must be true before authorization

1. An approved, structurally relevant SDK reference PAK is locally available;
   `pak-compare` has run against it with zero BLOCKING findings. A skipped
   comparison is not sufficient.
2. The POC adapter repository has an operator-approved commit and the official
   candidate is built by its own CI release workflow. A local `0.x` PAK is a
   preview, not a release artifact.
3. An administrator explicitly approves the named development-lab change,
   its maintenance window, the fixture VM, and this rollback plan. That
   approval is separate from this document.
4. The operator has read privileges to enumerate the selected VM resource,
   its ResourceKey, relationships, and resource counts; installation and
   removal authority is held by a separately identified lab administrator.
5. The operator has a secure local location outside Git for sanitized reports
   and any short-lived resource UUID handoff. No password, token, raw API
   response, or raw inventory capture may enter either repository.
6. The pre-install identity proof is **unique**. Missing, ambiguous, or
   incomplete identity is a stop condition, not a reason to guess.

## Outcomes and evidence model

Keep API acceptance, persistence, and UI visibility separate:

| Outcome | Evidence | Pass condition |
|---|---|---|
| API acceptance | Installation/configuration task result and adapter logs, sanitized | Platform accepts the package and POC instance without an adapter error. |
| Runtime persistence | Bounded Suite API resource and relationship reads across collection cycles | Exactly one local `RdmMapping` resource and one edge from the proven VM to it remain present. |
| UI visibility | Topology view observation after the API result is stable | UI shows the same VM-to-mapping relationship; this does not substitute for API evidence. |

An accepted install alone is not a persistence pass. A UI-only observation is
not a topology persistence pass.

## Operator procedure

### 1. Establish immutable test inputs

1. Record the official POC candidate filename, SHA-256, adapter Git revision,
   factory revision, Operations build, and current time in the operator's
   change record. Do not put credentials or raw IDs in the record.
2. Select only the approved fixture VM in its owning vCenter. Display name may
   aid a human search but is never proof of identity.
3. Run the existing guarded `ops-vm-discovery` probe only after separate
   read-only-lab approval, using its secure local-only handoff mode. Accept
   only status `unique`; retain the actual Operations resource UUID only in
   the mode-0600 handoff file. The probe and its guards are documented in
   `scripts/rdm_lab_probe.py` and
   `vsphere-rdm-topology-lab-validation.md`.
4. Read the selected VM resource and prove that the returned resource key has
   the expected `VMEntityObjectID` + `VMEntityVCID` pair. Record names,
   uniqueness flags, and resource UUID only as sanitized fingerprints in the
   change evidence. Stop if either value is absent, the flags differ from the
   observed VMWARE key, or more than one candidate matches.

### 2. Capture the pre-install baseline

Using bounded, read-only Suite API requests for the one proven VM and a
bounded query for `vcfcf_rdm_topology_poc::RdmMapping` resources:

1. Capture the selected VM's complete relationship list and summarize it by
   related adapter kind/resource kind and count. Retain a stable fingerprint
   per relationship endpoint for exact before/after comparison.
2. Record counts for: the selected VM's relationships, all local POC
   `RdmMapping` resources, and POC adapter instances. Expected precondition:
   zero POC mappings and no POC relationship edge.
3. Capture the selected VM ResourceKey again immediately before installation.
   Abort if its VMEntity identity changes or becomes incomplete.
4. Save sanitized baseline output in the approved scratch location. Never
   write a raw response into the factory or POC repository.

### 3. Install and configure only after explicit approval

1. Reconfirm the candidate checksum and adapter kind against the approved
   change record.
2. Have the authorized administrator install only the approved POC candidate.
   Do not install a production RDM pack, alter VMWARE configuration, or add
   credentials/endpoints: the POC has none.
3. Create/configure at most one POC adapter instance, if the platform requires
   an instance to collect. Record the resulting POC instance identifier only
   as a fingerprint.
4. Wait for the first completed POC collection. If installation/configuration
   is rejected or collection fails, stop; preserve the error evidence and use
   the rollback procedure only if anything was created.

### 4. Test creation and additive topology

After the first collection, make bounded reads and require all of these:

1. Exactly one `RdmMapping` exists with the expected three identifier names.
   Its identifier values are compared locally to the deterministic fixture but
   reported only as fingerprints.
2. The selected, proven `VMWARE::VirtualMachine` has exactly one new relation
   to the pack-owned `RdmMapping`; it is not a relation to a metric instance.
3. The before/after set of VMware-owned relationships is unchanged. New
   non-POC relationships, missing baseline relationships, or a changed foreign
   VM identity are an immediate stop condition.
4. Record API acceptance, relationship-persistence state, and UI observation
   separately. The UI check occurs only after the API relationship is stable.

### 5. Test idempotence and persistence

1. Allow a second completed POC collection. Re-read POC mapping count and the
   selected VM relationship set. Require one mapping and one POC edge, with no
   duplicate edge or additional local resource.
2. Observe at least one subsequent completed VMWARE adapter collection, then
   repeat the same bounded relationship read. Require the POC edge and every
   baseline VMWARE relationship to persist.
3. If timing or asynchronous reconciliation makes a result transient, mark it
   inconclusive rather than passing it. Repeat only within the approved window;
   otherwise stop and roll back.

## Rollback and cleanup

Rollback is performed only by the authorized lab administrator and begins on
any stop condition or at experiment completion.

1. Capture a pre-removal snapshot of the selected VM relationship set and POC
   resource/instance counts. If any unexpected inventory change is already
   present, **stop** and escalate; do not uninstall or delete additional
   objects until the cause is understood.
2. Disable or remove only the POC adapter instance using the platform's normal
   management-pack workflow. Do not delete a `VMWARE` resource or use a
   bulk/topology cleanup operation.
3. Allow asynchronous inventory reconciliation to complete. Poll only the
   POC resource kind and the selected VM's relationship list at bounded
   intervals within the approved window.
4. Pass cleanup only when POC instance count and `RdmMapping` count return to
   their baseline values and the selected VM's relationship set matches its
   pre-install baseline. Record any platform-retained orphan separately.
5. If a POC edge or resource persists, or any VMware-owned relationship is
   absent or changed, stop all further cleanup, preserve sanitized evidence,
   and escalate to the platform owner. Never attempt to repair VMware topology
   manually.

## Acceptance criteria for an authorized E2

- The scoped VM is uniquely proven by real `VMEntityObjectID` plus
  `VMEntityVCID` and returned uniqueness flags.
- One local mapping and one additive VM-to-mapping edge are observed after the
  first collection.
- A second POC collection creates no duplicate resource or edge.
- At least one subsequent VMWARE collection does not remove the POC edge or
  alter baseline VMware relationships.
- API persistence and UI visibility are each recorded independently.
- Cleanup returns the lab to the recorded baseline, or a retained object is
  treated as an unresolved incident rather than silently accepted.
