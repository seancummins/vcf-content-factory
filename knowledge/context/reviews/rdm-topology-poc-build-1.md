# RDM topology POC build 1 — independent SDK adapter review

**Reviewer:** `sdk-adapter-reviewer` (independent static/pre-install gate)  
**Adapter:** `content/sdk-adapters/rdm-topology-poc`  
**Candidate:** declared `0.1.0`, build `1`; locally built dev PAK
`0.0.0.1`  
**Verdict:** **CHANGES REQUESTED — 2 BLOCKING findings**

The Java mechanics compile and the focused tests pass, but this candidate is
not ready to progress past the local review gate. Its shipped installation
guide contradicts the fixture-only/no-network implementation, and its README
gives a direct test command for a non-executable script. Neither finding
requires or authorizes a deployment.

## Independent validation

| Check | Independent result |
|---|---|
| SDK artifact | Used the supplied local `vrops-adapters-sdk-2.2.jar`; no download, network access, or redistribution occurred. |
| `validate-sdk` | **PASS.** Compiled five Java sources. The sole `javac` warning is the known JDK 25 `-source/-target 11` module-location warning. |
| Focused tests | **PASS:** `bash scripts/run-tests.sh` reports `RdmTopologyPocTest: PASS (6 tests)`. It covers identifier flags, same-MOID/two-vCenter separation, payload repeatability, unresolved identity rejection, local key construction, and additive foreign-parent output. |
| `build-sdk` | **PASS.** Independently built `/tmp/rdm-topology-review-build.t5SWWO/vcfcf_sdk_rdm_topology_poc.0.0.0.1.pak` (78,306 bytes). The dev build did not bundle the Broadcom SDK JAR; it bundled the factory base JAR as intended. |
| `pak-compare` | **BLOCKED by missing reference PAK.** `tmp/reference_paks` does not exist, and an explicitly created empty reference directory produced `No .pak files found ...` with exit 1. The build itself correctly reported its dev-mode comparison skip. This is a validation-stage blocker, not a claim of a clean comparison. |
| PAK inspection | **PASS for static hygiene.** The built PAK contains one adapter JAR, `describe.xml`, resources, icons, and `vcfcf-adapter-base.jar`; it contains no `vrops-adapters-sdk` JAR, credentials, tokens, lab reports, or raw inventory. Bytecode for `RdmTopologyRelationships` calls only `RelationshipBuilder.parentForeign(...).build()`. |
| Live activity | **None.** No install, adapter-instance creation, Suite API/vCenter request, or topology write occurred. |

## Verified implementation properties

- `ForeignVmIdentity` reconstructs a `VMWARE` / `VirtualMachine`
  `ResourceKey` by copying every supplied identifier name, value, and actual
  `isPartOfUniqueness` flag; it rejects an input missing a uniqueness-bearing
  `VMEntityObjectID` or `VMEntityVCID`
  ([ForeignVmIdentity.java](../../../content/sdk-adapters/rdm-topology-poc/src/com/vcfcf/adapters/rdmtopologypoc/ForeignVmIdentity.java)
  lines 18–58, 65–74). This is the required vCenter-scoped identity and does
  not fall back to name or bare MOID.
- The focused test proves equal MOIDs from two distinct vCenter identifiers
  create unequal keys ([RdmTopologyPocTest.java](../../../content/sdk-adapters/rdm-topology-poc/tests/com/vcfcf/adapters/rdmtopologypoc/RdmTopologyPocTest.java)
  lines 37–45). It also proves the exact observed uniqueness flags are kept
  (lines 24–35).
- The local `RdmMapping` key contains precisely
  `vcenter_instance_uuid`, `vm_instance_uuid`, and `virtual_disk_key`, all
  uniqueness-bearing in the emitted `ResourceKey` (RdmMappingIdentity.java
  lines 9–34; test lines 73–84). Its `describe.xml` declares the same stable
  tuple (lines 13–21).
- The only emitted edge is `parentForeign(foreignVm, localMapping)`
  (RdmTopologyRelationships.java lines 12–22). Local framework source routes
  `parentForeign` through additive `Relationships.addRelationships`, never
  `setRelationships` against the VMWARE parent
  ([RelationshipBuilder.java](../../../src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/stitch/RelationshipBuilder.java)
  lines 178–198 and 318–354). The POC test also asserts `isAdd()` and
  `!isClearFirst()` (test lines 86–98).
- Repeated fixture collection produces equal parent/child relationship
  payloads and additive items (test lines 47–61). This proves deterministic
  *emission*, not platform-side duplicate-edge idempotence or persistence;
  those remain deployment-proof questions as the design correctly states.
- No POC method creates an HTTP client, vCenter client, Suite API client, or
  metric/property payload. `RdmTopologyPocAdapter` has no endpoint
  configuration and calls no network operation (lines 17–80).

These checks satisfy the central requirements of the `vcfops-sdk-adapter`
skill and the reviewer’s **stitching identity** dimension, especially
`knowledge/lessons/stitch-moid-not-unique-across-vcenters.md` and
`knowledge/lessons/cross-mp-foreign-key-uniqueness-flags.md`. They do not
prove VCF Operations will resolve or retain this foreign key/edge after a
deployment.

## Findings

### B1 — shipped installation guide contradicts the fixture-only, no-network POC

**Severity:** BLOCKING  
**Authority:** `.claude/agents/sdk-adapter-reviewer.md`, review dimension 11
“Docs parity”; `vcfops-sdk-adapter` (“Gaps — name them, never hide them”);
RULE-005 [`knowledge/rules/validate-before-install.md`](../../rules/validate-before-install.md).

The POC states it has no endpoint, credentials, or network collection in
`adapter.yaml` lines 6–10 and `RdmTopologyPocAdapter.java` lines 17–37.
However, the shipped `docs/installing.md` says that outbound HTTPS/443 to a
target endpoint is required, tells an operator to add an account and fill in
configuration fields, and instructs them to validate a connection (lines
15–35). There are no configuration fields in `describe.xml` and
`getTester()` returns `null`.

**Required correction:** replace the scaffold with POC-accurate instructions:
no endpoint, no credential, no outbound network requirement, no connection
validation, and no install/deployment unless separately authorized. State
that installation is intentionally outside this increment and that any later
foreign-edge persistence test needs a fresh approval.

**If shipped as-is:** an operator can attempt a nonexistent endpoint/account
configuration path and infer a failed connection workflow rather than the
actual fixture-only scope.

### B2 — documented focused-test command fails because its script is not executable

**Severity:** BLOCKING  
**Authority:** `.claude/agents/sdk-adapter-reviewer.md`, review dimensions 9
and 11; RULE-005
[`knowledge/rules/validate-before-install.md`](../../rules/validate-before-install.md).

The landing README directs the operator to execute
`content/sdk-adapters/rdm-topology-poc/scripts/run-tests.sh` directly (lines
18–25), but the tracked file mode is non-executable (`100644`). Independent
execution produced `permission denied`; only an explicit `bash
scripts/run-tests.sh` invocation passed.

**Required correction:** either set the tracked executable bit or change the
README command to `bash content/sdk-adapters/rdm-topology-poc/scripts/run-tests.sh`.
Prefer exercising the documented command in the POC’s validation path.

**If shipped as-is:** a reviewer/operator following the documented test
command cannot run the required focused test suite.

## Registry check

`knowledge/context/defects.md` was read for this review. No open defect lists
`rdm-topology-poc`, `rdm`, or this adapter kind in `Affects:`. No closure is
proposed and no registry file was modified. B1 and B2 must be rechecked in a
subsequent build; if either survives accepted remediation, it is a candidate
for registry graduation under RULE-012
[`knowledge/rules/release-gate-defects.md`](../../rules/release-gate-defects.md).

## Deployment prerequisites still owed

After B1/B2 are resolved and a fresh reviewer pass has zero BLOCKING
findings:

1. Obtain a suitable reference PAK and rerun `pak-compare` with zero
   BLOCKING findings.
2. Obtain explicit authorization for a deployment experiment.
3. Capture a pre-install VMWARE topology baseline, install only the approved
   candidate, collect the fixture, and verify that the target VM retains its
   existing children while gaining exactly one pack-owned `RdmMapping` child.
4. Verify repeated collections do not create duplicate edges; test missing,
   ambiguous, and wrong-vCenter identity cases; then remove the POC only with
   a separately approved cleanup plan.

