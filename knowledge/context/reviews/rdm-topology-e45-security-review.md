# E4.5 — Independent native Operations provider security review

**APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT**, for dormant offline
implementation only. This does not authorize installation, live authentication,
automatic collection or topology publication.

## Scope and independent verification

Reviewed the complete new `ops/` production package, synthetic tests, runner and
adapter-local provider documentation in the independent RDM adapter repository,
plus the [E4.5 record](../../designs/managementpacks/vsphere-rdm-topology-e45-operations-provider.md).
Read E4.1–E4.4 architecture/contracts and inspected actual local SDK signatures
and `AdapterCredentialConfig.getPassword()` bytecode. Its platform `Crypt`
dependency is real; successful collector decryption is not established offline.
The proprietary SDK is local-only, not reproducible from Git; no binary was
copied or redistributed.

Authority: SDK reviewer contract and [reviewer doctrine](../authoring/guide_reviewer_doctrine.md),
RULE-001 source-of-truth, RULE-008 no-secrets, RULE-012 defect registry, and the
Tier 2 skill's scoped identity, classloader and gap-honesty requirements.

| Independently executed check | Result |
|---|---|
| Final provider runner, synthetic localhost TLS included | **345 assertions passed**, exit 0 |
| Final provider runner `--no-network-tests` | **281 assertions passed**, exit 0 |
| Existing runtime-binding runner | **62 deterministic cases passed**, exit 0 |
| `validate-sdk` | **PASS**, 18 production sources; existing source/target-11 warning |
| Provider Java API/dependency check | `--release 11` passed; JDK `java.base`, existing discovery classes and platform-provided SDK only |
| Adapter whitespace check | PASS |

Full TLS execution required explicit permission after the sandbox denied socket
creation. Tests used temporary synthetic CA/server keys and loopback servers,
not VMware endpoints, environment credentials or private inventory. No new PAK
or install candidate exists; build/comparison is inapplicable to this dormant
increment. The separate runner verifies Java-11 APIs despite the existing
validator warning.

## Security assessment

- **Injected-only identity:** the source is the actual SDK
  `AdapterConfig.getAdapterCredentials()` carrier. Missing material, changed
  association, invalid values and decryption/linkage failures reject with static
  categories. No target/VMware credential reuse, maintenance file, service-account
  fallback or guessed auth source exists. Secret-array ownership and closure are
  explicit; request bytes are cleared. Immutable SDK/token/serialization Strings
  remain a documented erasure limitation, not a secret-logging path.
- **Authentication versus authorization:** public token acquisition and only
  resource-list/detail GETs are allowed; 401 and 403 remain distinct. The current
  token is released through authenticated bodyless POST. Cleanup has a separate
  bounded budget and static diagnostic, and cannot mask the primary outcome.
  No resource/relationship/configuration write is exposed.
- **Transport isolation:** direct native `SSLSocket` avoids inherited global
  `Authenticator`, `CookieHandler` and proxy behavior without changing global
  handlers. Tests install hostile synthetic global handlers and establish they
  are never consulted, including a Basic challenge and Set-Cookie response.
  Redirects are not followed and no alternate identity is attempted.
- **TLS before secrets:** normal chain validation, HTTPS endpoint identification
  and an independent SAN check occur before any HTTP bytes. Tests cover approved
  CA success, untrusted CA and hostname rejection. A deliberately permissive
  test-only `X509ExtendedTrustManager` still cannot bypass the independent name
  check: the mismatched server completes TLS, observes EOF with zero HTTP bytes,
  and its thread completion is explicitly checked. Production has no permissive
  trust manager or hostname-disable mode.
- **Trust delivery remains honest:** enterprise mode validates bounded unique
  current CA PEM/DER material and keyCertSign, rejects leaf pins/unresolved IDs
  and hostname/date-disable flags, and constructs isolated trust. JVM trust is
  an explicit alternative. Actual SDK-managed material delivery, collector
  movement, FIPS/provider behavior and Cloud Proxy routing are not proven.
- **Bounded hostile inputs:** fixed public request allowlists, request/cycle/
  cleanup deadlines, response/header/JSON complexity bounds, finite pagination,
  aggregate 32-MiB response budget and 2-Mi-character selected-key budget are
  enforced. Unrequested keys are validated but not retained across pages;
  bounded UUID/scope sets still detect duplicates. Slow-drip deadlines and
  fixed-length/chunked/EOF overflow rejection are exercised. DNS cancellation
  limits and the one unusable transport's possible lingering daemon are explicit.
- **Deliberately narrow HTTP:** duplicate headers, CL+TE, malformed framing,
  unsupported transfer/compression, chunk extensions/trailers and informational
  responses fail closed. Tests exercise framing attacks and supported body
  forms. This is not broad HTTP interoperability; real Operations gateway framing
  remains a prerequisite. The response implementation never follows remote links.
- **Exact foreign identity:** both uniqueness-bearing vCenter UUID and VM MOID
  must match. Full original identifier names, values, order, flags and display
  name are retained; explicit empty nonunique strings survive, absent/null do
  not become invented strings. Duplicate/ambiguous/unscoped/changed keys reject.
  Fresh detail must agree with the complete listing key. Invalid snapshot input
  and expired/overflowed freshness fail with sanitized categories, not raw NPEs.
- **Coverage is not overstated:** complete pages and fresh detail do not prove
  globally atomic inventory or sufficient RBAC. NOT_FOUND means caller-visible
  absence, never permission to delete stale topology. Installed build-9 fixture
  behavior, discovery engine and additive relationships are not rewired.
- **Diagnostics:** exception messages, causes, suppressed exceptions and DTO
  string representations do not emit remote bodies, credentials, tokens or raw
  ResourceKeys. Malformed API/credential/clock/transport responses fail closed.

The initial inherited-global-handler concern, temporary secret-array ownership,
manual-SAN test completion proof and exact header LF accounting were corrected
by the author and independently rechecked. No finding was waived.

Registry check: `knowledge/context/defects.md` inspected; **no open defect affects
the RDM adapter**. No closure or surviving new defect registration is proposed.

## Remaining boundary

`OperationsBinding.production()` continues to reject `RUNTIME_UNQUALIFIED`.
Native injected authentication, effective least-privilege visibility, configured
FQDN reachability from each collector role, managed certificate delivery and
gateway interoperability still need separately authorized runtime qualification.
Recommended E4.6 remains read-only diagnostic/lifecycle composition and sanitized
in-process evidence, not topology publication or release infrastructure.

**If shipped as-is:** the registered build-9 fixture adapter is unchanged; the
new provider is a dormant, bounded read-only implementation candidate. Local
tests do not confer deployment or production-activation approval.
