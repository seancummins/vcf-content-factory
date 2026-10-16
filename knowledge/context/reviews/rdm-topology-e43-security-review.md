# E4.3 — Independent runtime configuration and identity-boundary security review

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT**, for the dormant,
offline-tested boundary only. Production Operations authentication, routing,
configuration activation and topology publication are not approved or proven.

## Scope and authority

Read-only review of the independent adapter's new `RuntimeDiscoveryBinding` and
`ScopedOperationsResolver`, synthetic `RuntimeBindingTest`, runtime test script
and `docs/runtime-configuration-boundary.md`. No adapter source was edited by
this reviewer. Previous worktree changes are not attributed to E4.3.

Authority: [E4.1 architecture](../../designs/managementpacks/vsphere-rdm-topology-e41-automatic-discovery.md),
[E4.2 foundation](../../designs/managementpacks/vsphere-rdm-topology-e42-discovery-foundation.md),
[injected credential contract](../api-surface/per-instance-suiteapi-credential-contract.md),
[reviewer doctrine](../authoring/guide_reviewer_doctrine.md), RULE-001, RULE-008,
and the Tier 2 skill's identity, classloader, lifecycle and gap-honesty contracts.

## Independent verification

| Check | Observed result |
|---|---|
| New runtime suite with authorized local SDK | **62 deterministic cases passed**, exit 0; actual SDK configuration carriers, synthetic credential reader and generated CA only |
| Java API target and dependencies | Test script compiles production boundary with `javac --release 11`; `jdeps` resolves JDK, existing discovery classes and platform SDK only |
| `validate-sdk` | **PASS**, 13 production source files; existing source/target-11 compiler warning remains, separate strict-release compilation passed |
| Existing Java fixture/topology suites | **PASS**: 8 topology/descriptor tests, 42 invalid-runtime cases, 34 invalid-LUN cases and associated positive matrices |
| Existing discovery suite without sockets | **54 cases passed**, exit 0 |
| Existing discovery suite with synthetic loopback HTTPS | **55 cases passed**, exit 0, after explicit local-socket sandbox approval; no VMware endpoint contacted |
| Independent adapter whitespace check | Passed |
| Existing build-9 PAK SHA-256 | Unchanged: `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb` |

No new PAK was built or compared: there is no new install candidate. The existing
PAK hash is a local-only artifact record, not a reproducible public artifact
citation. No proprietary dependency was copied or redistributed.

## Security assessment

- **Associated credential only:** binding requires the owned adapter-instance
  ResourceConfig and exact proposed `rdm_vcenter_readonly` credential kind, with
  one username field and one password-marked password field. It never reads
  VMware integration credentials, injected Operations credentials, environment
  secrets or maintenance/automation files. Missing or duplicate fields reject.
- **Verified SDK access:** independently inspected the supplied SDK APIs and
  bytecode. `ResourceConfig.getResourceCredential()` and
  `CredentialConfig.getCredenialFields()` are real interfaces.
  `CredentialFieldConfig.getValue()` for password fields invokes platform
  `com.vmware.vcops.security.Crypt`, as does the injected Operations password
  accessor. Missing linkage/decryption is sanitized and fails closed; actual
  platform decryption was not exercised or replaced with guessed production
  crypto.
- **Configuration generation:** endpoint, scope, trust mode, certificate
  material/flags and certificate IDs are stamped and rechecked before transport
  construction and secret acquisition. Credential association/field metadata are
  separately rechecked. Mutation regressions reject changed endpoint, trust,
  scope and credential association. A future lifecycle coordinator must still
  serialize configuration replacement against acquisition/use; this inert class
  is not a race-safe deployed lifecycle implementation.
- **Secret lifetime/redaction:** leases are one-shot and erase their owned
  password array on success/failure/close. Tests independently inspect erasure
  and sanitized callback failure behavior, including suppressed exceptions.
  XML-incompatible usernames/passwords reject without trimming valid passwords.
  Diagnostics use static categories and no raw causes, identifiers or secrets.
  Immutable SDK Strings and SOAP serialization buffers cannot be securely wiped;
  documentation accurately states that limitation.
- **Trust and hostname:** strict HTTPS `/sdk` only, no userinfo/query/fragment or
  insecure mode. Explicit enterprise material is bounded, parsed as complete
  unique valid CA certificates, checked for CA/key usage and rejects false
  hostname/date flags. Opaque certificate IDs reject instead of guessing a
  node-local lookup. Explicit CA delivery is tested; inherited transport's actual
  chain/name rejection and approved-CA acceptance were independently rerun.
  These are compositional checks, not an integrated platform-managed trust or
  failover proof.
- **Scoped VM boundary:** immutable complete ordered keys retain actual flags
  and supported empty nonunique values. Expected vCenter UUID, generation,
  completeness, routing/authentication attestations and bounded monotonic age
  are checked. Future/stale/overflowing/throwing clocks and ambiguous candidates
  fail closed. Provider failures are sanitized. Attestations are explicitly
  offline inputs, not a substitute for real authentication.
- **No guessed Operations client:** `production()` refuses construction.
  There is no token/HTTP client, permissive localhost route or fallback account.
  No production connection, resource creation, relationship publication or
  deletion path was introduced. Registered adapter source/descriptor do not
  reference the new runtime classes; build-9 fixture operation remains isolated.

Review-time concerns about mutable configuration association, clock failure
redaction and XML-invalid usernames were corrected by the author and retested;
none remains outstanding. The reviewer did not implement the fixes.

## Remaining prerequisite and next increment

Before enabling automatic collection, establish actual platform Crypt linkage,
injected per-instance identity availability, least-privilege inventory-read RBAC,
strict Suite API TLS and collector/Cloud Proxy endpoint routing. Verify whether
Operations supplies CA material or opaque IDs/accepted leaves, and establish a
supported cluster-managed trust delivery contract. Existing permissive framework
stitch transports and file-backed ambient fallbacks are not substitutes.

The smallest E4.4 is supported-contract qualification and a strictly read-only,
bounded Operations provider plus lifecycle coordination, initially producing an
in-memory graph only. Any deployed read-only experiment needs separate approval.
Publication, descriptor migration, shared-LUN ownership, stale-edge cleanup and
production activation remain separate work.

Registry check: `knowledge/context/defects.md` inspected; **no open defect affects
this RDM adapter**. No registry closure or new surviving defect is proposed.

**If shipped as-is:** the installed fixture-driven behavior remains unchanged;
automatic discovery cannot be enabled through the registered adapter, and the
new Operations resolver explicitly remains offline-only.
