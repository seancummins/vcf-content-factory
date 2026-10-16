# E4.9.2 — Collector constructor security review

## Scope and independent evidence

Review follows `.claude/agents/sdk-adapter-reviewer.md`, the shared reviewer
doctrine, the Tier 2 SDK playbook, RULE-005/007/008/012/014/015 and the
bare-controller instantiation lesson. Source is read-only to this reviewer;
only this report is written. No live connections, fixture reads, credentials,
installation, dependency downloads, PAK builds or Git mutations were used.

The collector failure supplied by the operator is an exact Java reflection
ABI failure. Independent SDK `AdapterBase` bytecode inspection confirms that
its public `(String, Integer)` constructor carries those arguments into its
logging/interface/cache initialization. The original adapter already forwards
both arguments to the keyed factory framework constructor. Java constructors
are not inherited by the direct-interface dispatcher.

Independently reran the frozen implementation with the genuine Broadcom SDK,
factory framework and eight explicitly selected external platform libraries:

- Dispatcher **348 assertions PASS**, including actual public
  `getConstructor(String.class, Integer.class)` and reflective construction,
  constructor-bound instance rejection, disabled diagnostic behavior, unchanged
  default fixture selection, invalid configuration, mode isolation, lifecycle
  races and actual SDK empty-payload checks.
- Full fixture lifecycle **948 assertions PASS**, four synthetic scenarios and
  four routes: legacy/v2 fixtures, absent/explicit fixture mode, original and
  dispatcher no-argument paths, and original and reflected collector paths.
  Actual SDK configuration, discovery, collection, repeat, refresh, stop and
  discard preserve exact scoped foreign keys, mapping/LUN keys, additive
  relationships and initial descriptive properties. Actual SDK logger carriers
  retain the exact supplied constructor String and instance ID. Repeat-property
  delta suppression remains governed by the existing SDK cache contract.
- Existing diagnostic suite **243 coordinator plus 22 SOAP assertions PASS**
  with network tests explicitly disabled. No local or VMware endpoint was
  contacted by these runs. The unchanged synthetic TLS suite is not rerun or
  newly qualified by this review.
- Actual combined descriptor loader **PASS**, three resource kinds and one
  credential kind, with no logging/platform shims. All eight external JARs
  match the supplied `SHA256SUMS` manifest. Appliance provenance is
  operator-attested, not independently re-acquired here.
- Generic constructor-contract regression suite **21 tests PASS**. The gate
  inspects `javap` metadata rather than loading or initializing adapter classes;
  it does not execute adapter constructors. This security-focused observation
  does not replace the required independent framework review.
- `validate-sdk` **PASS**, compiling all 22 production sources and verifying
  both constructor signatures. Existing source/target-11 module-path and
  deprecation warnings remain; they are not hidden.

The previously observed intermediate lifecycle harness assertion failure was
an incorrect test assumption about a global logging-properties path. Final
tests inspect the actual argument-bearing SDK logging carriers instead; the
production implementation was not changed to satisfy the mistaken assertion.

## Safety conclusions

The exact public collector constructor captures directory and boxed instance
ID in a lazy original-adapter factory. Neither public constructor instantiates
the publishing SDK base, opens a connection, decrypts credentials or starts a
worker. Valid fixture configuration alone constructs the original adapter with
the captured arguments. Collector-ID mismatch is rejected before selection or
delegate construction; configured identity/mode latching and stale-output
fences remain in place. Initialization/configuration failures do not select a
different mode or fall back to fixture publication.

The diagnostic route remains a direct-SDK empty-result path. Actual SDK
resource-collection maps, embedded discovery, explicit discovery and per-resource
status payloads are empty across success, failure, repeat, cancellation and
unconfigured tests. No resources, relationships, resource metrics, properties
or events are emitted; sanitized adapter-level status remains intentional.
No endpoint, credential, trust, ResourceKey or relationship code was changed
by this constructor repair. Strict TLS and explicit diagnostic opt-in remain
unchanged. The controller no-argument/describe path remains supported.

External SDK/platform dependencies are local-only, not reproducible from Git
or redistributed. Bytecode findings are summarized here in full. No open
defect-registry entry names this RDM adapter; no closure or waiver is proposed.

## Final artifact and verdict

**APPROVE — zero outstanding security findings (0 BLOCKING / 0 WARNING /
0 NIT).** This is offline implementation/package approval, not installation
or live diagnostic execution authorization.

Independently verified local development candidate
`vcfcf_sdk_rdm_topology_poc.0.0.0.11.pak`, SHA-256
`250d58894c624178863779f44d9fcea5a89c9f5e9774fa4b102251f0313392ce`.
Outer archive, inner archive and both embedded JAR integrity checks pass.
Registration retains the existing adapter kind and dispatcher entry class.
Only the entry JAR and factory framework JAR are present; no SDK, trustmanager,
Log4j/Commons or test classes are bundled. Against build 10, the descriptor and
framework JAR are byte-identical, and the dispatcher is the **only changed
existing class** in the adapter JAR. The reviewed dispatcher source SHA-256 is
`a19483fc49945d8564cbfa0bf728c02b7180af0e0ab3af0453581f3e07ef4389`.

Independent explicit structural comparison against the approved Synology
1.0.0.30 reference, pinned SHA-256
`beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`,
returns **0 BLOCKING, 4 WARNING, 21 INFO, exit 0**. All four comparison warnings
remain: D3 credential-field count 2/5, D8 instance-identifier count 12/3,
D23 traversal count 0/1 and D25 empty versus populated traversal kinds. The
21 INFO findings remain metadata/display/icon/JAR differences and data-kind
count 2/9. These are comparator findings, not suppressed or reclassified as
reviewer security findings.

Build-9 and build-10 PAK hashes remain respectively
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`
and `df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`.
Candidates and proprietary test dependencies are local-only artifacts, not
reproducible from factory Git; findings are summarized above without binary
redistribution.

**If shipped as-is:** the exact missing collector reflection constructor is
present, default fixture lifecycle preserves the tested keys/topology, and
diagnostic mode retains its zero-publication boundary. Real collector
re-instantiation and restoration of the existing installed account still
require the separately authorized controlled retry in the
[E4.9.2 record](../../designs/managementpacks/vsphere-rdm-topology-e492-collector-constructor.md).
Injected decryption/RBAC, managed trust delivery, routing, collector failover
and diagnostic live execution are not newly qualified by these offline tests.
