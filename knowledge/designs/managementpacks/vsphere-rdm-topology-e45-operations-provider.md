# E4.5 — Dormant native Java Operations identity provider

## Scope and implementation

Implements the read-only provider proposed in
[E4.4](vsphere-rdm-topology-e44-runtime-contract-qualification.md), alongside the
unchanged [E4.2 discovery engine](vsphere-rdm-topology-e42-discovery-foundation.md)
and [E4.3 binding](vsphere-rdm-topology-e43-runtime-bridge.md).
All Java additions belong to the independent repository at
`content/sdk-adapters/rdm-topology-poc`. No registered entrypoint, descriptor,
fixture parser, build version or relationship implementation is modified.

New adapter surfaces:

| Surface | Responsibility |
|---|---|
| `ops/OperationsBinding.java` in the existing Java source package | Explicit dormant Operations endpoint, independent JVM/managed-CA trust and associated injected-identity binding |
| `ops/OpsHttpsTransport.java` | Isolated direct TLS/HTTP transport, fixed public request allowlist, chain/name checks and bounded framing/I/O |
| `ops/OpsJson.java` | Bounded strict UTF-8 JSON decoding and safe authentication request encoding |
| `ops/SuiteApiVmProvider.java` | One-session batch resolution, complete bounded inventory pagination, fresh selected-resource reads and immutable scoped result |
| `ops/OpsException.java` | Static actionable sanitized failure categories |
| `tests/com/vcfcf/adapters/rdmtopologypoc/ops/OperationsProviderTest.java` | Synthetic provider, SDK-carrier, parser and loopback TLS/framing regressions |
| `scripts/run-ops-provider-tests.sh`, `docs/operations-identity-provider.md` | Standalone Java-11 test runner and exact adapter-local contract/limitations |

These are new dormant source files, not deployed capabilities. The production
factory explicitly refuses activation with `RUNTIME_UNQUALIFIED`; development
construction does not authorize connection. No resource, metric, property or
relationship publication is added. Existing build-9 credential-free fixture
behavior and VM/mapping/LUN identities remain isolated and unchanged.

## Authentication, transport and trust

The only credential source is the SDK-public injected
`AdapterConfig.getAdapterCredentials()` carrier. It is distinct from a vCenter
credential and checked for association changes. The real password accessor
depends on platform `Crypt` decryption; missing linkage or values fails closed.
Synthetic readers prove handling, not real collector decryption. No file,
environment, maintenance/automation user, service-account or VMware-integration
fallback exists. Owned secret arrays and request buffers are cleared; immutable
SDK Strings, token Strings and JDK serialization buffers cannot be securely
erased. No real secret is read by offline tests.

The public contract is the repository's `reference/docs/operations-api.json`:
token acquisition with username/password (no guessed authentication source),
`Authorization: OpsToken` on resource reads, and authenticated bodyless token
release. Release terminates authentication state, not inventory. Its sanitized
failure diagnostic is separate and cannot replace a primary result/error.
No internal endpoint or unsupported-API header is introduced.

An explicit HTTPS Operations FQDN ending `/suite-api` is required, separate from
the vCenter `/sdk` endpoint. The binding has no current descriptor/UI wiring.
Enterprise trust uses bounded SDK-managed CA certificate material, rejects
unresolved IDs, malformed/duplicate/non-CA anchors and hostname/date-disable
flags. JVM trust is an alternative; no insecure mode exists. Trust material is
in memory, not a collector-local fixture or manually synchronized directory.
Actual Operations delivery of CA material versus IDs/accepted leaf certificates
remains unqualified, as does failover propagation.

The transport uses native JDK `SSLSocket` and a deliberately small HTTP/1.x
response subset. This avoids inherited JVM-global HTTP authentication, cookie
and proxy handlers without mutating them. TLS chain checks and an independent
SAN match finish **before any credential-bearing HTTP request bytes** are sent.
Only exact public token/resource paths are accepted; no redirect, proxy,
alternate identity, external process or download is used.

The limited HTTP implementation accepts bounded content-length, chunked or
connection-close bodies. It deliberately rejects ambiguous framing, repeated
headers, compression, informational responses, chunk extensions and trailers.
Some otherwise valid HTTP responses therefore fail closed: compatibility with
the target Operations gateway is a runtime prerequisite, not proven by localhost
tests. No connection is reused. JDK-native transport is not a claim of broad
HTTP-client interoperability or collector/FIPS-provider qualification.

Concrete budgets: connect/read 10/30 seconds, request at most 40 seconds, capture
120 seconds plus independent 5-second token cleanup; 4 MiB per response, 32 MiB
aggregate successful response bodies per capture, 64 KiB header/chunk-line
metadata, 512 metadata lines and 8 KiB per line. JSON depth is 24, with at most
100,000 values, 16 KiB strings and 64-character numbers. Inventory is limited to
20,000 caller-visible VMs over 100 pages of 200, with 1,000 requested targets and
2 MiB retained selected-key text. All rows are validated, but only requested
keys are retained alongside bounded UUID/scope duplicate indexes. These combined
limits are ceilings, not a guarantee every 20,000-VM inventory fits the byte cap.
A timed-out/cancelled transport is retired. A non-interruptible platform DNS
resolver may leave its one daemon worker until resolution returns; the retired
transport cannot accumulate additional request workers. This limitation is
documented, not a claim that Java can forcibly terminate DNS resolution.

## Identity and failure contract

`capture(vcenterUuid, vmMoids)` uses one inventory scan and one token for a batch,
then performs a fresh GET for every selected resource UUID. Both
`VMEntityVCID` and `VMEntityObjectID` must exactly match and carry actual boolean
uniqueness flags set true. No case/identifier normalization is introduced.
Duplicate candidates or resource UUIDs, missing scope, malformed keys, wrong
kinds, missing/nonboolean flags and fresh-detail disagreement fail closed.

The immutable result retains the fixed validated VMware adapter/kind, original
display name and every identifier's name, exact value, order and uniqueness flag.
Explicit empty nonunique strings survive; absent/null values are not silently
coerced. It uses the unchanged E4.2 VM-key model and offers a resolver bridge
without exposing a mutable SDK key or publishing anything.

Finite pages, stable reported totals, expected page numbers/sizes and duplicate
detection guard completeness. These are not an atomic-inventory guarantee under
concurrent churn, and cannot prove RBAC completeness. `NOT_FOUND` means no match
in the caller-visible successfully enumerated scope, not global nonexistence.
Snapshots have bounded monotonic freshness; do not reuse them across collections.
Batch resolution avoids rescanning all inventory once per VM; the single-target
convenience method is not the recommended multi-VM collection integration.

Sanitized codes distinguish configuration/unqualified runtime/credentials,
unreachable endpoint, TLS, authentication (401), authorization (403), invalid
response, not found, ambiguity, invalid ResourceKey, identity mismatch, timeout,
response limit, incomplete paging and cancellation. Raw response bodies,
ResourceKeys, usernames, passwords, tokens and exception causes never appear in
diagnostics. Missing data never becomes a guessed foreign relationship.

## Validation and independent review

Run from the factory root with the legitimately supplied SDK:

```bash
VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
  bash content/sdk-adapters/rdm-topology-poc/scripts/run-ops-provider-tests.sh
```

The test runner creates ephemeral synthetic CA/server keys and localhost TLS
servers only. Sandbox socket binding required explicit local-test execution
approval; no VMware endpoint was contacted. `--no-network-tests` omits sockets.
Assertion counts below are assertions, not separate JUnit test-case counts.

| Check | Actual result |
|---|---|
| Frozen provider suite, including actual synthetic localhost TLS | **345 assertions passed**, exit 0 |
| Provider suite without sockets | **281 assertions passed**, exit 0 |
| Existing runtime binding / offline discovery | **62 / 54 cases passed** |
| Existing SDK topology/fixture/LUN suites | **8 topology/descriptor, 42 invalid-runtime, 34 invalid-LUN cases** plus positive/idempotence/convergence matrices passed |
| `validate-sdk` | **Passed**, 18 production sources compiled |
| Explicit Java 11 API compilation / production `jdeps` | Passed; new code requires only `java.base`, the platform SDK and unchanged discovery classes |
| Complete factory suite | **2500 passed, 15 skipped, 131 deselected; 1 unchanged failure** |
| Changed/full content validation, skill parity, whitespace checks | Passed; parity 5 paired / 7 Codex-only |
| Path-reference audit | Clear; 6 standing warnings |

The unchanged failure is
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
conservative unknown Git-ignore verdict versus expected no-repo verdict. No
unrelated fix was made. The SDK validator's existing source/target-11 warning
remains; the standalone runner separately compiles with `--release 11`.

Tests cover fake API pagination/identity failures and actual TLS authentication
request JSON, token/read/release flow, untrusted CA and hostname rejection,
independent SAN rejection with a permissive test-only ExtendedTrustManager
**before any HTTP bytes**, ignored global HTTP handlers, framing attacks,
slow-drip deadline, aggregate limits and redaction. They do not invoke actual
platform decryption or prove a current Operations principal's privileges.

Independent [SDK review](../../context/reviews/rdm-topology-e45-sdk-review.md) and
[security review](../../context/reviews/rdm-topology-e45-security-review.md):
**APPROVE, zero BLOCKING / WARNING / NIT outstanding** for the dormant offline
scope. Both reran the final frozen provider suite. Review findings concerning
global handler isolation, malformed JSON escapes, secret-array ownership,
hostname-test evidence, exact framing limits, snapshot input sanitization and
memory budgets were corrected and tested, not waived.

All 27 pre-E4.5 adapter source/test/script/metadata/artifact baseline hashes
remain unchanged. The existing build-9 PAK retains SHA-256
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
No new PAK build/comparison is applicable: there is no new installation candidate.
No non-platform dependency or proprietary SDK was copied, bundled or downloaded;
package-boundary assessment is static plus compilation/dependency evidence,
not a newly inspected built artifact. The broad foundation also uses JDK
`java.xml`. Test servers, keytool and synthetic readers are not production
runtime dependencies.

Exactly eight adapter files above, this factory record and the two review
reports are authored by E4.5. Both independent Git repositories retain earlier
dirty-worktree changes; neither index contains staged changes. `.claude/`,
immutable vendor material and GitHub/release infrastructure remain unchanged.
Nothing was committed, pushed, tagged or published. No live calls, credentials,
private fixture files, installed instance or VMware topology were accessed.

**COMPLETE / APPROVED for offline implementation; BLOCKED for production
activation until the remaining runtime prerequisites are qualified.**

## Remaining live prerequisites and E4.6

Still unproven: injected credential population/decryption and token acceptance on
the actual RDM instance, effective least-privilege VM visibility, FQDN routing
from every collector/Cloud Proxy, real gateway HTTP representation, cluster-
managed CA delivery and collector movement, platform runtime/classloader/FIPS
compatibility. Neither token acquisition nor complete pages alone proves RBAC
coverage. No administrator authority or another adapter's credentials is assumed.

Smallest E4.6: compose the dormant vCenter binding, batch Operations provider and
discovery graph behind an explicit read-only diagnostic/lifecycle boundary.
Verify configuration-generation replacement and resource cleanup with synthetic
tests first. Prepare an explicitly authorized in-process development-lab
qualification that reports sanitized identity/auth/trust capabilities and graph
counts only, never topology publication. It will require separate permission for
any installation/instrumentation/configuration needed to run it; none is
authorized by this record. Keep build 9 unchanged until migration is explicitly
approved. No release infrastructure work is necessary.
