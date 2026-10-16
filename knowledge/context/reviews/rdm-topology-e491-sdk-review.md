# E4.9.1 — Independent SDK lifecycle dependency review

## Verdict and scope

**Final verdict: APPROVE offline same-kind fixture lifecycle qualification for
the four synthetic scenarios below, zero outstanding findings.** The final
actual lifecycle rerun supersedes the original missing-JAR result and earlier
configuration-only coverage limit without changing their recorded history.
This is not live upgrade, deployment or collector-runtime approval.

**APPROVE the blocker assessment and read-only dependency-acquisition next
step; full fixture lifecycle qualification remains BLOCKED.** This is not
approval of a completed lifecycle run, installation, or an adapter change.
No source, descriptor, PAK, or runtime dependencies were changed by this
reviewer. No VMware connection, build, shim, download, or publication occurred.

Authorities: the SDK reviewer contract, Tier 2 SDK playbook section “Gaps —
name them, never hide them,” RULE-005/008/012/015, and the shared reviewer
doctrine. The defect registry contains no open entry whose `Affects:` token
targets this adapter. No closure or waiver is proposed.

## Independently verified evidence

- The supplied local SDK and seven descriptor libraries are the only JARs
  present under the supplied SDK directory. Every library passes its local
  `SHA256SUMS` manifest. Appliance origin remains operator-attested; this review
  did not connect to the appliance to attest it independently.
- `run-dispatcher-tests.sh --fixture-lifecycle`, using the genuine SDK and
  seven explicit library paths, passes **317 dispatcher assertions**, including
  actual SDK combined-descriptor loading and bare facade `describe()`. It then
  returns **exit 2** with
  `FIXTURE_LIFECYCLE code=BLOCKED_PLATFORM_DEPENDENCY
  class=com.vmware.vrops.secure.connection.ConnectionCategory`.
- The actual SDK `CustomTrustManager` constructor bytecode reads
  `ConnectionCategory.ADAPTER_TO_SOURCE`, calls
  `SSLOptions.getSSLOptions(ConnectionCategory)`, and calls `getStoreType()`.
  `CustomSSLSocketFactory` static initialization also uses both classes and
  `SSLOptions.getSupportedProtocols()` / `getSupportedCipherSuites()`.
  `jdeps --ignore-missing-deps -verbose:class` independently identifies both
  secure-connection classes as unresolved. These are concrete immediate
  requirements, not evidence of the provider JAR's filename or its own
  transitive dependencies.
- The dispatcher tests assert empty SDK resource-collection maps, absent
  embedded discovery payload, empty resource-status map, and empty explicit
  discovery results for diagnostic success, repeat, rejection, cancellation,
  and concurrent invalidation paths. Diagnostic dispatch never constructs
  the fixture base delegate. These deterministic results re-confirm zero
  resource/relationship/metric/property publication in the tested path;
  sanitized adapter-level status is still intentionally returned.

The inspected proprietary SDK/platform files are external local-only
artifacts, not reproducible from Git and not redistributed. Relevant bytecode
findings are summarized above rather than requiring a fresh clone to resolve
an ephemeral binary citation.

## Important lifecycle-test coverage limit

The existing `FixtureLifecycleProbe` constructs **the original fixture
adapter directly**, calls `configure(DispatcherTest.fixture())`, and calls
`discard()`. It does not instantiate the dispatcher, invoke fixture
`discover()` / `collect()`, inspect topology payloads, or exercise repeated
collections. The 317 dispatcher assertions use a synthetic delegate seam for
fixture dispatch and cannot substitute for that missing actual lifecycle
coverage. Even a future `CONFIGURE_PASS` from the present probe must not be
reported as completion of the requested full fixture lifecycle regressions.

## Dependency acquisition assessment and next step

An operator-run, read-only scan of JAR archives beneath
`/usr/lib/vmware-vcops`, testing exact ZIP entries for
`com/vmware/vrops/secure/connection/ConnectionCategory.class` and
`SSLOptions.class`, then printing matched archive paths and `sha256sum`, is
appropriate. Include all discovered secure-connection package providers to
avoid assuming the classes share one archive. Report inaccessible paths or
unreadable archives rather than treating an incomplete scan as absence.

**No exact platform JAR filename has been established locally.** Copy only
the matching authorized appliance files outside Git, retain source hashes,
verify destination hashes/classes, and inspect their dependency references
before execution. Never load all appliance libraries indiscriminately or use
replacement classes. Further missing classes, static-initialization settings,
or unavailable platform services remain possible until the genuine provider
and its dependencies are available.

After dependency qualification, extend a deterministic actual-dispatcher
lifecycle harness to cover valid legacy fixture configuration, discovery,
collection payload and additive topology invariants, repeat idempotence,
stop/discard, and both legacy/versioned fixtures. Any new test code requires
its normal author/reviewer boundary; production adapter changes are not
justified by this classpath gap. Stop on further missing dependencies without
shims. The live installation remains untouched.

**If shipped as-is:** deterministic diagnostic isolation and dispatcher
forwarding remain approved, but full fixture SDK lifecycle compatibility is
still unqualified. No completed lifecycle or same-kind upgrade safety claim
is warranted.

## Assessment follow-up

Independently reviewed the [operator dependency assessment](../../designs/managementpacks/vsphere-rdm-topology-e491-lifecycle-dependencies.md),
including its exact read-only Python archive scan. It performs no extraction,
class loading, credential reads or writes; traversal/archive errors abort, and
directory-symlink coverage is explicitly limited. Its three exact-class
searches do not claim exhaustive package or dependency coverage. **APPROVE.**

The supplied SDK's embedded Maven POM independently confirms
`com.vrops.certificate-validation:vrops-trustmanager:3.0-SNAPSHOT` and
`javax.xml.bind:jaxb-api:2.3.1`. The cleanroom classpath contract corroborates
the trustmanager JAR family, not the current appliance filename/hash.
`CertificateChecker.getCertificate(String)` bytecode independently confirms
`DatatypeConverter.parseHexBinary`; the assessment correctly treats JAXB as a
certificate-processing branch requirement, not the observed constructor
failure or a proven no-certificate fixture requirement. Further transitive
closure remains unknown. No additional completed qualification is claimed.

## Supplied trustmanager follow-up — independent rerun

The newly supplied external `vrops-trustmanager-3.0-SNAPSHOT.jar` is SHA-256
`64f915e64bbee1a69b75dcc8b4eef6038da3993c0b1c1cc212f2c047ac502e37`.
Its actual ZIP entries contain both `ConnectionCategory.class` and
`SSLOptions.class` under the expected package. All **eight** entries in the
updated operator-supplied `SHA256SUMS` manifest independently verify. This
establishes local agreement with the supplied source hash record, not a new
reviewer connection to or attestation of the appliance.

Re-running the unchanged shim-free runner with eight explicit external paths
produces **317 dispatcher assertions PASS**, followed by
`FIXTURE_LIFECYCLE code=CONFIGURE_PASS`, **exit 0**. No additional missing class
is observed on the actual fixture constructor/configure/discard path. The
original `ConnectionCategory` blocker is therefore resolved for that path.
Diagnostic zero-output regression assertions still pass.

The trustmanager embedded POM declares
`com.vmware.vcops:vcops-security:1.0-SNAPSHOT`; its `SSLOptions` bytecode calls
`com.vmware.vcops.security.Crypt.dec(String)` conditionally from
`readPasswordProperty` when encrypted platform SSL properties are used. That
is a verified branch reference, **not** a new failure of this successful
no-certificate fixture run or justification for fetching every POM dependency.
The previously identified SDK JAXB branch remains similarly unexercised.
No complete trustmanager/platform transitive closure is claimed.

**Remaining requirement:** the existing probe still does not execute actual
fixture discovery/collection through the dispatcher, compare publication
payloads, or test repeated actual SDK collections. Its success must be
reported as `CONFIGURE_PASS`, not full build-9 lifecycle regression completion.
No adapter/source/test changes, PAK build, substitutes, shims, live calls,
installation or publication occurred during this follow-up. Reviewer verdict:
**APPROVE the limited qualification evidence; full lifecycle remains NOT
QUALIFIED pending the real dispatcher lifecycle harness.**

## Completed actual fixture lifecycle review

Independently inspected the author's test-only `FixtureLifecycleProbe`
extension and reran the unchanged dispatcher runner against the actual SDK,
factory framework and **eight explicit genuine external libraries**. Results:

- `DispatcherTest: PASS 317 assertions`.
- `FIXTURE_LIFECYCLE code=PASS assertions=460 scenarios=4 routes=2`.
- Combined process **exit 0**, with no additional missing runtime class.

The four scenarios are legacy mapping-only and version-2 CanonicalLun fixtures,
each with absent/default and explicit `fixture` mode. Each executes both the
unchanged original fixture implementation and the public no-argument
dispatcher, using actual SDK configuration, monitoring-resource and attribute
policy carriers. Both routes execute configure, discover, initial collection,
repeated collection, same-config reconfigure, another collection, stop and
discard. The dispatcher additionally proves empty output after stop/discard.
Assertions verify scoped foreign VM key/identifier values/uniqueness, exact
mapping/LUN keys, additive parent/child edges without clear-first operations,
repeat stable topology and baseline/dispatcher output agreement.

The initial version-2 LUN collection must contain all **seven expected property
values**, including capacity `524288` bytes. Missing attribute-policy carriers
initially explained suppressed property output in the synthetic harness; the
test now supplies real `AttributeConfigs` / `AttributePolicyConfigs`, not a
production workaround. Actual SDK `AdapterCache.shouldCollect` bytecode
confirms policy-controller lookup. `AdapterCache.updatePropertyChanges` confirms
unchanged-property delta suppression with a `900000` ms resend window. Tests
therefore require full initial properties but permit either full matching or
empty unchanged property deltas on repeats/refresh while requiring complete
stable topology. They do not weaken identity or accept arbitrary property data.

No logging shim, synthetic fixture publishing delegate, reflective
constructor bypass, subclass replacement, production modification, platform
secret read or live call is used by this actual lifecycle extension. Standard
SDK-generated adapter health/timing output is not conflated with fixture
topology. Diagnostic zero-publication remains independently covered by the
317-assertion suite; sanitized adapter-level status remains intentional.

**Final disposition:** the named missing-class and actual offline positive
fixture lifecycle blockers are resolved for the tested no-certificate,
no-decryption paths. This does not execute every historical negative parser
matrix through the lifecycle or qualify live installation, UI serialization,
injected credentials, certificate-processing branches, Cloud Proxy networking,
or cross-collection persistence on an Operations appliance. No PAK was rebuilt.
If deployed as-is, runtime upgrade/platform behavior still requires separately
authorized controlled qualification. No open defect-registry item affects this
adapter; no registry closure or new defect is proposed.
