# E4.9.2 — Independent SDK constructor and lifecycle review

## Verdict

**APPROVE the offline correction and development candidate; zero outstanding
SDK review findings.** This is not installation approval or a claim that the
real collector has recovered. The operator-reported build-10 failure remains
the live baseline until a separately authorized upgrade verifies recovery.

If shipped as-is, build 11 exposes the exact constructor that the reported
collector reflection requires while retaining lazy, isolated execution routes.
Actual offline fixture discovery/collection and diagnostic zero-publication
regressions pass; real collector/UI/network behavior remains unqualified.

Authorities: `.claude/agents/sdk-adapter-reviewer.md`, the Tier 2 SDK playbook,
RULE-005/007/008/012/014/015, and the shared reviewer doctrine. I checked the
defect registry: no open `Affects:` entry targets this adapter. No closure,
waiver or comparator policy change is proposed. The generic factory validator
change belongs to the separate framework-reviewer gate, not this SDK verdict.

## Root cause and correction independently inspected

The operator supplied the real collector contract:
`getConstructor(String.class, Integer.class)`. A no-argument constructor does
not satisfy it, and `int` would not satisfy boxed `Integer` reflection either.
The original `RdmTopologyPocAdapter(String, Integer)` forwards to its existing
SDK/framework constructor. The dispatcher now declares exactly that public
signature and lazily forwards the original directory and instance-ID arguments
to that constructor when fixture configuration succeeds.

The dispatcher does not eagerly instantiate its fixture SDK base. It records
the collector instance ID for status/identity checks, rejects mismatched SDK
configuration and unsaved-test carriers before delegation, and retains the
existing mode/ID/UUID latch. Missing or invalid configuration fails closed;
constructor/delegate failures do not choose another execution mode. The no-arg
controller `describe()` route remains available. No endpoint, credential,
resource key, topology rule or adapter kind changed.

## Independently rerun evidence

All commands were offline. The supplied SDK and eight explicitly listed
external platform libraries were used; no wildcard classpath, substitutes or
logging/platform shims were used for the constructor, descriptor or complete
fixture lifecycle qualification. All eight local `SHA256SUMS` entries verify;
appliance provenance remains operator-attested, not independently reacquired.

| Check | Observed result |
|---|---|
| `run-dispatcher-tests.sh --fixture-lifecycle` | Exit 0; 348 dispatcher assertions and 948 actual fixture lifecycle assertions |
| Reflection constructor regression | Exact public boxed signature lookup and instantiation pass; fixture delegate initially absent |
| Actual SDK initialization | Collector arguments preserved in SDK logger context and instance identity |
| Fixture matrix | Legacy mapping-only and v2 LUN fixtures, each default/explicit fixture selection, four routes: original/dispatcher × no-arg/collector constructor |
| Lifecycle coverage | Configure, discover, collect, repeat, reconfigure, collect, stop/discard; baseline/dispatcher keys and additive edges agree |
| Diagnostic isolation | Empty SDK resource map, no embedded discovery/relationship payload, no resource status/data payload; repeat/failure/cancellation/owner guards pass |
| Actual combined descriptor loader | Exit 0; 3 resource kinds, 1 credential kind |
| `validate-sdk` | Exit 0; 22 sources compile and reusable entry-constructor ABI check passes |
| Existing fixture tests | 8 topology/descriptor tests, 42 invalid runtime cases and 34 invalid LUN cases plus positive matrices pass |

The old standalone fixture runner explicitly uses test-only logging linkage and
constructor-bypass coverage; it is supplementary, not the shim-free lifecycle
proof above. Compiler warnings remain source/target-11 system-module and
deprecated-API notices. No additional missing class occurred on tested paths;
encrypted platform configuration and unexercised certificate branches are not
claimed qualified.

## Frozen artifact review

Development artifact: `vcfcf_sdk_rdm_topology_poc.0.0.0.11.pak`.

SHA-256:
`250d58894c624178863779f44d9fcea5a89c9f5e9774fa4b102251f0313392ce`.

This is an external local-only development artifact, not a published release
or reproducible binary citation. Its inspected properties are summarized here:

- Outer, inner and both JAR CRC checks pass. Registration remains
  `ENTRYCLASS=com.vcfcf.adapters.rdmtopologypoc.RdmTopologyDispatcher`,
  `KINDKEY=vcfcf_rdm_topology_poc`.
- Independent `javap -public` against the **packaged** entry JAR confirms both
  public `()` and `(java.lang.String, java.lang.Integer)` constructors.
- The descriptor is byte-identical to build 10. Comparing existing entry-JAR
  classfiles, only `RdmTopologyDispatcher.class` changed. Original fixture,
  identity, graph and relationship implementation bytecode remains identical.
- Exactly two JARs ship: adapter entry JAR and factory adapter-base JAR.
  Neither contains proprietary SDK/platform, `com.vmware`, Apache dependency,
  lifecycle-probe or test classes. External platform dependencies remain outside
  the PAK.
- Preserved build-9 SHA-256:
  `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`;
  build-10 SHA-256:
  `df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`.

Independent explicit structural comparison against approved Synology 1.0.0.30
(SHA-256 `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`)
returns **0 BLOCKING, 4 WARNING, 21 INFO; exit 0**. All findings are retained:
W1 credential-field count 2 vs 5; W2 instance-identifier count 12 vs 3;
W3 traversal-kind count 0 vs 1; W4 empty traversal container vs populated.
I1–I3 are description/display-name/name differences, I4–I8 adapter-specific
RDM icons/JAR additions, I9–I20 reference-specific Synology icons/JAR absence,
I21 data-kind count 2 vs 9. No suppression or reclassification was used.

## Remaining controlled qualification

The live collector must still instantiate build 11, retain the existing account
and exact configuration, resume default fixture collection and preserve keys,
counts and additive VMware topology. Diagnostic configuration/runtime, SDK
credential injection, enterprise trust delivery and collector routing remain
separate controlled evidence. No live API call, installation, account/resource
change, artifact regeneration, commit or publication occurred in this review.
