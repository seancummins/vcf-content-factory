# RDM topology POC build 2 — independent SDK adapter review

**Reviewer:** `sdk-adapter-reviewer` (independent static/pre-install gate)  
**Adapter:** `content/sdk-adapters/rdm-topology-poc`  
**Candidate:** declared `0.1.0`, build `2`; locally built dev PAK
`0.0.0.2`  
**Verdict:** **APPROVE — 0 BLOCKING static findings.**

This approves only the reviewed local fixture POC mechanics. It is not an
installation or relationship-persistence approval: `pak-compare` has no
reference PAK to compare and the foreign-edge behavior remains unproven until
a separately authorized deployment test.

## Re-review of build-1 findings

### B1 — RESOLVED: fixture-only documentation now matches the implementation

`docs/installing.md` now explicitly says the POC has no endpoint,
credentials, network activity, live inventory collection, or connection
validation (lines 1–12), and forbids upload, installation, configuration, or
enablement without fresh explicit authorization (lines 14–24). This matches
`RdmTopologyPocAdapter` and `adapter.yaml`, which configure no endpoint or
credentials and contain no live client path.

This satisfies the docs-parity requirement in
`.claude/agents/sdk-adapter-reviewer.md` review dimension 11 and the gap
honesty direction in the `vcfops-sdk-adapter` skill. The old misleading
HTTPS/account/connection-validation scaffold is absent.

### B2 — RESOLVED: the documented focused-test command passes

The landing `README.md` now documents
`bash content/sdk-adapters/rdm-topology-poc/scripts/run-tests.sh` (lines
18–25). I ran that exact command with the supplied external SDK JAR and it
passed:

```text
RdmTopologyPocTest: PASS (6 tests)
```

The script remains mode `0644`, which is now harmless because the documented
command invokes it through `bash`. This resolves the prior command/document
contradiction under reviewer dimensions 9 and 11 and RULE-005
[`knowledge/rules/validate-before-install.md`](../../rules/validate-before-install.md).

## Independent validation

| Check | Result |
|---|---|
| `validate-sdk` | **PASS.** Five Java sources compiled using the supplied local `vrops-adapters-sdk-2.2.jar`. The only output was the known JDK 25 `-source/-target 11` module-location warning. |
| Documented focused test command | **PASS.** The six deterministic checks cover exact identifier flags, duplicate MOID across two vCenters, payload-repeatability, unresolved foreign identity rejection, local RDM identity, and additive/no-clear foreign-parent output. |
| `build-sdk` | **PASS.** Independently built `/tmp/rdm-poc-build2-review.6EPmvd/vcfcf_sdk_rdm_topology_poc.0.0.0.2.pak` (78,305 bytes). |
| PAK inspection | **PASS.** The package contains the POC adapter JAR, `describe.xml`, resources/icons, and `vcfcf-adapter-base.jar`; it does not contain the external Broadcom SDK JAR, credentials, tokens, or lab inventory. |
| `pak-compare` | **BLOCKED, not passed.** No reference PAK exists in `tmp/reference_paks`; an explicit empty reference directory returned `No .pak files found ...` with exit 1. The dev build correctly reported that it skipped comparison. |
| Live activity | **None.** No vCenter/VCF Operations request, installation, adapter instance, or topology mutation occurred. |

## Static correctness verification

- `ForeignVmIdentity` copies every provided foreign identifier and its actual
  `isPartOfUniqueness` flag into the `VMWARE` / `VirtualMachine` key and
  rejects input lacking a uniqueness-bearing `VMEntityObjectID` or
  `VMEntityVCID`
  ([ForeignVmIdentity.java](../../../content/sdk-adapters/rdm-topology-poc/src/com/vcfcf/adapters/rdmtopologypoc/ForeignVmIdentity.java)
  lines 18–74). It does not form an edge from a bare MOID or display name.
- The focused test independently exercises the two-vCenter same-MOID case
  ([RdmTopologyPocTest.java](../../../content/sdk-adapters/rdm-topology-poc/tests/com/vcfcf/adapters/rdmtopologypoc/RdmTopologyPocTest.java)
  lines 37–45) and the actual flag propagation (lines 24–35), meeting the
  requirements from `knowledge/lessons/stitch-moid-not-unique-across-vcenters.md`
  and `knowledge/lessons/cross-mp-foreign-key-uniqueness-flags.md`.
- `RdmMapping` retains precisely the intended stable local tuple:
  `vcenter_instance_uuid`, `vm_instance_uuid`, and `virtual_disk_key`
  (RdmMappingIdentity.java lines 9–34; `describe.xml` lines 13–21).
- The emitted relationship bytecode calls only
  `RelationshipBuilder.parentForeign(foreignVm, localMapping)`. Framework
  source routes that form through additive `Relationships.addRelationships`,
  not `setRelationships` on the VMWARE parent
  ([RelationshipBuilder.java](../../../src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/stitch/RelationshipBuilder.java)
  lines 178–198 and 318–354). The test asserts `isAdd()` and
  `!isClearFirst()`.
- The absence of any network/Suite API code is intentional and documented.
  Therefore test repeatability proves deterministic edge *emission*, not
  platform persistence or server-side duplicate handling. The design and
  documentation state that boundary correctly.

## Registry check

`knowledge/context/defects.md` was read for this review. No open defect has
`Affects: rdm-topology-poc`, `rdm`, or `vcfcf_rdm_topology_poc`. No closure is
proposed and no registry was modified, satisfying RULE-012
[`knowledge/rules/release-gate-defects.md`](../../rules/release-gate-defects.md).

## Remaining deployment prerequisites

1. Supply a suitable reference PAK and rerun `pak-compare` with zero
   BLOCKING findings.
2. Obtain explicit approval for a controlled deployment experiment.
3. Capture a pre-install VMWARE topology baseline, install only the approved
   POC, collect the fixture, and verify the resolved VM retains existing
   children while gaining exactly one local `RdmMapping` child.
4. Verify duplicate-add behavior, UI direction, first-collection timing,
   wrong-vCenter/ambiguous/unresolved identity handling, and safe POC cleanup
   before designing production lifecycle/removal semantics.

