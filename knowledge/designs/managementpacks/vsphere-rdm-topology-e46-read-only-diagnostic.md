# E4.6 — Read-only automatic-discovery diagnostic candidate

## Scope and safety boundary

Composes the [E4.2 discovery engine](vsphere-rdm-topology-e42-discovery-foundation.md),
[E4.3 SDK binding](vsphere-rdm-topology-e43-runtime-bridge.md) and
[E4.5 Operations provider](vsphere-rdm-topology-e45-operations-provider.md)
under [E4.1](vsphere-rdm-topology-e41-automatic-discovery.md).
The implementation remains in the independent adapter repository at
`content/sdk-adapters/rdm-topology-poc`.

The new, **unregistered** `ReadOnlyDiagnosticAdapter` implements the actual SDK
`AdapterInterface3` directly. This is necessary because bytecode inspection
showed `AdapterBase.collectBase()` adds system properties, adapter metrics and
other results after `onCollect`; an empty callback would not establish a
no-publication boundary. The diagnostic does not extend that base or the factory
adapter class. Its `collect()` returns an empty SDK `CollectResult`, with only
sanitized adapter-status text; `discover()` returns empty inventory. No resource,
relationship, metric, property or event is emitted. The in-memory graph is never
converted into a platform publication payload.

The separate candidate kind is `vcfcf_rdm_discovery_diagnostic`. The registered
POC entrypoint, active descriptor, build version, fixture mode and PAK remain
unchanged. No candidate is built or installed by E4.6. Direct-interface collector
acceptance is not inferred from successful compilation.

## Composition and target scope

`DiagnosticRuntime` validates the real SDK configuration and binds the associated
vCenter credential separately from the injected per-instance Operations identity.
No credential fields are relabeled, copied into identifiers or borrowed from an
existing VMware integration. Explicit diagnostic-only binding overloads accept
only the exact diagnostic owner kind; the original POC entry points retain their
previous owner and configuration contracts.

The pipeline is:

1. Capture the exact Operations key for configured vCenter UUID plus VM MOID,
   using the native public Suite API provider, including fresh detail confirmation.
2. Use that immutable scoped resolver in the actual vCenter SOAP discovery engine.
3. Verify the returned vCenter UUID, retrieve only the specified VM via explicit
   PropertyCollector object sets, retrieve only its current host's SCSI inventory,
   and fence the same VM configuration/host. No recursive VM container view is
   used in this scoped overload. Original unscoped behavior remains available
   unchanged through the original constructor.
4. Require a complete graph with exactly one RDM attachment, the expected disk
   key and exactly one intrinsically qualified LU-associated NAA logical unit.
   Preserve all existing RDM and CanonicalLun identity rules and exact VM keys.

Operations listing still enumerates bounded caller-visible VM-kind pages; the
public GET has no documented identifier filter. It is not described as a
target-only server query or evidence of exhaustive RBAC coverage. The source SOAP
read is narrowly targeted. Other RDM attachments on the target VM cause the
single-mapping diagnostic to fail closed, not silently select the first.

An empty, partial, unstable, unresolvable or ambiguous graph is not PASS. A PASS
means only this read-only in-memory identity chain was qualified. It does not
prove global LUN deduplication, external-array identity, resource materialization
or persistence of a new relationship. E2's existing live foreign-parent evidence
and E3's conditional identity evidence remain separate and unchanged.

## Isolated transport, lifecycle and reporting

Integration review found that the older E4.2 `HttpsURLConnection` transport can
inherit global proxy/authentication/cookie handlers. It is **not** used by the
diagnostic. A new diagnostic-only `IsolatedSoapTransport` implements the existing
SOAP transport interface with direct JDK TLS, explicit operation/cookie handling,
strict pre-request chain/SAN checks and bounded HTTP/XML data. The original
default transport is not silently claimed hardened. Operations retains its
separate E4.5 transport, endpoint, identity and TLS context. Integration testing
also exposed implicit SOCKS proxy selection in an unconnected default TLS
socket. Both diagnostic transports now connect an explicit
`Socket(Proxy.NO_PROXY)` before layering TLS; this corrects the earlier E4.5
proxy-isolation claim rather than treating it as already established.

Both binding classes construct private JVM-mode TLS contexts with the default
TrustManagerFactory and JVM trust roots, instead of inheriting mutable
`SSLContext.getDefault()`. Another integration replacing the global default
with a permissive context must not bypass these clients' certificate-chain
checks. This does not promise immunity to administrator changes to JVM trust
stores or installed security providers.

Configuration is Operations-managed SDK data, not fixture JSON, environment
secrets or collector-local files. Enterprise trust retains the approved CA-only
contract; opaque IDs, unsupported leaf-only delivery and verification-disable
flags fail closed. Both endpoints must validate their configured names. If JVM
trust is insufficient and the platform cannot supply supported CA material, the
experiment is blocked; do not substitute insecure TLS or invent a certificate API.

Disabled is the initial/default state. Both `diagnostic_enabled=true` and
`authorize_once=true` are required before execution. The `test(TestParam)`
configuration-validation callback does not decrypt secrets, connect, consume
authorization or replace the running configuration; `configure(AdapterConfig)`
does retire the prior generation. A Validate Connection success is explicitly **configuration-only,
not runtime proof**.

Execution is one-shot per diagnostic Java object, with a 150-second caller wait and
one worker. Cancellation/discard/configuration retirement cannot spawn another
worker while an old one is retiring. Identical configuration refresh cannot
re-arm a consumed instance. Restart, reinstantiation or failover can create a new
object: this is **not** a durable cluster-wide exactly-once guarantee. Stop the
test on placement changes and disable collection after observing its terminal
result; do not leave an authorized diagnostic scheduled indefinitely.
Cancellation closes active sockets, but independent SOAP/logout and Operations
token-cleanup budgets are up to 30 and 5 seconds respectively. Worker retirement
can outlast the caller deadline; JVM DNS or platform accessors cannot be forcibly
terminated. A retiring worker cannot authorize another execution on that object.

Only fixed stage/state/failure categories and VM/mapping/LUN counts are reported.
There are no raw ResourceKeys, identifiers, credentials, tokens, response bodies
or exception causes in the report. Repeated collection does not rerun APIs and
retains the prior terminal counts, labeled as no new execution. Cleanup failures
are identified separately from primary API collection failures. Incomplete or
cancelled execution is not reported as a successful runtime qualification.

## Minimal future collector configuration and procedure

The exact adapter-local procedure and candidate metadata are in
`docs/read-only-diagnostic.md` and `docs/diagnostic/` within the independent
adapter repository. These are preparation artifacts, **not an installed PAK**.
The candidate XML/resource bundle must be included under the documented classpath
resource path by a separately prepared diagnostic package; it is not added to
the active POC descriptor.

Required ordinary nonunique settings:

| Setting | Contract |
|---|---|
| `vcenter_endpoint` | Certificate-valid HTTPS `/sdk` URL |
| `trust_mode` | `jvm` or supported instance-managed `enterprise_ca` |
| `discovery_scope` | `single_vm_current_host` |
| `ops_endpoint` | Certificate-valid Operations FQDN HTTPS `/suite-api` |
| `ops_trust_mode` | Independent Operations trust selection |
| `target_vcenter_uuid` | Exact verified vCenter instance UUID |
| `target_vm_moid` | Exact VM MOID scoped to that UUID |
| `target_disk_key` | Expected positive virtual-disk key |
| `diagnostic_enabled`, `authorize_once` | Exact booleans as text; initially false |

Associated credential: `rdm_vcenter_readonly`, username/password, persisted by
Operations. Operations authentication uses only the distinct injected SDK slot;
no second integration's credentials or implicit administrator rights are assumed.
Actual target identities belong only in authorized Operations configuration or
ignored restrictive local evidence, never this document or a tracked fixture.

Future operator sequence, **not authorized for execution now**:

1. Resolve packaging/loader/trust prerequisites below. Obtain explicit approval
   for the distinct diagnostic package and a new development-only instance; do
   not upgrade, reconfigure or replace the working build-9 instance.
2. Use the established lab installation procedure only after that approval.
   Confirm the distinct adapter kind/entrypoint before installation. Snapshot
   existing VM/RDM/LUN topology and counts; the intentionally created diagnostic
   adapter instance is platform configuration, not a discovered mapping/LUN.
3. Configure the fields above and associated read-only vCenter credential, with
   execution flags false. Verify strict trust from the intended collector role.
   Configuration validation alone is not discovery/authentication evidence.
4. After explicit read-only execution authorization, enable and authorize the
   one-shot diagnostic on the new instance. Observe its first terminal SDK status.
   Expected runtime evidence is a fixed PASS graph report with counts **1/1/1**,
   not merely Collecting, Data Receiving or Validate Connection success.
5. Confirm there are no new discovered topology objects or relationships and
   existing topology is unchanged. Repeated collection must make no new API run.
   Stop on any unexpected result, scope, TLS/auth/RBAC failure, timeout, duplicate,
   unexpected inventory change or collector movement; never widen permissions or
   relax matching/trust to force a pass.
6. Disable collection and disarm the new diagnostic. Preserve only sanitized
   status evidence. Do not automatically uninstall/delete shared credentials or
   touch the existing POC resources. Any later cleanup needs its own exact scope.

This sequence is conditional, not a currently executable install command: E4.6
creates no diagnostic PAK and has not established platform acceptance of its
direct interface, descriptor or UI flow. No guessed API bypass is prescribed.

## Offline validation and review

Adapter-local additions (paths relative to its independent repository):

- `src/com/vcfcf/adapters/rdmtopologypoc/diagnostic/DiagnosticRuntime.java`
  and `ReadOnlyDiagnosticAdapter.java`: guarded coordinator and direct SDK lifecycle.
- `src/com/vcfcf/adapters/rdmtopologypoc/discovery/IsolatedSoapTransport.java`:
  bounded diagnostic transport, including balanced SOAP-session cookie parsing.
- `tests/com/vcfcf/adapters/rdmtopologypoc/diagnostic/DiagnosticRuntimeTest.java`
  and `DiagnosticTlsTest.java`; discovery helpers `DiagnosticSoapFixture.java`
  and `IsolatedSoapTest.java`; Operations helper `DiagnosticOpsFixture.java`.
- `scripts/run-diagnostic-tests.sh`, `docs/read-only-diagnostic.md`,
  `docs/diagnostic/diagnostic-describe.xml` and its `resources.properties`.

Exactly four pre-existing production sources changed relative to the E4.6
starting snapshots: `VimDiscoveryClient.java`, `RuntimeDiscoveryBinding.java`,
`OperationsBinding.java` and `OpsHttpsTransport.java`. The active entrypoint,
fixture parsers, resource identities, descriptor, adapter metadata and existing
PAK are byte-for-byte unchanged from that checkpoint. Earlier uncommitted
E3/E4 work remains present; this increment neither commits nor stages it.

| Offline check | Result |
|---|---|
| Diagnostic coordinator, real SDK empty results, shared provider/SOAP composition, publication bytecode guards | PASS, 243 synthetic assertions |
| Isolated SOAP wire validation | PASS, 22 assertions |
| Synthetic localhost TLS/integration | PASS, 19 assertions; enterprise CA, hostname/chain rejection, permissive global context rejection, zero global proxy/auth/cookie callbacks |
| Existing Operations provider | PASS, 345 assertions |
| Existing runtime binding | PASS, 62 cases |
| Existing discovery foundation | PASS, 55 cases including localhost TLS |
| Existing fixture/topology regressions | PASS, 8 topology/descriptor tests, 42 invalid runtime cases, 34 invalid LUN cases plus positive/idempotence matrices |
| `validate-sdk` | PASS, 21 production sources; legacy source/target-11 warning and deprecated SDK API note remain |
| Diagnostic compilation and dependencies | PASS, `--release 11`; JDK modules, supplied SDK and project classes only; no new runtime library or downloaded dependency |
| Complete factory tests | 2,500 passed, 15 skipped, 131 deselected, one unchanged failure, 293 warnings |
| Full content validation, skill parity, path audit | PASS; 5 paired/7 Codex-only skills; six standing path warnings, no dead references |

The unchanged factory failure is
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
its expected no-repository message differs from the conservative unknown
Git-ignore verdict in this environment. No unrelated correction was made.
Local socket tests required sandbox permission for synthetic localhost servers;
they did not contact VMware systems. No build, package comparison or installation
is claimed for this unregistered diagnostic candidate.

Independent [SDK review](../../context/reviews/rdm-topology-e46-sdk-review.md)
and [security review](../../context/reviews/rdm-topology-e46-security-review.md):
**APPROVE**, each with zero outstanding BLOCKING/WARNING/NIT findings. Both
independently reran the final 243/22/19 diagnostic suites. Approval covers dormant
offline preparation only, not installation or execution.

Factory HEAD remains `f53bb603e0b112e4febe9acc09cb4d2c6b1f7315`;
adapter HEAD remains `dc7e83afc7aee75536faaf6dd7b86628f74588c1`. Both worktrees
retain uncommitted work. Neither index contains staged files. `.claude/`,
immutable reference material and release workflows are unchanged. Existing
build-9 PAK SHA-256 remains
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.

## Remaining prerequisites and next increment

The supplied SDK alone lacks platform Commons Configuration linkage needed by
`AdapterDescribe.make`; actual descriptor loading could not be completed offline.
No dependency was installed, fabricated or redistributed. XML well-formedness,
compilation and empty SDK payload tests are not equivalent to successful
controller installation. A future package must supply its descriptor resource
and rely on legitimately available platform dependencies.

Other empirical prerequisites remain: direct-interface controller lifecycle and
UI acceptance; actual associated/injected secret decryption; effective resource-
read visibility; collector/Cloud Proxy DNS/firewall routing; supported CA delivery
and propagation; the strict HTTP representation subset; cancellation/provider
behavior and process/failover lifecycle. Exact least-privilege role identifiers
are not invented, and caller-visible results never authorize stale deletion.

Next: prepare a distinct diagnostic packaging candidate and qualify those
contracts in a separately authorized development experiment, with graph reporting
only. No automatic topology publication, existing-instance migration or new
release infrastructure is proposed.

**Disposition: offline implementation/review COMPLETE; collector execution
BLOCKED pending those prerequisites and separate explicit authorization.**
