# E4.6 independent SDK implementation review

## Verdict

**APPROVE — zero BLOCKING, WARNING or NIT findings outstanding**, for dormant
offline preparation only. Not an install-ready artifact or live runtime
qualification. Reviewed the independent RDM adapter repository; no adapter
source was edited by this reviewer.

If shipped as currently registered, the existing fixture adapter remains the
entrypoint. The new diagnostic is unregistered. A separately packaged diagnostic
still requires descriptor/platform dependency and lifecycle qualification before
any authorized collector execution.

## Independently verified implementation

- Inspected actual legacy SDK 2.2 bytecode: `AdapterBase.collectBase()` calls
  `prepareCollectResult`, `addSystemProperties`, `finalizeCollectResult` and
  `collectAdapterInstanceMetrics`; `collect()` can append certificate events.
  Consequently, empty `onCollect()` would not satisfy this increment. The new
  `ReadOnlyDiagnosticAdapter` instead implements public `AdapterInterface3`
  directly. Actual SDK result tests verify empty resource maps, absent discovery
  payload, empty resource-status maps and empty discovery results. Only static
  sanitized adapter status is returned. No resource/relationship builder,
  stitching writer or publication method is invoked.
- `DiagnosticRuntime` composes the actual Operations provider and SOAP decoder.
  Both explicit flags must authorize execution; default/bad configuration cannot
  access credentials or network. Configuration generations, association/mutation
  checks, cancellation, bounded execution and consumed grants prevent stale
  worker output or another attempt on the same object. Configuration-only test
  callback neither arms nor proves live collection.
- SOAP direct-MOR scope is limited to the expected vCenter UUID, selected VM,
  current host and host/changeVersion fence. Missing, zero, multiple, unstable,
  unresolved or conflicting mappings fail qualification. PASS requires exactly
  one complete target mapping and qualified LUN; complete-but-empty graphs fail.
  Current-host exact backing UUID join and existing LU-associated NAA rules are
  retained. Operations resolution preserves the complete original scoped key,
  identifier order, values, actual uniqueness flags and empty nonunique strings.
- Injected Operations identity and associated vCenter credentials remain distinct
  SDK carriers. No fallback account, credential file, implicit VMware integration
  reuse or fake platform decryption class is introduced. Token release failure
  is a separate cleanup stage and cannot replace a primary collection failure.
- Initial independent localhost integration exposed ten global proxy callbacks:
  default TLS sockets consulted the JVM SOCKS selector. This was corrected in
  both Operations and diagnostic SOAP transports using explicit
  `Socket(Proxy.NO_PROXY)` before TLS wrapping, not suppressed in tests. Final
  tests prove zero global proxy/authenticator/cookie callbacks. Private JVM-root
  trust contexts reject a permissive replacement global default SSLContext;
  independent SAN checks still reject wrong names before HTTP credentials.
- Candidate descriptor/localization remain outside active build inputs; fixture
  descriptor, entrypoint and version are not migrated. No dependency download or
  proprietary SDK bundling is introduced. Java 11 compilation and `jdeps` show
  diagnostic dependencies on JDK/platform SDK/existing local classes only.

Authority: `.claude/skills/vcfops-sdk-adapter/SKILL.md` sections “ARIA_OPS
stitching identity,” “Classloader isolation,” “Unreadable is NOT compliant,” and
“Gaps”; RULE-001, RULE-005, RULE-008, RULE-016; lessons
`cross-mp-foreign-key-uniqueness-flags.md` and
`controller-describe-bare-instantiation.md`.

## Independent execution evidence

Executed against the supplied legitimate local SDK, without VMware access:

| Check | Actual result |
|---|---|
| Final `run-diagnostic-tests.sh`, synthetic localhost TLS explicitly authorized | **243 diagnostic/composition assertions + 22 framing assertions + 19 TLS/integration assertions passed**, exit 0 |
| Existing `run-ops-provider-tests.sh`, synthetic localhost only | **345 assertions passed**, exit 0 |
| Existing `run-runtime-tests.sh` | **62 deterministic cases passed**, exit 0 |
| Existing `run-discovery-tests.sh --no-network-tests` | **54 deterministic cases passed**, exit 0 |
| Existing `run-tests.sh` | **8 topology/descriptor, 42 invalid-runtime, 34 invalid-LUN cases**, positive roundtrip/idempotence/convergence matrices passed |
| `validate-sdk` | **21 production sources passed**, exit 0 |
| Adapter whitespace check | Passed |

Standalone diagnostic compilation uses `--release 11`; validator retains its
existing source/target-11 warning, plus deprecated SDK callback warnings.
No PAK build or comparison was run: no new installation artifact is requested or
claimed by E4.6. RULE-005 remains applicable to a future installation candidate.

Final reviewed coordinator SHA-256:
`a91e80c83f5a28ac14aa3d762a3b8e8a27ada2a2c5f1f38e3e2e16be3d95f02c`;
direct SDK wrapper:
`52763de76205f4849b8cf35e4bd49e3cc83b5caa75d287463fa6207ed2ac58d0`;
isolated SOAP transport:
`1d5d5fe87f619e51087c02056996fa06d329012dd54f5a75a97632b20bd72290`.

## Explicit qualification limits and next step

Candidate `AdapterDescribe.make` cannot fully load in this SDK-only JVM because
platform Commons Configuration linkage is absent; its failure is sanitized and
documented. No fake dependency or passing loader claim was used. Bare describe
does not read injected state. Full descriptor loading/localization, distinct-kind
packaging, UI save/test/collect acceptance and actual platform classloading remain
prerequisites, not waived installation defects.

One-shot authorization is per object, not durable across restart or collector
movement; operator instructions require stopping the separate diagnostic instance
and resetting flags before movement/restart. The SDK exposes one managed CA list:
using it for both independent endpoint policies requires explicitly approved trust
coverage. ID-only/leaf-only delivery remains unsupported and fails closed.
Actual decryption, injected principal/RBAC visibility, collector/Cloud Proxy
routes, managed CA delivery, gateway framing and JDK/FIPS compatibility are not
proven by offline tests. The operator procedure distinguishes those gaps and
prohibits altering the working POC instance.

Recommend next: qualify the distinct diagnostic descriptor/package offline with
legitimately available platform dependencies, then seek separate authorization
for one tightly scoped read-only collector experiment. No topology publication
or automatic production activation follows from this approval.

Registry check: inspected `knowledge/context/defects.md`; no entry names this
RDM adapter as affected, and no local override registry is present. No closures
or new surviving findings are proposed. Review stayed read-only except this
report; no live calls, secrets/private evidence, installations, commits or pushes.
