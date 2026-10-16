# E4.6 — Independent read-only diagnostic security review

**APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT outstanding**, for offline
implementation and diagnostic preparation only. This is not approval to install,
execute against VMware endpoints, migrate the working instance or publish topology.

## Scope and authority

Reviewed the new diagnostic coordinator, direct SDK lifecycle carrier, isolated
SOAP transport, target-scoped discovery overload, narrow configuration-binding
changes, Operations transport correction, synthetic tests, candidate metadata and
operator instructions in the independent RDM adapter repository. Reviewed the
[E4.6 implementation record](../../designs/managementpacks/vsphere-rdm-topology-e46-read-only-diagnostic.md)
against the E4.1–E4.5 contracts and actual supplied SDK interfaces.

Authority: the SDK reviewer contract, [reviewer doctrine](../authoring/guide_reviewer_doctrine.md),
RULE-001 source-of-truth, RULE-008 no-secrets, RULE-012 defect registry, and the
Tier 2 skill's scoped-identity, resource-hygiene and gap-honesty requirements.
The proprietary compile SDK is local-only, not reproducible from Git; it was
neither copied nor redistributed.

## Independently executed checks

| Check | Actual result |
|---|---|
| Final diagnostic runner, after balanced-cookie correction | **243 coordinator + 22 SOAP wire + 19 localhost TLS/integration assertions passed**, exit 0 |
| Existing Operations provider runner, full synthetic TLS | **345 assertions passed**, exit 0 |
| Existing provider runner without sockets | **281 assertions passed**, exit 0 |
| Existing runtime-binding runner | **62 deterministic cases passed**, exit 0 |
| `validate-sdk` | **PASS**, 21 production sources compiled |
| Java-11 API compilation/dependency analysis | PASS; JDK plus platform SDK and existing adapter classes |
| Adapter whitespace check | PASS |

The first full diagnostic attempt was denied socket creation by the sandbox;
the subsequent explicitly approved runs used ephemeral synthetic localhost TLS
servers only. No VMware endpoint, real credential or private evidence was used.
The validator retains its existing source/target-11 warning and the SDK lifecycle
API has a deprecation note; the standalone runners compile with `--release 11`.
No new PAK or installation candidate exists, so no build/comparison result is
claimed by this review.

## Security findings and resolution

- **Technically empty publication boundary.** `ReadOnlyDiagnosticAdapter`
  implements `AdapterInterface3` directly. It does not inherit `AdapterBase` or
  the framework's automatic metrics/properties/events/resource behavior.
  Actual SDK `CollectResult` and `DiscoveryResult` payloads remain empty on
  successful, failed, disabled, repeated, stopped and discarded paths. Only
  sanitized adapter status is returned. No relationship/resource/metric emission
  method is reachable from the coordinator. The candidate kind and descriptor
  are distinct and unregistered; active POC metadata and entrypoint are not
  repurposed.
- **Explicit execution gate.** Configuration and validation inspect credential
  metadata but do not retrieve passwords or connect. Both exact lowercase flags
  are required before one execution. Validation does not arm/reconfigure the
  running object. Configuration stamps, identity association checks, generation
  retirement and final rechecks reject mutable-carrier changes. No second worker
  starts on the same object after consumption, timeout or cancellation; retired
  results cannot overwrite a new generation.
- **Honest deadline/authorization limits.** The caller waits at most 150 seconds;
  underlying cleanup has separate bounded allowances. JVM DNS/platform accessors
  may outlive cancellation and cannot be forcibly killed. One-shot consumption
  is object-local, not durable across restart/failover. Instructions explicitly
  require stopping the separate diagnostic and resetting both flags false after
  its first terminal result. No durable exactly-once guarantee is claimed.
- **Real scope and identity.** SOAP retrieves the exact configured VM MOR, its
  current host storage inventory and the same VM's consistency fence; it does
  not create a recursive container view and merely filter its results later.
  Operations retains bounded caller-visible pagination and fresh selected-key
  confirmation. Complete original foreign identifiers, ordering, flags and valid
  empty nonunique values are retained. The diagnostic requires exactly one RDM,
  the expected disk key, exact host-local backing-UUID join and qualified
  LU-associated NAA/canonical agreement. Empty/partial/unstable/ambiguous or
  unresolved graphs cannot become PASS.
- **Separate credentials and endpoints.** Associated vCenter credentials and
  injected per-instance Operations credentials use their actual SDK carriers.
  No relabeling, another integration's credential, administrator assumption,
  maintenance file, environment fallback or guessed internal endpoint exists.
  Public Suite API token release is authentication cleanup, not inventory
  mutation. Primary failures remain primary; cleanup-only failure prevents PASS.
- **Global handler isolation corrected, not presumed.** The diagnostic bypasses
  the older URLConnection SOAP path. Integration testing exposed that an
  unconnected default TLS socket could still consult global SOCKS proxy
  selection. Both diagnostic transports now connect `Socket(Proxy.NO_PROXY)`
  before layering TLS. The real integrated test installs global proxy, cookie
  and authenticator callbacks and verifies zero callbacks. This supersedes the
  earlier E4.5 proxy-isolation claim; it does not claim the unused E4.2 default
  URLConnection transport was hardened.
- **Strict trust and hostname checks.** Both JVM-mode binders construct private
  TLS contexts from the default TrustManagerFactory/JVM trust roots, rather
  than inheriting mutable global `SSLContext.getDefault()`. Synthetic replacement
  with a permissive default does not admit the untrusted CA. Enterprise trust
  keeps the bounded CA-only contract and rejects unresolved IDs/disable flags.
  Approved CA success, untrusted chain, wrong hostname and independent SAN
  rejection with a permissive test trust manager are exercised before HTTP
  credential bytes. No global TLS mutation occurs in production code.
- **Wire and output containment.** Diagnostic SOAP permits only the required
  read/session lifecycle operations, bounded strict HTTP/XML framing and one
  explicitly managed session cookie. Duplicate/unbalanced cookies, ambiguous
  framing, unsupported encodings/trailers and exact header-budget overflow
  reject. Request, response, parsing and execution budgets remain bounded.
  Reports expose only static stage/state/code and counts; no raw identities,
  fixture, ResourceKey, body, secret, token or chained remote exception appears.

The global-handler exposure, private-JVM-context concern, final header-LF budget,
balanced-cookie validation and object-local authorization caveat were resolved
or explicitly bounded and regression-tested, not waived.

## Remaining qualification boundary

Platform Commons Configuration linkage required by `AdapterDescribe.make` is
absent from the SDK-only test classpath. Its loader failure is sanitized and
reported honestly; candidate XML parsing and compilation are not controller
installation proof. No dependency was fabricated or installed to conceal this.

Still unqualified: direct-interface collector/controller acceptance, candidate
packaging/UI behavior, actual credential decryption/token acceptance and RBAC,
managed CA representation/delivery, collector/Cloud Proxy routing, strict gateway
HTTP compatibility, supported JDK/FIPS providers and placement/failover lifecycle.
Configuration validation is not runtime authentication proof. A PASS would prove
only one qualified in-memory chain, not topology persistence or global LUN
deduplication. No deployment or live-execution authorization follows from this
review.

Registry check: `knowledge/context/defects.md` inspected; **no open defect affects
the RDM adapter**. No closure or surviving new defect registration is proposed.

**If shipped as-is:** the registered build-9 fixture adapter is unchanged. The
new diagnostic remains an unregistered, publication-free candidate requiring a
separately approved package and read-only lab qualification before execution.
