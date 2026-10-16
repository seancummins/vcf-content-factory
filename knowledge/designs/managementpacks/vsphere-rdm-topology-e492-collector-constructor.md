# E4.9.2 — Real collector constructor compatibility

## Operator evidence and root cause

The operator reports that development build 10 installed but the existing
fixture account then failed collection. The collector reported
`NoSuchMethodException: RdmTopologyDispatcher.<init>(String, Integer)` while
calling `adapterClass.getConstructor(String.class, Integer.class)`.
No live investigation or installation was performed in this increment.

The original working `RdmTopologyPocAdapter` declares both public no-argument
and `(String adapterDir, Integer adapterInstanceId)` constructors. The latter
passes both values to the keyed framework/SDK constructor. SDK initialization
uses them for instance-scoped logging/cache state. E4.9's direct-SDK facade
provided only the no-argument constructor, so actual collector construction
failed before mode selection or fixture collection. Java compilation, descriptor
loading and no-argument lifecycle tests do not prove this reflection ABI.

This is an entry-class construction defect, not a fixture identity, credential,
TLS, relationship or descriptor defect. The supplied SDK and platform libraries
are external local-only proprietary dependencies; bytecode/API findings are
summarized here, not redistributed. Authorities are the SDK author constructor
contract and the [bare-controller lesson](../../lessons/controller-describe-bare-instantiation.md).

## Correction and regression boundary

Retain the existing public no-argument controller path. Add the exact public
`RdmTopologyDispatcher(String, Integer)` collector constructor. Preserve the
directory and instance ID in a lazy fixture factory so the original adapter
receives the same arguments only when valid fixture mode is selected.
Diagnostic mode must never construct the publishing base class. Bind collector
identity before configuration and reject conflicting instance IDs without a
fallback or automatic mode switch. No second kind or alternate collector ABI.

Tests must call actual `Class.getConstructor(String.class, Integer.class)` and
`newInstance`, then exercise both actual collector and no-argument lifecycles.
Use genuine SDK carriers and the eight verified external libraries, without
logging shims or constructor bypass. Preserve the legacy/v2 fixture resource
keys, exact foreign VM identifiers/uniqueness flags and additive edges. Account
for the [qualified SDK property-delta behavior](vsphere-rdm-topology-e491-lifecycle-dependencies.md)
rather than interpreting unchanged-property suppression as topology loss.

The generic factory gate must inspect compiled entry-class metadata, not load
or initialize adapter classes. Require the supported controller and collector
constructor signatures without hardcoded adapter names or exceptions. SDK/JDK
unavailability must remain explicitly unverified, not an ABI pass.

## Controlled upgrade retry — only after separate authorization

1. Retain the currently installed build-10 account and all Operations inventory.
   Record its configuration, collector placement, resource counts and topology
   privately. Do not uninstall the shared kind, delete resources, recreate the
   account or edit fixture/configuration as a repair.
2. Verify the approved replacement PAK's exact checksum and separately authorize
   its development-lab upgrade. Install only through the supported update path;
   this document does not execute or authorize installation.
3. Confirm the intended new version is installed and the collector instantiates
   the existing account without the missing-constructor error. Require actual
   collection/data evidence and the unchanged resource identities/additive
   topology, not merely Validate Connection or a successful PAK upload.
4. Observe repeated collections for duplicate resources or unintended topology
   changes. Stop on constructor/configuration/identity errors or unexpected
   publication. Do not switch modes, relax TLS or inject dummy credentials.
5. Stop the affected instance within the authorized recovery scope if unexpected
   inventory changes occur. Do not uninstall the shared pack or assume a
   downgrade is safe. Any rollback/roll-forward requires its own verified
   recovery procedure and authorization.

Diagnostic execution remains separately opt-in and separately authorized; this
repair is not permission to run it or to alter the working lab topology.

## Final offline evidence

The production correction is confined to `RdmTopologyDispatcher.java`: the
public collector constructor lazily forwards both original initialization
arguments, and a constructor-bound instance-ID guard rejects mismatched
configuration/test input. The controller constructor remains available. Tests
add actual reflection construction, SDK logger-context verification, wrong-ID
rejection, default fixture and diagnostic isolation checks. The fixture
lifecycle probe now compares original/dispatcher implementations through both
controller and collector construction. `adapter.yaml` advances to development
build 11 with matching changelog/documentation; the combined descriptor and
resource kinds/keys/relationship logic do not change.

The factory adds `_validate_entry_constructor_contract` to
`src/vcfcf_managementpacks/sdk_builder.py`. Both validation and build/buildkit
paths inspect the compiled configured entry class with `javap -public -s`
before packaging. No adapter code is loaded or initialized. The check requires
a public concrete class and exact declared public `()` and `(String, Integer)`
JVM constructors. Generic constructors with the correct erased ABI are accepted;
private, inherited-only, primitive-int, Object and varargs alternatives are
rejected. Inspection errors/missing tools fail closed. When compilation is
unavailable, structural validation explicitly reports constructor qualification
as unverified, retaining the established no-SDK/no-JDK behavior.

New regression module:
`tests/managementpacks/test_sdk_entry_constructor_contract.py`. Two synthetic
Java fixtures in `test_buildkit_isolated_build.py` and
`test_buildkit_release_flag.py` gain the real required constructors; existing
assertions and release controls remain unchanged. Prior descriptor-key
validation and unrelated dirty changes are preserved.

| Offline check | Actual result |
|---|---|
| Reflection/dispatcher and diagnostic isolation | PASS, 348 assertions |
| Actual shim-free SDK fixture lifecycle | PASS, 948 assertions, 4 fixture scenarios across 4 construction/routes |
| Actual combined SDK descriptor loader | PASS, 3 resource kinds / 1 credential kind; genuine eight-library classpath |
| SDK validation / compilation | PASS, 22 production sources plus compiled entry ABI verification; existing Java warnings |
| Runtime binding / Operations provider / discovery regressions | PASS, 62 / 281 / 54 deterministic cases |
| Generic constructor-contract tests | PASS, 21 tests; includes class-initialization/constructor execution traps |
| Management-pack test directory | PASS, 339 passed / 8 skipped |
| Complete factory suite, independent framework rerun | 2521 passed / 15 skipped / 131 deselected / 293 warnings; one unchanged failure below |
| Full content validation, skill parity, path audit, whitespace | PASS; existing standing-exception path warnings only |

The existing full-suite failure remains
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`.
It expects a not-a-repository setup message rather than the implementation's
conservative unknown-Gitignore diagnosis. It was not modified or suppressed;
the factory suite is not represented as entirely green.

The [independent framework review](../../context/reviews/framework/sdk-entry-constructor-e492.md)
is **APPROVE, zero outstanding findings**. No commit, push, tag, release or live
modification is permitted in this increment.

## Development candidate and unchanged package boundary

Local development artifact (not an approved release):
`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.11.pak`.

SHA-256: `250d58894c624178863779f44d9fcea5a89c9f5e9774fa4b102251f0313392ce`.

The candidate is local-only and not reproducible from factory Git alone; the
adapter is an independent repository with uncommitted changes and proprietary
external build dependencies. No platform/SDK JAR is redistributed in the PAK.
Both ZIP layers and both embedded JARs pass integrity checks. Registration keeps
the existing adapter kind and dispatcher entry class. The packaged dispatcher
declares the exact public `(String, Integer)` constructor. The descriptor,
factory-base JAR and all 59 other existing entry-JAR classes are byte-identical
to build 10. Only the dispatcher class changes among those compiled classes.

The original build-9 and build-10 PAKs remain unchanged, respectively:

- `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`
- `df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`

Explicit structural comparison against approved Synology `v1.0.0.30`, reference
SHA-256 `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`,
returns **0 BLOCKING / 4 WARNING / 21 INFO, exit 0**. No comparator change,
suppression or manual reclassification was made. Findings remain:

| Findings | Actual differences |
|---|---|
| W1 / D3 | CredentialField count 2 versus 5 |
| W2 / D8 | Adapter-instance identifier count 12 versus 3 |
| W3 / D23 | TraversalSpecKind count 0 versus 1 |
| W4 / D25 | Empty versus populated TraversalSpecKinds |
| I1–I3 / M7 | Description, display name and name |
| I4–I20 / A1–A2 | Adapter-specific icon/JAR presence differences |
| I21 / D17 | Data-resource-kind count 2 versus 9 |

Older fixture unit matrices also pass (8 topology/descriptor checks, 42 invalid
runtime and 34 invalid-LUN cases). Their historical logging-linkage or
constructor-bypass limitations are not substituted for the separately executed
348/948 assertion shim-free lifecycle evidence above. This increment does not
claim every historical test is a full platform lifecycle test or that static
comparison proves deployed collector success.

## Independent disposition and remaining live qualification

- [SDK implementation review](../../context/reviews/rdm-topology-e492-sdk-review.md):
  **APPROVE**, zero outstanding findings; independently reproduced the real SDK
  suites, inspected the packaged constructor ABI and compared the actual PAK.
- [Security review](../../context/reviews/rdm-topology-e492-security-review.md):
  **APPROVE**, zero outstanding findings; independently verified startup
  isolation, identity guards, no-publication diagnostics and package exclusion.
- [Framework review](../../context/reviews/framework/sdk-entry-constructor-e492.md):
  **APPROVE**, zero outstanding findings; generic gate and complete factory
  validation independently rerun, including disclosure of the unrelated failure.

**Offline correction/candidate approved; controlled upgrade retry requires
separate operator authorization.** Actual recovery of the installed build-10
account, real collector classloading, credential/trust delivery, routing and
deployed repeated collection remain unverified. Tests do not establish live
recovery or re-authorize diagnostic execution. Existing accounts, installed
PAK, VMware-owned resources and topology have not been contacted or changed.
