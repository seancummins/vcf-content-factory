# E4.4 — Independent SDK runtime-contract qualification review

**APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT.** This approves the offline
qualification and proposed dormant E4.5 boundary, not production authentication,
collector activation, deployment or topology publication.

## Independent scope and evidence

Reviewed the [qualification record](../../designs/managementpacks/vsphere-rdm-topology-e44-runtime-contract-qualification.md)
and `tests/managementpacks/test_rdm_e44_sdk_contract.py`. Independently inspected
the actual operator-supplied legacy SDK using `javap -c -p` and its JAR index,
current factory stitching sources, the public/internal API specifications and
the earlier credential/routing evidence. No adapter/framework source was changed
by this increment or this reviewer; no credential accessor on real configuration,
private inventory, network request, PAK build or installation was used.

The proprietary SDK is local-only and not reproducible from Git; its relevant
signatures and bytecode findings are summarized here rather than redistributed.
Independently verified SDK SHA-256:
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.

Authority: SDK reviewer contract and shared doctrine; RULE-001, RULE-005,
RULE-007, RULE-008, RULE-012 and RULE-015; SDK skill sections on scoped foreign
identity, classloader isolation and gap honesty. Historical evidence is retained
but not promoted to a target-build or vendor-support guarantee.

## Verified contracts and limits

- `AdapterBase.getAllMonitoringResources()` delegates to
  `AdapterCache.getMonitoringResources()`. `getMonitoringResource(ResourceKey)`
  ultimately consults `monitoringResourcesByKey` through `Map.get`.
  `AdapterCache.update(AdapterConfig)` consumes supplied resource configuration,
  not a global VMware inventory service. No global lookup bypass is established.
- `ResourceKey` models identity and `Relationships.addRelationships(ResourceKey,
  Collection<ResourceKey>)` declares an outgoing additive relationship. Neither
  returns an existing foreign object's complete ResourceKey. Knowing two
  uniqueness-bearing fields is not permission to infer the remainder of the
  approved complete-key contract.
- The SDK JAR has no `SuiteAPIClient`. `AdapterBase.getConnectionURL(AdapterConfig)`
  returns null by default; `AdapterConfig.getHostCollectorID()` returns an integer,
  not an endpoint. A vendor framework's client and historical localhost tunnel
  do not establish a stable native service-discovery contract.
- `AdapterConfig.getAdapterCredentials()` returns the distinct
  `AdapterCredentialConfig` carrier. Its `getPassword()` calls platform
  `com.vmware.vcops.security.Crypt.getDefaultCrypt().decrypt(...)`; that class is
  absent from this compile SDK. This proves a runtime dependency, not failure on
  an actual collector. The older plaintext/injected-operator-account descriptions
  are appropriately superseded, and historical injected-principal read success
  on Cloud Proxies is not erased.
- `ResourceConfig.getTrustedCertificates()` and `getTrustedCertificateIds()`,
  plus `AdapterBase.getAdapterTrustStore()`/`getCertificateMap()`, are real SDK
  carriers. `CustomHostnameVerifier` consults hostname-enforcement flags, so
  adopting it indiscriminately would not preserve E4.3's strict trust policy.
  Actual CA representation, delivery and failover remain unqualified.
- The public specification contains the exact token acquire/release and resource
  GET operations used by the design. They do not require a fabricated internal
  endpoint or unsupported-header exemption. The optional authentication-source
  flow is correctly identified as needing target-runtime qualification.
- Existing framework utilities are evidence, not directly reusable production
  contracts here: platform connections install trust-all and an all-true hostname
  verifier; the generic resolver uses single-identifier last-wins indexing and
  failure-to-empty behavior. Token-release representation also needs verification
  against authenticated current-session cleanup before reuse. No unrelated
  framework repair is hidden in this qualification increment.

## Safety and recommendation

The configured certificate-valid Operations FQDN is the conservative route from
each collector/Cloud Proxy. It does not require guessing localhost, node keys,
administrator inheritance or another integration's credentials. Resource-read
permission and independently confirmed object visibility are necessary; exact
platform role IDs are not invented. Complete pagination alone cannot prove RBAC
coverage or distinguish globally absent inventory from caller-invisible objects.

The prepared operator-only curl diagnostic is credential-free, strict-TLS,
no-redirect and body-discarding. It can establish route/TLS outcomes only, not
Java trust, injected authentication, ResourceKeys or RBAC. It is not executed
and is not a deployed dependency. The existing build-9 adapter has no in-process
diagnostic hook; full live qualification is therefore honestly unavailable
within the current no-install/no-reconfiguration/no-credential-retrieval scope.

The proposed E4.5 is justified: an inert native Java, configured-FQDN,
injected-only, strict-TLS, bounded read provider with sanitized failures and
complete scoped keys. Missing injection/linkage/visibility must fail closed;
there is no automatic maintenance-account or service-account fallback. Runtime
acceptance and certificate propagation still require separately authorized
qualification, not a claim inferred from successful SDK compilation.

## Independent validation

| Check | Independently observed result |
|---|---|
| New actual-SDK/API contract tests | **6 passed**, exit 0 |
| Runtime binding runner | **62 deterministic cases passed**, exit 0; no production API/decryption exercised |
| Discovery runner `--no-network-tests` | **54 deterministic cases passed**, exit 0 |
| `validate-sdk` | **PASS**, 13 production sources; existing source-11 system-modules warning |
| Factory and adapter `git diff --check` | PASS |

No PAK build/comparison is needed for this documentation/test-only increment;
no installation candidate is claimed. Existing runtime tests are not substituted
for target-runtime authentication or TLS-delivery evidence.

Registry check: `knowledge/context/defects.md` has **no open defect affecting the
RDM topology POC**; no local override was present. No closure or new defect
registration is proposed. Known other-adapter/framework limitations are
documented reuse boundaries, not waived RDM implementation defects.

**If shipped as-is:** build-9 fixture behavior is unchanged; the record enables
the next offline provider increment but cannot authenticate or publish topology.
