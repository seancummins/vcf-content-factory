# E2-P — minimal development-lab evaluation

**E2.1 follow-up:** the build-4 limitation below is historical. The runtime
configuration implementation, build-5 checksum and operator loading steps are
in the [E2.1 addendum](vsphere-rdm-topology-e21-runtime-fixture.md). Use that
candidate's configuration and review disposition with the unchanged experiment
and rollback steps below; build 4 itself remains unsuitable. No live execution
is authorized by either document.

**BLOCKED for the VM relationship experiment: build 4 has no real-lab fixture
binding. Not blocked on release CI.** This is preparation only; no live access
or installation is authorized or performed by this document.

## Artifact and technical blocker

Existing local-only preview: `vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak`, SHA-256
`5354acc09b4afa5a2fad5aed9429adebd8fe0f0e751b0b64b909c59854381d61`.
This local-only artifact is not registry-fetchable. Offline reinspection confirmed
ZIP/JAR integrity, credential-free metadata and exclusion of the Broadcom SDK.
The approved Synology comparison was rerun: **exit 0,
0 BLOCKING / 3 WARNING / 22 INFO**. Warnings remain: no adapter-instance
identifiers and no traversal declarations. Instance acceptance and UI navigation
are still experimental, not guaranteed by packaging/tests.

However, the packaged `RdmTopologyFixture.class` contains synthetic vCenter
and VM-instance UUIDs and a fixed disk key. The
[fixture source](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/blob/160f6461541ca312708ee880f3b5837b7ccfd312/src/com/vcfcf/adapters/rdmtopologypoc/RdmTopologyFixture.java)
is compiled data. The
[adapter](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/blob/160f6461541ca312708ee880f3b5837b7ccfd312/src/com/vcfcf/adapters/rdmtopologypoc/RdmTopologyPocAdapter.java)
ignores instance configuration and emits the compiled synthetic ResourceKey.
Matching `vm-71` alone is insufficient. The Python probe's UUID handoff is
**not consumed by this adapter**.

**Minimum instance configuration today:** one POC account/instance with a
display name and designated development collector, no endpoint, credentials,
or custom identifier fields. **Fixture-loading procedure today: none exists.**
Environment variables/JSON cannot override build 4. Packaging permits a smoke
test, not a meaningful real-VM topology proof. Do not change VMware identity to
fit the fixture or manually add an edge to manufacture a pass.

Smallest prerequisite change: a bounded, credential-free lab fixture binding
using the already validated real VM ResourceKey entries/flags plus the real
vCenter UUID, VM instance UUID and RDM disk key. Keep fixture inputs outside Git;
no live collector is needed. Specify/test its loading contract and produce
a **new numbered local development PAK**, not an in-place build-4 patch. No
adapter change is authorized here; no loading command/path exists to document.

## Proposed lab-only boundary

For one development Operations instance, proven VM, POC account and bounded
window, replace precondition 2 of the
[existing E2 experiment](vsphere-rdm-topology-poc-deployment-experiment.md)
with acceptance of a checksum-pinned, locally validated **0.x preview**.
This proposed project-plan exception requires user acceptance, not a rule
change: RULE-014 already permits temporary development testing of 0.x artifacts.

No 1.x release/tag, factory registration/publication, protected runner, release
workflow activation, GitHub policy remediation or new reviewer/ceremony is
required. Reuse existing reviews; official release controls remain unresolved,
not passed or waived. Keep checksum/provenance, full pre-install validation,
zero-BLOCKING structural comparison, secret protection, unique VM identity,
preservation of VMware-owned edges and verified cleanup.

One later execution authorization names the lab, checksum, fixture VM/window
and covers snapshots, POC installation/account collection and POC-only cleanup.
It excludes vCenter collection, VMware account/configuration changes,
replacement of VM relationships and production use. No live call is approved now.

## Minimum prerequisites and offline commands

- Fix the fixture binding above; capture the exact resulting artifact/hash.
- Operator has resource/relationship read and POC install/account/removal
  privileges; no adapter credentials or dummy credentials.
- Unique VM proof uses `VMEntityObjectID` **and** `VMEntityVCID`, preserving
  every returned ResourceKey identifier and uniqueness flag. Reuse approved
  local probe evidence; refresh only under the later live-access authorization.
- Baseline has zero POC accounts/mappings and no previously installed POC;
  stop rather than overwrite an existing pack or downgrade a release.
- Keep identifiers/session data outside Git in restrictive scratch storage;
  report fingerprints/counts only. Bound the window, e.g. 30 minutes including cleanup.

From factory root, these **offline build-4 checks** are safe now; they do not
clear the fixture blocker or authorize installation:

```bash
sha256sum content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak
scripts/validate-changed-content.sh --all
PYTHONPATH=src .venv/bin/python -m vcfcf_managementpacks pak-compare \
  content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak \
  tmp/reference_paks/vcfcf_sdk_synology_diskstation.1.0.0.30.pak \
  --policy structural \
  --reference-sha256 beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1
```

For a corrected candidate, repeat its focused tests/SDK validation and these
gates with its own filename/hash; retain all warnings. Do not rebuild under the
existing build-4 version or promote it into a release.

## Short operator experiment — conditional, NOT executable with build 4

Use the platform UI for installation/account management and an approved,
authenticated Suite API client for the following reads. Do not put tokens in
commands. API paths below include `/suite-api`; follow **all** pages using
`page`/`pageSize` and verify totals before treating a list as complete.

1. **Before upload:** prove the loaded fixture matches exactly one existing
   `VMWARE::VirtualMachine` ResourceKey, including its actual flags; verify the
   mapping's real stable identity tuple. Missing loading support or any mismatch
   stops here. Record POC/VMWARE resource counts and complete baseline edge sets.
2. **Snapshot reads:** `GET /suite-api/api/resources/{vmId}`;
   `GET /suite-api/api/resources/{vmId}/relationships/children` and
   `/relationships/parents`; and
   `GET /suite-api/api/resources?adapterKind=vcfcf_rdm_topology_poc&resourceKind=RdmMapping`.
   Use the same resource query for `VMWARE` / `VirtualMachine` counts. Locally
   fingerprint endpoint IDs/kinds and compare complete sets, not counts alone.
3. **Install/configure:** in the management-pack repository UI, Add/Install
   from disk only the approved candidate, verify displayed kind/version and
   finish the task. Select the POC's Add Account action; create exactly
   one instance, no endpoint/authentication. If the UI demands credentials,
   stop. Use only the corrected candidate's documented fixture-loading action;
   no such action exists in build 4.
4. **Collect:** start only the POC account; allow its normal collection
   (descriptor interval five minutes). Confirm an actual completed cycle in
   account/log evidence, not simply elapsed time or Test Connection success.
5. **First result:** repeat the reads. Require exactly one `RdmMapping` with
   the expected three identifiers, exactly one new POC edge from the proven VM,
   unchanged VMWARE resource identities/counts and unchanged non-POC baseline
   edges. Inspect the VM and mapping topology views separately. This is a
   resource relationship, not a metric-instance relationship.
6. **Repeat:** after a second completed POC cycle, require the same mapping
   UUID and endpoint pair, one resource and no duplicate edge. Then observe a
   naturally completed VMware adapter cycle **after edge creation**, without
   reconfiguring that adapter; re-read and require persistence. Record three
   distinct outcomes: installation/API acceptance, persisted API edge, UI
   visibility. Missing UI traversal is not proof the API edge failed, or vice versa.
7. **Cleanup:** stop POC collection first; capture final evidence and remove
   only its account through the UI. If a mapping remains, remove only the
   positively identified pack-owned mapping through normal object deletion,
   within the proposed POC-only cleanup authorization and only if it has no
   unexpected dependents. Uninstall only the POC, never VMWARE/built-in packs.
   Allow asynchronous reconciliation, then repeat baseline reads: zero POC
   accounts/mappings/edges and all original VMWARE objects/edges preserved.
   Uninstallation alone is not proof of cleanup. No step authorizes deleting
   VMware resources or replacing/repairing their owned relationships.

## Stop and rollback

Stop collection on identity ambiguity/mismatch, incomplete inventory, install/
configuration/collection error, more than one mapping, absent/wrong/duplicate
edge, unexpected object/edge change, unavailable cycle evidence or window expiry.
Missing persistence is a failed/inconclusive result, not permission to hand-wire
relationships. API/UI disagreement is recorded separately, never concealed.

If VMware-owned topology changed, **freeze further cleanup and escalate to the
lab owner**; do not PUT a replacement child list or delete a VM to restore it.
Otherwise perform step 7. If ownership/deletion scope is uncertain, cleanup
would affect dependents, or an orphan/edge persists after bounded reconciliation,
stop and report unresolved cleanup; never claim baseline restored. Reuse the
existing E2 rollback detail, with the explicitly scoped own-object cleanup above.

**Decision: BLOCKED on fixture binding and later lab execution authorization.**
No CI infrastructure is needed. Reuse the
[F0.3 build-4 review](../../context/reviews/rdm-topology-poc-f03-credential-free-review.md)
and [F0.5 comparison](../../context/reviews/rdm-topology-poc-f05-comparator-results.md).
The full content-validation chain, skill parity and path audit passed during
E2-P (six existing path-audit warnings). No new review gate, adapter/workflow
change, commit, publication or live request was introduced.
