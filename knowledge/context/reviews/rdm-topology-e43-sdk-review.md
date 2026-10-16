# E4.3 — Independent SDK runtime-boundary review

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT outstanding.**
Approval is limited to dormant SDK configuration/credential binding and the
explicit offline identity-provider boundary. It is **not** approval of deployed
Operations authentication, automatic collection, publication or installation.

## Scope and authority

Read-only independent review of the managed RDM adapter's new
`runtime/RuntimeDiscoveryBinding.java`, `runtime/ScopedOperationsResolver.java`,
`RuntimeBindingTest`, `scripts/run-runtime-tests.sh` and
`docs/runtime-configuration-boundary.md`. The independent adapter repository
boundary is unchanged; older worktree changes were not attributed to E4.3.
No source was repaired by this reviewer and no private evidence or credentials
were read.

Authority: the SDK-adapter reviewer contract and reviewer doctrine, RULE-001,
RULE-005, RULE-007, RULE-008 and RULE-012; the SDK skill's foreign-identity,
classloader, resource-hygiene and gap-honesty contracts; the
[E4.1 architecture](../../designs/managementpacks/vsphere-rdm-topology-e41-automatic-discovery.md),
[E4.2 foundation](../../designs/managementpacks/vsphere-rdm-topology-e42-discovery-foundation.md)
and [credential carrier evidence](../api-surface/per-instance-suiteapi-credential-contract.md).

The operator-supplied proprietary SDK is local-only and cannot be redistributed.
Its public signatures and bytecode were independently inspected with `javap`;
the relevant findings are summarized below without publishing its binary.

## Verified SDK and implementation contracts

- Actual SDK `ResourceConfig` exposes `getResourceCredential()`,
  `getResourceIdentifiers()`, `getTrustedCertificates()` and opaque certificate
  IDs. The binder accepts only the owned adapter-instance kind, exactly the
  proposed nonunique endpoint/trust/scope settings, and its explicitly associated
  `rdm_vcenter_readonly` credential. It does not traverse VMware integrations,
  read ambient files or use environment credentials.
- `CredentialConfig.getCredenialFields()` is the real misspelled accessor.
  Actual `CredentialFieldConfig.getValue()` decrypts when `isPassword=true`
  through `com.vmware.vcops.security.Crypt`. This implementation is absent from
  the supplied compile SDK. Missing linkage and credential access failures
  become standalone sanitized authentication failures, never a plaintext or
  alternative-account fallback. Synthetic reader tests do **not** prove actual
  collector decryption.
- Original resource/credential association and field metadata are rechecked
  before leasing credentials; endpoint/trust/configuration stamps are checked
  before leases and transport construction. Review initially identified missing
  owned-kind enforcement and mutable password-flag/association bypasses; these
  were corrected and regression-tested before approval. A later configuration
  replacement must retire this binding under serialized SDK lifecycle control;
  arbitrary concurrent mutation of SDK objects is not claimed safe.
- Passwords are not configuration identifiers. Leases erase their char arrays on
  close/discovery exit, including failures; immutable SDK Strings and SOAP
  buffers cannot be securely erased. Exceptions and object summaries contain
  fixed codes, no raw account, endpoint, fixture, ResourceKey or chained cause.
- Enterprise trust uses bounded in-memory SDK certificate material, rejects
  unresolved IDs, malformed/non-CA/duplicate anchors and explicit hostname/date
  disable flags. JDK trust mode refuses conflicting supplied material. This is
  connected to the unchanged E4.2 strict HTTPS/name-verification transport; no
  trust-all or global SSL modification is introduced. Runtime certificate
  representation, ID/material association and cluster propagation remain
  unverified rather than guessed.
- The Operations bridge is expressly `offline(...)`; `production()` always
  fails closed. Complete authenticated/routed snapshot attestations are synthetic
  provider inputs, **not** runtime authentication. Expected vCenter, generation,
  maximum monotonic age and overflow are checked. Scoped resolution preserves
  complete immutable ordered keys, real uniqueness flags and empty nonunique
  strings through E4.2. Missing, cross-vCenter, duplicate, expired, incomplete or
  ambiguous candidates cannot become a successful foreign VM identity.
- No Suite API HTTP/token implementation, VMware credential harvesting,
  collector-local file, process, download, publication, deletion or relationship
  replacement is added. The registered fixture entrypoint does not reference
  either new class. The build-9 descriptor remains credential-free and continues
  to use the original fixture contract, not the proposed runtime settings.

## Independent reruns

| Check | Result |
|---|---|
| `VCFCF_SDK_JAR=<authorized-local-SDK> bash content/sdk-adapters/rdm-topology-poc/scripts/run-runtime-tests.sh` | **62 deterministic cases passed**, exit 0 |
| E4.2 discovery runner `--no-network-tests` | **54 cases passed**, exit 0 |
| Existing actual-SDK POC runner | **8 topology/descriptor**, **42 invalid runtime**, **34 invalid LUN** cases and existing positive/convergence/idempotence matrices passed |
| `validate-sdk` | **PASS**, 13 production Java sources compiled |
| Runtime runner `javac --release 11 -proc:none` and `jdeps` | PASS; JDK and supplied platform SDK only, no added third-party dependency |
| Adapter `git diff --check` | PASS |

The existing builder source/target-11 system-modules warning remains; the
runtime runner separately performs strict Java-11 API compilation. Test-only
deprecated SDK setter warnings are not runtime dependencies. The ephemeral CA
and keytool used by tests are not deployed requirements. No SDK logging shim,
test credential reader or proprietary SDK is newly packaged.

These are independent executions, not repeated author claims. This reviewer
opened no socket. Existing E4.2 real loopback TLS/name/deadline tests are a
separate orchestrator/security regression, not evidence of live Operations or
enterprise certificate delivery. The binder's CA parsing and existing
transport's TLS checks are composition evidence; an integrated real collector
certificate/authentication path remains a deployment prerequisite.

No new PAK was built or compared: these classes are dormant, no installed
configuration changed, and a new install candidate is not claimed. The existing
build-9 PAK is not evidence of deployed E4.3 behavior.

## Registry, limitations and handoff

Registry check: `knowledge/context/defects.md` contains **no open defect affecting
the RDM topology POC**. No closure or new defect registration is proposed; no
implementation finding remains outstanding.

Actual injected-identity decryption/linkage, least-privilege inventory RBAC,
strict Suite API TLS/authentication/pagination, collector/Cloud Proxy endpoint
routing, SDK certificate delivery and accepted-trust failover are unresolved
production contracts. Public credential carriers alone do not establish them.
No maintenance-file fallback or permissive existing stitch client is adopted.

Recommend E4.4 first establish the missing platform contracts, then implement a
narrow strictly read-only authenticated provider and serialized lifecycle
binding. Keep resource publication, descriptor migration, shared-LUN ownership
and stale-edge reconciliation disabled until their separately approved work.

**If shipped as-is:** the existing fixture-driven adapter behaves unchanged;
the new foundation cannot activate production Operations resolution or automatic
topology publication.
