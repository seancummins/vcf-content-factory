# E4.4 — Independent runtime-contract security review

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT**, for offline
qualification and the prepared credential-free operator diagnostic only.
Injected authentication, current collector routing, RBAC coverage and managed
trust propagation remain unverified; production activation is not approved.

## Scope and independent evidence

Reviewed the [E4.4 qualification](../../designs/managementpacks/vsphere-rdm-topology-e44-runtime-contract-qualification.md)
and `tests/managementpacks/test_rdm_e44_sdk_contract.py`, actual authorized local
SDK signatures/bytecode, public/internal API specifications and existing stitch
utilities. No adapter, framework or probe source was edited by this reviewer.

Authority: RULE-001 source-of-truth, RULE-008 no-secrets, RULE-012 defect registry,
the Tier 2 skill's identity/classloader/gap-honesty contracts and
[reviewer doctrine](../authoring/guide_reviewer_doctrine.md). Historical
[injected-identity evidence](../api-surface/per-instance-suiteapi-credential-contract.md)
and the [later Cloud Proxy lesson](../../lessons/cross-mp-stitch-cp-identity-and-edge-mechanics.md)
are evidence of other adapters, not a current RDM runtime test.

Independent reruns:

| Check | Result |
|---|---|
| E4.4 actual-SDK contract tests | **6 passed**, exit 0 |
| Existing E4.3 runtime binding suite | **62 deterministic cases passed**, exit 0; Java 11 compilation |
| SDK artifact verification | SHA-256 `2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54` |

The proprietary SDK was inspected locally, not copied or redistributed; its
artifact is not reproducible from Git. Tests inspect synthetic carriers and
bytecode, not live credentials, platform decryption or VMware endpoints. No new
PAK exists, so build/package comparison is not applicable to this qualification.

## Security assessment

- **No lookup-free shortcut:** actual `AdapterBase` monitoring methods delegate
  to `AdapterCache`; they are not a global inventory query. Foreign relationship
  key processing cannot return the complete existing VMware ResourceKey.
  The scoped Suite API read remains necessary under the approved identity
  contract; MOID-only or name-based resolution is not substituted.
- **Injected identity is a candidate, not assumed authority:** the SDK-public
  carrier is distinct from the associated vCenter credential. Its password
  accessor invokes platform `com.vmware.vcops.security.Crypt`, absent from the
  compile SDK. Presence, runtime linkage, provisioning guarantees and effective
  resource visibility are explicitly unresolved. Missing injection fails closed;
  no administrator, maintenance/automation-file or VMware-credential fallback.
- **Public versus internal is correctly separated:** the actual public spec
  includes token acquire/release and resource-list/detail operations. A
  `/suite-api` base URL alone does not imply an unsupported endpoint. No guessed
  identifier query parameter, injected auth source or role name is introduced.
- **Routing is explicit:** the configured certificate-valid Operations FQDN
  must be reachable from every intended collector role. Historical Cloud Proxy
  loopback tunneling is acknowledged, not promoted to a guaranteed strict-TLS
  route. Node certificates secure the platform tunnel, not Java user-token
  authorization; adapter access to node keys is neither needed nor proposed.
- **Trust remains strict:** actual SDK trust-store/certificate-map APIs are
  useful integration surfaces, not proof of cluster delivery or unconditional
  name validation. Independently inspected `CustomHostnameVerifier` can honor
  accepted-certificate flags disabling hostname checks. The proposal explicitly
  refuses those overrides and the framework's current trust-all stitching path,
  preserves endpoint-specific trust and identifies CA/ID/leaf representation and
  failover as empirical gaps. No node-local synchronization or global SSL change.
- **Least privilege is bounded honestly:** resource reads and independently
  confirmed object/group visibility are required. Authentication success is not
  authorization; complete pagination is not proof of complete RBAC visibility.
  No permission mutation, credential-read or topology-write privilege is proposed.
- **Manual diagnostic is appropriately limited:** `curl --disable` is first,
  proxy inheritance and redirect following are off, HTTPS chain/name checks stay
  on, no credentials/netrc/client keys are requested and response bodies are
  discarded. Only HTTP status and operator-inspected exit classification are
  intended outputs. The operator must supply the exact non-secret URL and must
  not use tracing, verbose output or insecure TLS. No execution is automatic.
  A 401 proves only reachability to an authentication-required HTTP service, not
  correct injected authentication. This diagnostic cannot qualify Java trust,
  complete ResourceKeys or in-process credential decryption.
- **Boundary is not circumvented:** current build 9 has no diagnostic hook.
  The document correctly declines configuration dumps, JVM attachment, secret
  extraction or installation/reconfiguration to manufacture runtime evidence.
  A later dormant, injected-only provider is a testable implementation candidate,
  not authorization to activate or publish topology.

Registry check: `knowledge/context/defects.md` inspected; **no open defect affects
this RDM adapter**. No registry closure or surviving new defect is proposed.

**If shipped as-is:** installed build-9 fixture behavior remains unchanged. The
operator has an explicitly unexecuted route-only diagnostic; automatic identity
resolution and topology publication remain inactive. Runtime acceptance still
requires a separately authorized, appropriately instrumented experiment.
