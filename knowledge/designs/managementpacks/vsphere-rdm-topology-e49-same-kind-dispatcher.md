# E4.9 — Same-kind read-only diagnostic dispatcher

## Scope and compatibility contract

Implements the preferred [E4.7 design](vsphere-rdm-topology-e47-diagnostic-packaging.md)
after [E4.8 actual-loader qualification](vsphere-rdm-topology-e48-supplied-platform-libraries.md#seven-library-offline-qualification).
The independent adapter repository remains
`content/sdk-adapters/rdm-topology-poc`; no second adapter kind is registered.

`RdmTopologyDispatcher` directly implements the actual SDK `AdapterInterface3`.
Missing `execution_mode` selects the unchanged fixture implementation;
explicit `fixture` also selects it. Only explicit `read_only_diagnostic` selects
the reused bounded native diagnostic engine. An empty/unknown/duplicate mode,
mixed nonempty configuration or failed validation cannot select another path.
There is no error fallback between modes.

The fixture adapter class and parsers retain the original resource-key
contracts, complete foreign VM identifiers/flags and additive VM-parent and
mapping-to-LUN semantics. Diagnostic lifecycle dispatch bypasses their resource
enumeration and SDK base-class collection. It returns empty SDK publication
payloads plus sanitized status/counts; source API inventory reads are not SDK
resource publication. No diagnostic mapping, LUN, metric, property, event or
relationship may be emitted.

The direct facade is required because final SDK base lifecycle methods add
properties/metrics outside `onCollect()`. A flag inside that callback would not
satisfy the boundary. Route latching, invalid-configuration retirement,
serialized fixture lifecycle and diagnostic generation/cancellation fences are
part of the implementation review, not inferred from an empty callback.

Valid legacy fixtures retain their collection path. The facade strengthens
unsaved fixture validation: the former no-tester callback returned true even
for an invalid fixture; the facade rejects malformed input before selection.
This is not a claim of bit-identical behavior for invalid-input callbacks.
Fixture callbacks are serialized, so a stop request can wait for a finite
fixture callback to return; it is not preemptive cancellation of that code.

## Combined descriptor and configuration

One adapter kind/instance kind: `vcfcf_rdm_topology_poc`. Existing `RdmMapping`
and `CanonicalLun` kinds and identifying fields remain unchanged.
`fixture_json` becomes optional **in descriptor metadata only** so a diagnostic
instance can be saved without it. The fixture runtime still requires exactly
one complete valid fixture; existing accounts do not need a new mode field or
credential. All newly introduced settings are nonunique ordinary instance
configuration, never foreign resource identities or secret fields.

| Setting | Fixture path | Diagnostic path |
|---|---|---|
| `execution_mode` | Absent or exact `fixture` | Exact `read_only_diagnostic` |
| `fixture_json` | Required and parsed as before | No populated fixture |
| vCenter endpoint/trust, Operations endpoint/trust | No populated diagnostic settings | Required; strict HTTPS and approved trust contract |
| `discovery_scope` | No populated diagnostic setting | Exact `single_vm_current_host` |
| Target vCenter UUID, VM MOID, disk key | Derived from fixture as before | Exact scoped target configuration |
| `diagnostic_enabled`, `authorize_once` | Not diagnostic opt-in | Both explicit booleans; initially false |
| Associated vCenter credential | No credential required | Actual SDK-managed `rdm_vcenter_readonly` association required |
| Operations identity | No remote collection | Only distinct SDK-injected per-instance credential carrier |

The combined descriptor retains `isCredentialRequired="false"`; mode-specific
requirements are enforced in code. No dummy credential, credential-valued
identifier, other integration's credential, node-local file or authentication
fallback is introduced. Ordinary optional blank settings must not activate a
route; duplicate/unique-marked or unknown settings fail closed. UI serialization
and optional credential selection remain collector/UI qualification items even
if the actual SDK model loader accepts the descriptor.

Strict CA/JVM trust and hostname checks remain those reviewed in E4.6.
Supported SDK-managed CA PEM material is not an operator-complete CA delivery
guarantee; opaque IDs/leaf-only trust/disable flags remain rejected. If neither
approved existing JVM roots nor supported instance-managed CA delivery is
available on the intended collector, stop. Do not synchronize local trust files
or disable TLS verification. Actual injected secret decryption/RBAC and Cloud
Proxy routing remain unproven for this diagnostic instance.
Both bindings read the same SDK instance certificate collection. If CA material
is supplied, both must select `enterprise_ca` and the administrator must approve
that bundle for both endpoints; `jvm` rejects additional material. Separate
contexts do not imply separate persisted certificate slots.

## Upgrade and operator boundary

Changing the entrypoint/descriptor under the same kind updates shared code for
**all instances**, even when the diagnostic will use a new account. Offline
tests cannot prove a nondisruptive installed upgrade. Preserve the working
build-9 artifact and instance configuration. Do not modify the installed instance
or uninstall the shared pack as preparation or diagnostic cleanup.

Conditional operator sequence, **not authorized for execution by E4.9**:

1. Obtain separate authorization for a controlled same-kind development upgrade
   and one read-only attempt. Verify the exact candidate hash and acceptance
   records. Record the current solution version, fixture account, collector
   placement, counts, topology and recovery baseline privately.
2. Stop existing fixture collection only within the approved maintenance scope;
   upgrade through the supported UI without uninstalling first. Verify the
   actual installed version/kind/descriptor and that the original fixture
   account resumes unchanged with its existing resources and relationships.
3. Create a **new same-kind instance**, with a distinct name and independently
   verified new instance UUID, in diagnostic mode; do not switch or reuse the
   fixture instance. Enter exact target settings privately and
   associate only its dedicated read-only vCenter credential. Keep execution
   flags false. Establish strict trust/routing and injected identity access;
   configuration-only validation is not connectivity or discovery evidence.
4. On the separately authorized attempt, set both flags true and permit one
   collection. Expected evidence is sanitized `PASS / GRAPH /
   READ_ONLY_GRAPH_QUALIFIED`, counts **1/1/1**, not merely Collecting or Data
   Receiving. Confirm no diagnostic SDK inventory/metric/property/relationship
   publication and that existing fixture/VMware topology is unchanged.
5. Immediately stop/disarm the diagnostic and reset both flags false. One-shot
   authorization is object-local, not durable across restart/failover. Stop on
   placement changes, ambiguity, partial discovery, auth/RBAC/TLS failures,
   timeout, unexpected publication or fixture regression; do not relax guards.

Rollback first stops/disarms only the diagnostic. Do not delete VMware or POC
topology or kind-wide credentials. Shared-kind uninstall can remove the working
POC and cascade credentials. Any downgrade/roll-forward or exact-instance cleanup
needs separately authorized recovery steps and post-reconciliation verification;
possessing the old PAK does not prove downgrade safety.

## Offline evidence and final disposition

The seven E4.8 libraries suffice for actual descriptor loading, not every SDK
lifecycle operation. A direct probe of the **unchanged** fixture constructor
encounters missing platform class
`com.vmware.vrops.secure.connection.ConnectionCategory` in SDK trust-manager
initialization. No fake class or runtime-library bundle is introduced to hide
that gap. Existing fixture source/core tests and exact carrier-forwarding
tests provide compatibility evidence; complete fixture construction/configure/
collection through the facade remains unqualified offline with this classpath.
The live build-9 evidence is retained, not presented as a live dispatcher test.

### Implementation and validation record

The independent adapter repository adds `RdmTopologyDispatcher.java`,
`DispatcherTest.java`, `FixtureLifecycleProbe.java`,
`diagnostic/DispatcherDiagnosticFixture.java`, `scripts/run-dispatcher-tests.sh`
and `docs/same-kind-diagnostic.md`. Existing `DiagnosticRuntime.java` and
`RuntimeDiscoveryBinding.java` gain explicit same-kind bindings; `describe.xml`,
`resources/resources.properties`, `adapter.yaml` and the descriptor regression
test change together. Manual/generated documentation reflects build 10 and the
unchanged fixture topology. The original fixture adapter, fixture parser,
CanonicalLun identity implementation and relationship emission are unchanged
relative to the start of E4.9. Earlier uncommitted increments remain separate
from this change; the factory does not absorb the adapter's Git history.

| Offline check | Result |
|---|---|
| Shim-free dispatcher, real SDK carriers/payloads and combined descriptor | PASS, 317 assertions; 3 resource kinds and 1 optional credential kind |
| Actual bare dispatcher `describe()` | PASS without constructing the fixture publishing base |
| SDK validation | PASS, 22 production sources; existing Java source/target and deprecation warnings |
| Existing topology/fixture regressions | PASS, 8 topology/descriptor tests, 42 invalid-runtime cases, 34 invalid-LUN cases and positive matrices |
| Diagnostic composition / isolated SOAP wire | PASS, 243 / 22 assertions |
| Runtime binding / Operations provider / discovery | PASS, 62 / 281 / 54 deterministic cases |
| External descriptor dependency tests | PASS, 15 tests; seven source-manifest checksums verified |
| Synthetic localhost transport TLS/security suite | PASS, 19 assertions, independently rerun by security reviewer; no VMware access |
| Full unchanged fixture SDK lifecycle | BLOCKED, exit 2: missing `ConnectionCategory` as described above |
| Complete factory pytest run | 2500 passed, 15 skipped, 131 deselected, 293 warnings; one existing failure described below |
| Changed-content and complete content validation | PASS |
| Codex skill parity | PASS, 5 paired and 7 Codex-only |
| Path-reference audit | PASS; existing RULE-015 standing-exception warnings only |

The unrelated factory failure remains
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
the assertion expects a not-a-repository message while the implementation emits
the conservative unknown-Gitignore diagnosis. No unrelated implementation or
test was changed to conceal it. These checks do not prove live SDK credential
decryption, UI serialization, routing or upgrade compatibility.

### Development artifact and comparison

Local-only candidate:
`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.10.pak`

SHA-256: `df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`.

Both package layers and both JARs pass integrity inspection. The package contains
only the adapter and factory-base JARs, not proprietary SDK/platform dependencies,
test classes or live fixture payloads. Registration uses the original kind and
new dispatcher entry point. All nine original RDM class files from build 9 and
the two data-resource-kind descriptor subtrees are byte-identical in build 10.
The original build-9 artifact remains unchanged, SHA-256
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.

Explicit structural comparison against approved Synology `v1.0.0.30`, reference
SHA-256 `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`,
returns **0 BLOCKING, 4 WARNING, 21 INFO; exit 0**. Nothing was suppressed or
reclassified, and comparator policy was not changed.

| Finding | Actual difference |
|---|---|
| W1 / D3 | CredentialField count: 2 versus 5 |
| W2 / D8 | Adapter-instance identifier count: 12 versus 3 |
| W3 / D23 | TraversalSpecKind count: 0 versus 1 |
| W4 / D25 | Empty versus populated TraversalSpecKinds |
| I1–I3 / M7 | Adapter description, display name and name differ |
| I4–I20 / A1–A2 | Adapter-specific icon and JAR additions/missing files |
| I21 / D17 | Data-resource-kind count: 2 versus 9 |

### Independent disposition

[SDK review](../../context/reviews/rdm-topology-e49-sdk-review.md): **APPROVE**,
zero outstanding findings. [Security review](../../context/reviews/rdm-topology-e49-security-review.md):
**APPROVE**, zero blocking/warning/note findings. Both independently exercised
the final 317-assertion suite and assessed the candidate package. Review
requests for strict same-kind binding validation and stale-output suppression
were corrected and retested before approval.

**Offline implementation/development candidate approved; CONDITIONAL GO for a
separately authorized controlled read-only lab qualification**, subject to the
runtime, trust, UI and shared-kind upgrade prerequisites above. This is neither
unconditional installation readiness nor live diagnostic success. No live
access, installation, adapter-instance change, commit, push or release occurred.
No automatic topology-publication approval is implied.
