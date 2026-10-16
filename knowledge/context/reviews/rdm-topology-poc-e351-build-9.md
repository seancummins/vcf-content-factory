# E3.5.1 — independent SDK review, build 9

**Verdict: APPROVE — zero BLOCKING, WARNING or NIT implementation findings.**
Offline descriptor correction only; not installation approval or live acceptance.

## Scope and root cause

Independent `sdk-adapter-reviewer` context, read-only adapter inspection against
the SDK skill, reviewer doctrine, RULE-005/008/012/014 and the
[E3.5.1 correction record](../../designs/managementpacks/vsphere-rdm-topology-e351-descriptor-compatibility.md).
Factory Python validation changes receive a separate framework review. The
previous build-8 review's loader skip was a real coverage gap: DOM parsing,
compilation and structural comparison did not establish descriptor acceptance.

The locally authorized SDK's actual private
`ResourceAttributeDescribe.isValidAttributeKey(String)` and
`ResourceGroupDescribe.isValidGroupKey(String)` reject either `|` or `:` in
individual descriptor segments. Independent `javap -c -p` confirms that bounded
rule; it is not an alphanumeric-only whitelist or full installation validator.
Working Synology descriptors and the factory DescribeBuilder use group/leaf XML.
All eleven build-8 flat CanonicalLun attributes violated this segment contract.
Composite runtime MetricKey paths are a different contract and remain legal.

Build 9 represents these properties as noninstanced `identity` and `storage`
ResourceGroups containing unqualified leaf keys. All eleven reconstructed full
paths equal the original Java property emission paths. Production Java classes
are **byte-identical** to build 8, including ResourceKey identity, qualification,
build-6 fixture parsing and both additive relationship implementations. No Java
property rename, credential metadata, endpoint or topology-policy change occurs.
Two localized group labels, version/build metadata and corresponding generated
documentation are the remaining package delta.

## Independently verified artifacts and checks

Local development candidate: `vcfcf_sdk_rdm_topology_poc.0.0.0.9.pak`.

SHA-256: `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.

Approved reference: Synology `v1.0.0.30`, SHA-256
`beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.
Supplied proprietary SDK SHA-256:
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
These hashes were independently computed before comparison. SDK and development
PAKs are local-only, not redistributable/repository-reproducible citations;
relevant findings are fully summarized here.

| Independent check | Actual outcome |
|---|---|
| Focused Java script | PASS: 8 topology/descriptor tests; 42 invalid runtime cases; 34 invalid-LUN cases and positive/convergence/idempotence matrices |
| Actual SDK loaders | PASS, no skipped loader checks: persisted fixture setting; both corrected groups/all eleven leaves; negative original pipe paths and colon keys for attributes/groups |
| Descriptor/emission parity | PASS: all eleven full paths equal Java emissions; no other illegal group/attribute segments |
| `validate-sdk` | PASS, six production Java sources compile |
| Independent scratch-copy `build-sdk` | PASS, explicit pinned structural automatic gate, exit 0 |
| Exact candidate structural comparison | **0 BLOCKING / 3 WARNING / 23 INFO**, exit 0 |
| Nested archive integrity | PASS, all 73 recursively expanded payload leaves match independent rebuild byte-for-byte |
| Build-8 to build-9 production class comparison | PASS, all 52 class leaves, including bundled framework classes, unchanged |
| Package safety | No SDK classes/JAR, logging shim, test classes, fixture JSON or environment files; adapter and framework JARs only |
| Embedded descriptor | Exactly source descriptor; legal group/leaf keys; credential-free instance unchanged; no credential declarations/references |
| Docs parity | Landing/inventory runtime supplements, overview and fixture contract describe both additive SDK paths and untested local-edge persistence |
| Adapter whitespace | `git diff --check` PASS |
| Registry | No local override; no open registry defects affect this adapter; `defect-gate --pak rdm-topology-poc` passes |

The actual SDK descriptor classes are not substituted. Two explicitly test-only
`org.apache.logging.log4j` linkage shims provide no-op logging methods because
the local log4j API is unavailable; validation remains SDK bytecode. The script
compiles those only from `tests/`, and archive inspection proves neither shim
is shipped. This exercises the relevant loader logic, not the real platform's
logging/classloader/controller environment. Java retains its existing
source/target-11 compiler warning; no JDK-11 runtime compatibility claim is added.

Independent rebuild SHA-256:
`2d82d658627db632c0bb1c60e5b40c52fa4b85ac9b7dbae812b513c7d44fea31`.
ZIP timestamp metadata differs; all expanded payload contents match. This is
payload reproducibility, not deterministic archive-byte proof. Scratch copying
avoided overwriting original build-8/build-9 artifacts or generated adapter docs.

## All structural findings retained

- WARNING W1/D8: adapter-instance identifier count 1 versus 3.
- WARNING W2/D23: TraversalSpecKind count 0 versus 1.
- WARNING W3/D25: empty candidate TraversalSpecKinds versus populated reference.
- INFO I1/D1 and I2/D6: independently valid optional credential-contract differences.
- INFO I3–I5/M7: description, display name and name differences.
- INFO I6–I10/A1: candidate adapter/data/instance icons and adapter JAR differences.
- INFO I11–I22/A2: reference adapter/data/instance icons and adapter JAR differences.
- INFO I23/D17: two candidate versus nine reference data kinds.

None is suppressed, waived or reclassified. Zero comparator blockers do not
replace descriptor-loader tests or prove runtime edge creation. No new surviving
review finding requires registry graduation; the reported build-8 defect has a
concrete offline correction, while controlled installation proof remains owed.

## Controlled retry and remaining limitations

The operator procedure appropriately requires separate authorization, a baseline
of the still-registered build-6 version/topology, checksum verification and a
management-pack update **without uninstalling build 6 or changing fixtures**.
It must confirm actual installed version and descriptor-load logs, and stop on
registration failure or unexpected topology changes. A qualified v2 fixture and
local LUN-edge experiment remain separately authorized work; no live requests,
configuration, cleanup, commits, pushes or publication occurred in this review.

The generated documentation still requires restoration of its explicit runtime
edge supplement after regeneration (standing E3.5 limitation, not changed here).
Cross-host/cross-vCenter/global deduplication, subsequent VMware-cycle persistence,
failover and cleanup remain unproven. The unrelated prior factory setup-test
failure and full factory checks are reported by the orchestration/framework gate,
not represented here as independently rerun by this SDK review.

**If shipped as-is:** the known illegal descriptor segments are corrected while
the existing VM-parent relationship and build-6 fixtures remain unchanged; a
controlled lab update must still demonstrate platform registration and later,
separately, qualified CanonicalLun topology acceptance/persistence.
