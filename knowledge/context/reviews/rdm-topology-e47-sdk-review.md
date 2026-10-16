# E4.7 independent SDK packaging-readiness review

## Verdict

**APPROVE the bounded design/readiness disposition and test-only loader tooling;
NO-GO for a diagnostic PAK or installation.** No diagnostic artifact was built,
and this is not an installation approval. Zero outstanding defects in the
reviewed disposition; the explicitly unresolved implementation and platform
prerequisites below remain gates, not waived findings.

Reviewed [the E4.7 design](../../designs/managementpacks/vsphere-rdm-topology-e47-diagnostic-packaging.md),
the current Java lifecycle/configuration boundaries, actual SDK signatures and
bytecode, loader tooling, and existing build-9 packaging. No adapter source or
registered metadata was edited by this reviewer.

## Independent technical conclusions

- Existing-kind execution is feasible **in principle**, not disproven by the
  SDK. The supplied SDK exposes `AdapterInterface3` publicly. A thin direct
  interface dispatcher could delegate unchanged fixture behavior while routing
  diagnostic callbacks around the SDK base. This has not been implemented or
  proven safe on upgrade.
- A flag inside the current `onCollect()` is insufficient: actual SDK
  `AdapterBase` finalizes `collect`, `configure`, `discover` and `test`;
  `collectBase()` adds system properties and adapter-instance metrics outside
  the callback. The active `RdmTopologyPocAdapter` also explicitly enumerates
  resources and emits properties/additive relationships. Diagnostic mode must
  never reach that delegate, including failure/cancellation/reconfiguration.
- A same-kind PAK upgrades the shared implementation/descriptor for **all**
  instances. A new diagnostic instance alone does not isolate installation
  effects. Preserve existing fixture keys, kinds, identities and relationships;
  absent mode must preserve build-9 behavior, unknown/mixed modes must fail
  closed, and mode changes must retire safely. Optional descriptor fields and
  credentials need real SDK-carrier regression tests and later UI evidence.
- Current E4.6 runtime/binders explicitly require the dormant diagnostic kind.
  Repackaging or relabeling them under the existing kind would fail validation,
  not provide a supported same-kind execution path. Do not relax all owner
  checks or reconstruct credential carriers to bypass this.
- The associated vCenter credential and injected Operations instance credential
  are separate SDK carriers. Configuration-only test success does not verify
  decryption, authentication, RBAC or collector/Cloud Proxy networking.
- Enterprise trust is not operator-complete: the dormant callback returns
  `NOT_SUPPORTED`, and runtime accepts CA PEM material, not opaque IDs or leaf
  pins. Endpoint/trust-mode strings do not supply that material. Qualify managed
  CA delivery or verify both endpoints already chain to approved JVM roots;
  no node-local file workaround or trust-all default is justified.
- The proposed removal boundary is sound: stop/disarm the exact diagnostic
  instance; never uninstall the shared pack to remove temporary functionality.
  Same-kind rollback/downgrade is not proven by possessing the old PAK.

Authority: SDK skill sections “Classloader isolation,” “Gaps” and “Build / verify
loop”; RULE-001, RULE-005, RULE-008 and RULE-016; lifecycle contract
`knowledge/context/cleanroom-spec/spec/01-adapter-lifecycle.md`; lessons
`controller-describe-bare-instantiation.md` and
`pak-uninstall-cascades-credentials.md`. The supplied proprietary SDK is
local-only, not redistributed/reproducible from Git; relevant observed behavior
is summarized here rather than requiring access to that binary.

## Independently rerun evidence

| Offline check | Result |
|---|---|
| `run-diagnostic-tests.sh --no-network-tests` | 243 diagnostic/composition + 22 framing assertions passed |
| `run-runtime-tests.sh` | 62 cases passed |
| `run-discovery-tests.sh --no-network-tests` | 54 cases passed |
| `run-ops-provider-tests.sh --no-network-tests` | 281 assertions passed |
| Existing `run-tests.sh` | 8 topology/descriptor, 42 invalid-runtime, 34 invalid-LUN cases and positive matrices passed |
| `validate-sdk` | 21 production sources compiled; exit 0, existing source/target-11 and deprecated-callback warnings |
| New loader shell syntax; invalid-argument guard | Passed; invalid arguments exit 1 with static diagnostic |
| Actual full SDK loader, active and dormant descriptors separately | Both exit **2**, `BLOCKED_PLATFORM_DEPENDENCY`, first missing class `org.apache.logging.log4j.LogManager` |
| Adapter whitespace check | Passed |

The actual-loader harness excludes `tests/org` no-op logging shims and does not
download, discover or fabricate dependencies. Its SDK-only result is **blocked**,
not a malformed-descriptor verdict or successful load. Earlier Commons
Configuration linkage failures occurred downstream when test logging shims were
available; those are not the first failure of this clean classpath. Existing
partial descriptor/key tests with explicit test logging linkage do not establish
full `AdapterDescribe.make()` acceptance.

Rechecked the final loader hardening: before either parser, its standalone child
JVM sets and verifies empty external DTD/schema/stylesheet access policies;
failure is a static blocked-security result. Its first parser also rejects
DOCTYPE/entities. These process properties are not changed in a collector JVM.
Independently reran the final active-descriptor probe: same exit 2/missing Log4j,
not a passing loader claim.

Tooling reviewed: shell SHA-256
`a2d8a6ed478bf411b28468df2fa86176c0aa262e485e8d639bb91f36f58a3491`;
Java loader probe
`3a00409ce614d47254e6667ee91829bef1f99a7c5c8bb0529df9051456f49dac`.
These live in the independent adapter repository, not factory-owned source.

## Existing artifact inspection — not a diagnostic artifact

Independently inspected build 9 in memory without extraction or modification:

- Artifact: `vcfcf_sdk_rdm_topology_poc.0.0.0.9.pak`.
- SHA-256: `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
- Outer and nested ZIP integrity checks passed.
- Two JARs: adapter entry JAR and `vcfcf-adapter-base.jar`; neither contains
  proprietary `com/integrien/` SDK classes.
- Registration remains `RdmTopologyPocAdapter` / `vcfcf_rdm_topology_poc`.
- Descriptor retains instance, `RdmMapping`, `CanonicalLun`; no credential-kind
  declarations. This remains fixture-driven, not a packaged diagnostic.

No new build or structural comparison was run: no diagnostic PAK exists. Prior
artifact comparisons cannot qualify a future changed descriptor/entrypoint.

## Required before a collector candidate

Implement/review the same-kind dispatcher and backward-compatible union
descriptor; demonstrate zero diagnostic output across lifecycle paths; obtain
legitimate dependency closure for actual descriptor loading; establish managed
trust setup; build/inspect/compare the resulting candidate. Then separately
authorize shared-kind upgrade, new diagnostic-instance configuration and one
read-only attempt. Real injection/RBAC/routing/UI/lifecycle acceptance remain
empirical qualifications, not inferred from offline success.

Registry check: inspected `knowledge/context/defects.md` affected scopes; no open
entry names this RDM adapter. No registry closures or surviving new defect
registrations are proposed. If shipped as-is, build 9 remains the active fixture
entrypoint; no runnable existing-kind diagnostic is available. No live calls,
installation, private inventory/credential reads, builds, commits or pushes were
performed by this reviewer.
