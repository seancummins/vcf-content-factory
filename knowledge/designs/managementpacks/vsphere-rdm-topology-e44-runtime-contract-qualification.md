# E4.4 — Native Operations identity and runtime contract qualification

## Disposition

**Native global lookup: unavailable in the inspected SDK. Operations bridge:
API-level design qualified, target-runtime authentication and trust unverified.**
The [E4.3 dormant binding](vsphere-rdm-topology-e43-runtime-bridge.md) and live
build-9 fixture adapter remain unchanged. No discovery/publication is activated.
This is offline qualification, not a claim that a current RDM collector has
authenticated successfully. No live calls, secrets or private evidence were read.

## Evidence and native lookup

Primary evidence: the operator-supplied legacy SDK 2.2, inspected using `javap`
and its JAR index. It is a **local-only proprietary artifact, not reproducible
from Git**; findings are summarized here without copying its binary. SHA-256:
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
Deterministic qualification tests are
`tests/managementpacks/test_rdm_e44_sdk_contract.py`.

| Actual SDK surface | What it establishes, and what it does not |
|---|---|
| `AdapterBase.getAllMonitoringResources()` | Delegates to `AdapterCache.getMonitoringResources()`, not global inventory |
| `AdapterBase.getMonitoringResource(ResourceKey)` | Delegates to the instance cache, ultimately a map lookup |
| `AdapterCache.update(AdapterConfig)` | Ingests supplied monitoring/stopped/removed configuration; does not fetch foreign VMware inventory |
| `ResourceKey`, `ResourceKindIdentifiers`, `Relationships` | Identity representation/validation and outgoing relationship declarations, not lookup or authentication |
| `AdapterConfig.getHostCollectorID()` | Collector integer identity, not an Operations service endpoint |
| `AdapterBase.getConnectionURL(AdapterConfig)` | Returns null by default; URL-list hooks describe adapter target connections, not Operations service discovery |

The SDK contains no `SuiteAPIClient` and `AdapterBase` has no such accessor.
The similarly named vendor client belongs to a distinct vendor framework, not
the SDK. An outgoing foreign key can be resolved by Operations when processing
a relationship, as proven by E2, but that is not a read API returning the full
existing key. Constructing a guessed key from two vCenter fields would violate
the approved requirement to preserve the complete returned VMware ResourceKey.
Therefore native cache access cannot replace the scoped Suite API read.

## Authentication strategy and support boundaries

Preferred candidate: the SDK-public chain
`getAdapterConfig().getAdapterCredentials()` returns
`AdapterCredentialConfig`, distinct from the associated **vCenter** credential
on `ResourceConfig.getResourceCredential()`. `getUserName()` returns the
injected principal; `getPassword()` invokes platform
`com.vmware.vcops.security.Crypt.getDefaultCrypt().decrypt(...)`. That class is
not in the supplied SDK; do not infer it is absent on a real collector.
No accessor is called on real configuration during this investigation.

The [injected credential evidence](../../context/api-surface/per-instance-suiteapi-credential-contract.md)
and [later live lesson](../../lessons/cross-mp-stitch-cp-identity-and-edge-mechanics.md)
document an instance-UUID principal and resource-read success, including Cloud
Proxies, in other adapters on historical 9.0.2/9.1 environments. Retain that
positive evidence. It does not establish every supported version, this RDM
instance's credential population/decryption or its current object visibility.
Public Java signatures are verified; provisioning, privilege scope and vendor
support/lifetime guarantees for the injected identity remain platform contracts
to qualify. No administrator privileges are inferred.

Use the **public** Suite API, documented in `reference/docs/operations-api.json`:

- `POST /api/auth/token/acquire`: username/password, optional `authSource`;
  `Authorization: OpsToken <token>` thereafter. Do not guess `authSource=Local`
  for an injected principal; qualify the documented optional-source flow.
- `GET /api/resources?adapterKind=VMWARE&resourceKind=VirtualMachine&page=...&pageSize=...`:
  bounded complete pagination, followed by exact in-memory scoped matching.
  No `resourceIdentifiers` query parameter is documented on this GET.
- `GET /api/resources/{id}`: fresh confirmation of the exact selected resource.
- `POST /api/auth/token/release`: authenticated current-session cleanup, not an
  inventory mutation; cleanup failure must not obscure the primary result.

Both public and internal local specifications were inspected. These operations
are public; the `/suite-api` base prefix does **not** make them internal or
require an unsupported-API header. Older contract prose describing all downstream
Suite API use as internal is overbroad; older plaintext-password and
operator-supplied-injected-credential descriptions are superseded by its own
decryption correction and the later lesson. No new internal endpoint is needed.

If injection is unavailable, fail closed. An explicitly declared, independently
authorized Operations service credential is a possible future supported public
API path, not implemented or required here. It would require a configuration
design change, not reuse of vCenter/VMware credentials or a maintenance-file
fallback. Do not add another account merely to conceal a failed injection test.

## Routing, trust and least privilege

Conservative endpoint choice: an explicitly configured, certificate-valid
`https://<Operations-FQDN>/suite-api` reachable from every intended collector.
There is no SDK service-discovery guarantee for this URL. Configure DNS,
firewall TCP 443 and the correct SAN name for local collectors **and** Cloud
Proxies; do not redirect credentials to another host or silently fall back.

[Historical routing evidence](../../context/api-surface/casa-injected-vs-raw-client.md)
documents a Cloud Proxy localhost route through platform HTTPD/haproxy tunnels;
node-certificate transport is outside Java and does not replace user-token
authentication. This is empirical historical routing, not a public SDK endpoint
contract or current strict-TLS qualification. Do not assume a loopback certificate
matches `localhost`, or require adapter access to node keys/CASA internals.

Use strict chain/date and independent dialed-host SAN verification. Prefer JVM
enterprise trust when legitimately present on all collector roles; otherwise
use instance-managed trust. Besides E4.3 PEM carriers, the actual SDK exposes
`AdapterBase.getAdapterTrustStore()`, `getCertificateMap()` and
`getAdapterTrustManager()`. These are credible native integration surfaces, not
proof of CA contents, ID-to-material association, collector propagation or
failover. Qualify their real representation before adapting the E4.3 binder.
An SDK trust manager/verifier may honor accepted certificate flags disabling
hostname/date checks; it is not unconditionally strict. Never copy those
overrides or weaken E4.3's CA-only, no-disable policy. Keep separate vCenter and
Operations trust scopes; no node-local synchronization, global SSL change or
insecure default is acceptable.

Minimum authorization is token authentication plus resource read and object/group
visibility covering the intended VMware VM scope. The public spec does not map
these operations to exact named role/privilege IDs, so no role name is invented.
No credential-read, adapter-management, resource-write, relationship-write,
administrator or configuration-changing permission is needed for this bridge.
401 is authentication failure; 403 is authorization failure; an empty/partial
visible result is not proof of global absence. Complete pages are necessary but
cannot prove RBAC completeness without independently confirming assigned scope.

## Existing framework reuse assessment

Repository sources inspected under
`src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/`:

- `stitch/AmbientCredential.java`: injected carrier access is useful evidence;
  its file-backed fallbacks are forbidden for this adapter.
- `stitch/SuiteApiStitchClient.java` and `VcfCfAdapter.java`: token lifecycle and
  endpoint patterns are informative, but the current platform connection installs
  trust-all plus an all-true hostname verifier, including remote URLs. Do not
  reuse that transport. Its token-release request representation also requires
  correction against the public authenticated-session contract before any reuse.
- `stitch/ForeignResourceResolver.java`: one-identifier indexing, last-wins
  duplicates, permissive boolean parsing and failure-to-empty behavior do not
  satisfy scoped, complete, fail-closed RDM resolution. Keep E4.3's strict model.
- The existing additive `RelationshipBuilder.parentForeign(...)` remains the
  future publication mechanism. Do not replace it with resource/relationship
  REST writes, TraversalSpecs or relationship-shaped properties.

No framework or adapter implementation is changed by this assessment.

## Prepared operator-only route probe and its limits

**Do not execute without separate explicit authorization.** From each intended
collector role, an operator can run the following credential-free, read-only
route/TLS probe if an approved `curl` is already available. It is a diagnostic,
not a deployed adapter dependency. Set `RDM_OPS_ROUTE_URL` privately to the exact
certificate-valid HTTPS endpoint, including `/suite-api/api/resources` and the
fixed query above with `page=0&pageSize=1`. Do not include userinfo, credentials,
tokens or redirects; unset the variable afterward. An optional administrator-
supplied CA bundle can be selected with `--cacert <approved-CA-bundle>` for this
diagnostic only; never `--insecure`. No credential file or environment profile
is loaded. Do not run with shell tracing or save a verbose transcript.

```bash
RDM_OPS_ROUTE_URL='https://<approved-Operations-FQDN>/suite-api/api/resources?adapterKind=VMWARE&resourceKind=VirtualMachine&page=0&pageSize=1'
curl --disable --silent --output /dev/null --write-out 'HTTP=%{http_code}\n' \
  --proto '=https' --proto-redir '=https' --proxy '' --noproxy '*' \
  --connect-timeout 5 --max-time 15 --max-redirs 0 \
  --request GET "$RDM_OPS_ROUTE_URL"
RDM_OPS_ROUTE_STATUS=$?
printf 'CURL_EXIT=%s\n' "$RDM_OPS_ROUTE_STATUS"
unset RDM_OPS_ROUTE_URL RDM_OPS_ROUTE_STATUS
```

`--disable` must be the first curl option (ignores `.curlrc`). No auth, netrc,
client key or token option is supplied; proxy inheritance and redirect following
are disabled. The response body is discarded; only a three-digit status is
reported. No command is run automatically. 401 means TLS/HTTP reached an
authentication-required service, **not successful authentication**; 403 is
access denied; 2xx is unauthenticated API acceptance requiring investigation,
not proof of injected identity; 3xx is an unqualified route. Curl exit 60 means
certificate validation failed, 6 DNS failure, 7 connection failure, 28 timeout;
other nonzero exits remain unclassified failures. HTTP 000 alone does not prove
which stage failed. Inspect the shell exit status without printing error bodies.

This probe retrieves no credentials and cannot prove Java trust/classloading,
injected authentication, RBAC or complete ResourceKeys. A workstation test cannot
substitute for collector execution. The current build-9 adapter has no diagnostic
hook, so a real in-process authentication test cannot be performed under the
present no-install/no-reconfiguration/no-secret-retrieval boundaries. Do not
attach an agent, dump serialized configuration, copy node credentials or modify
the working adapter to circumvent them. No full live qualification is claimed.

## Validation, prerequisites and smallest E4.5

Offline deterministic tests inspect actual SDK bytecode without invoking
credentials or initializing a collector. They verify cache delegation, absence
of a native Suite API client, public injected carrier plus platform decryption
dependency, null default endpoint, trust/verifier limitations and public endpoint
classification. The supplied SDK is optional for fresh-clone tests: SDK-specific
cases explicitly skip when it or `javap` is unavailable; the API-spec test runs.

Run locally:

```bash
VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
  PYTHONPATH=src .venv/bin/python -m pytest \
  tests/managementpacks/test_rdm_e44_sdk_contract.py -q --tb=short
```

Actual offline results: **6 new contract tests passed; 62 existing runtime cases
passed; validate-sdk passed with 13 production sources**. Its existing
source/target-11 warning remains; the runtime runner separately compiles with
`--release 11`. Independent SDK review also reran 54 no-network discovery cases.
Complete factory suite: **2500 passed, 15 skipped, 131 deselected, 1 unchanged
failure**, with the authorized SDK path supplied. The failure remains
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`
(conservative unknown Git-ignore verdict versus expected no-repo verdict), not
changed by this documentation/test-only increment. No unrelated fix was made.

Changed/full content validation and skill parity passed (5 paired, 7 Codex-only).
Path-reference audit is clear with six standing warnings; both repository
whitespace checks passed. No PAK build/comparison is applicable: there is no new
artifact or install candidate. Preflight reported incomplete live credentials
and unrecorded clone bootstrap; neither is needed for these offline checks and
neither was retrieved, installed or bootstrapped.

Remaining empirical prerequisites: actual injected slot/decryption; resource-read
visibility and exact complete scoped key; configured FQDN reachability from each
placement; Operations-managed CA/trust representation, hostname enforcement and
delivery after collector movement. Historical other-adapter success is not erased,
but neither does it close these target-runtime questions.

**Recommend E4.5:** implement a dormant, bounded Java read-only Suite API provider
using a configured Operations FQDN, strict per-endpoint trust and **injected-only**
SDK credential access, with explicit authentication/linkage/RBAC/coverage failure
states. Use the established public API, preserve complete foreign keys and feed
only the in-memory graph. Add token cleanup, finite pagination and deterministic
401/403/duplicate/multi-vCenter/TLS tests. This implementation candidate need not
wait for a guessed localhost contract; actual runtime acceptance remains a later,
separately authorized diagnostic integration test. Do not activate it, migrate
the descriptor or publish topology as part of that smallest step.

Independent reviews:
[SDK](../../context/reviews/rdm-topology-e44-sdk-review.md) and
[security](../../context/reviews/rdm-topology-e44-security-review.md).
Both returned **APPROVE, zero outstanding findings**, for offline qualification
only. Exactly this qualification document, two independent reviews and the new
test file are authored by E4.4; previous worktree changes remain intact. No
staging/commits, adapter source/configuration changes or live execution occurred.
