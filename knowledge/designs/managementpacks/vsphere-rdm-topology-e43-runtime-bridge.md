# E4.3 — Runtime configuration and Operations identity boundary

## Outcome and scope

**Offline foundation implemented; production Operations bridge remains blocked.**
This extends the [E4.2 discovery foundation](vsphere-rdm-topology-e42-discovery-foundation.md)
under the [E4.1 architecture](vsphere-rdm-topology-e41-automatic-discovery.md).
New code is dormant: no registered adapter entrypoint, descriptor, fixture
parser, build version or existing PAK is changed. The independent adapter
repository remains `content/sdk-adapters/rdm-topology-poc`.

No live VMware calls, real credentials, private inventory or fixture files were
used. No topology publication, adapter reconfiguration, build, installation,
commit, tag or push occurred. Earlier worktree changes are preserved.

## Verified SDK contracts and implemented binding

Inspection of the locally supplied legacy SDK signatures and bytecode established:

- `ResourceConfig.getResourceIdentifiers()` exposes ordinary configuration;
  `getResourceCredential()` exposes the explicitly associated credential.
- `CredentialConfig.getCredenialFields()` is the actual accessor spelling.
  `CredentialFieldConfig.getValue()` decrypts password fields through platform
  `com.vmware.vcops.security.Crypt`, absent from the supplied compile SDK.
- `ResourceConfig.getTrustedCertificates()` exposes `CertificateConfig` objects
  with `getCertificateString()` PEM material and hostname/date enforcement flags.
  `getTrustedCertificateIds()` exposes opaque references, not certificate bytes.
- The separate injected `AdapterConfig.getAdapterCredentials()` carrier exists;
  its password accessor also depends on platform decryption. Its existence does
  not prove authentication, least-privilege RBAC or collector endpoint routing.

`runtime/RuntimeDiscoveryBinding.java` accepts only the owned adapter-instance
kind and exactly these proposed ordinary, nonunique settings:

| Setting | Accepted contract |
|---|---|
| `vcenter_endpoint` | HTTPS URL ending `/sdk`, no userinfo/query/fragment |
| `trust_mode` | `jvm` or `enterprise_ca`; never insecure |
| `discovery_scope` | `caller_visible_inventory` only |

The proposed associated credential kind is `rdm_vcenter_readonly`, with exactly
`username` (not a password field) and `password` (`isPassword=true`). These are
**future binding contracts, not fields exposed by the build-9 UI**. No credential
kind is added to the installed credential-free descriptor in this increment.
No existing VMware integration credential is accessed or reused implicitly.

Credentials are acquired through the real SDK accessor just before explicit
discovery, with fixed sanitized failures on decryption/linkage errors. Tests
inject synthetic values at a package-private seam, not a production fallback.
One-shot AutoCloseable leases erase char arrays on success, failure and close;
immutable SDK Strings and serialized SOAP buffers cannot be securely erased.
Malformed XML characters, empty fields, wrong flags/association and unexpected
fields fail closed. Configuration stamps reject changed endpoint/trust/settings;
normal SDK lifecycle must serialize configuration replacement and retire old
bindings. Arbitrary concurrent mutation of SDK carriers is not supported.

Enterprise trust parses bounded, valid, unique CA certificates directly from
SDK PEM material in memory. It rejects leaf-only pins, malformed certificates,
explicit hostname/date-disable flags and any unresolved certificate IDs rather
than guessing platform storage. JVM trust rejects conflicting supplied material.
The private SSLContext feeds unchanged E4.2 strict certificate-chain and dialed
hostname verification. There is no global SSL modification or node-local file.
Platform leaf-versus-CA representation, ID/material association, delivery and
failover remain unverified. Offline parser and transport tests are composition
evidence, not proof of Operations-managed trust propagation.

Fixed transport connect/read limits are 10/30 seconds; E4.2 cycle, pagination,
object, response/XML and cleanup limits remain in force. Caller-visible scope
is not evidence of exhaustive permissions and cannot authorize stale deletion.

## Scoped Operations resolver: explicit offline boundary

`runtime/ScopedOperationsResolver.java` implements the E4.2 `VmResolver`
interface, but contains no Suite API HTTP, token or localhost implementation.
`production()` always fails closed. `offline(...)` consumes a complete scoped
snapshot with expected vCenter UUID, collection generation and bounded monotonic
age (at most 120 seconds). Authentication/routing flags are **synthetic provider
inputs**, not verified production authorization.

The provider must supply a complete projection for the expected vCenter; mixed
scope, stale/future/overflowed age, incomplete results, generation mismatch,
unqualified routing and authentication/transport failures reject. Resolution
requires exact vCenter instance UUID plus VM MOID and delegates to the strict
immutable E4.2 key model. Every returned identifier name, value, ordering and
uniqueness flag is retained, including supported empty nonunique strings.
Duplicate candidates are ambiguous, never first-match wins; missing ResourceKeys
are never inferred from vCenter data. Two vCenters containing the same MOID
remain separate identities.

Existing ambient/maintenance-file credential fallbacks, permissive stitch TLS
clients and single-identifier resolvers are not reused. A supported production
provider still needs verified injected identity/decryption, least-privilege
inventory access, strict TLS/authentication/pagination and endpoint reachability
for the intended collector and Cloud Proxy placements.

## Source changes and offline validation

Exactly five adapter files are new for E4.3: the two `runtime/` classes above,
`tests/com/vcfcf/adapters/rdmtopologypoc/runtime/RuntimeBindingTest.java`,
`scripts/run-runtime-tests.sh` and `docs/runtime-configuration-boundary.md`.
The latter contains the standalone binding contract and test command.

| Check | Actual result |
|---|---|
| Runtime binding runner against supplied SDK | 62 deterministic cases passed |
| Full E4.2 discovery regression, including synthetic loopback TLS | 55 deterministic cases passed, exit 0 |
| Existing topology/fixture/LUN suites | 8 topology/descriptor, 42 invalid-runtime and 34 invalid-LUN cases plus existing positive matrices passed |
| `validate-sdk` | Passed, 13 production sources compiled |
| Java 11 API compilation / dependency analysis | Passed using `--release 11`; JDK plus platform-provided Operations SDK only |
| Complete factory test suite | 2489 passed, 20 skipped, 131 deselected; 1 unchanged setup-test failure |
| Changed-content and full content validation; skill parity | Passed; 5 paired and 7 Codex-only skills |
| Path-reference audit; both repository whitespace checks | Clear, with 6 standing path warnings; whitespace passed |

The unchanged factory failure is
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
the conservative unknown Git-ignore verdict differs from the expected no-repo
verdict. No unrelated correction was made. The full TLS regression needed
explicit permission for a temporary localhost test socket; no VMware endpoint
was contacted.

The existing validator source/target-11 system-modules warning and test-only
deprecated SDK setter note remain. No non-platform runtime dependency, runtime
download, Python process, storage-array API or proprietary SDK packaging is
introduced. The broad discovery foundation also uses JDK `java.xml`.

No new PAK or `pak-compare` result is claimed: active runtime/descriptor metadata
is unchanged, and this is not an installation candidate. Existing build-9 PAK
SHA-256 remains
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
Its presence does not establish deployed E4.3 behavior.

All ten pre-E4.3 baseline hashes were rechecked unchanged: adapter metadata,
descriptor, registered entrypoint, RuntimeFixture, five E4.2 production files and
the build-9 PAK. Factory and adapter Git tips remain respectively
`f53bb603e0b112e4febe9acc09cb4d2c6b1f7315` and
`dc7e83afc7aee75536faaf6dd7b86628f74588c1`. Neither index has staged changes;
both worktrees retain earlier uncommitted work. `.claude/`, immutable reference
material and GitHub workflows were not changed.

## Review and next increment

Independent [SDK review](../../context/reviews/rdm-topology-e43-sdk-review.md)
and [security review](../../context/reviews/rdm-topology-e43-security-review.md)
cover the dormant boundary, not live authentication or automatic collection.
Both independently report **APPROVE, zero outstanding findings**, with the final
62 runtime cases verified. No finding was waived to obtain approval.

The smallest E4.4 is targeted qualification of Operations-managed configuration
and certificate serialization, actual SDK password decryption, injected identity
RBAC and strict Operations endpoint routing on the intended collector roles.
Any live read-only checks require separate explicit authorization; no credential
retrieval or live verification is authorized by this record. Once these contracts
are established, implement the narrow read-only provider and serialized lifecycle
binding, still without topology publication. Do not guess an auth scheme or
expand fixture JSON to bypass the missing contracts.

**READY for review of this offline foundation; BLOCKED for production bridge
activation.** Descriptor migration, active automatic collection, shared-LUN
ownership and safe stale-edge reconciliation remain separate technical work.
