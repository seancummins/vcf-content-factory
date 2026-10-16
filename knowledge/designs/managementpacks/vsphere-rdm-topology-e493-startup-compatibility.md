# E4.9.3 — Cold-start compatibility follow-up, build 13

## Result and live boundary

The continued offline investigation reproduced and corrected a cold-start
compatibility regression that build 12 did not address. A genuine SDK schema
synchronization operation can expand a legacy fixture-only key to twelve fields,
including exact empty execution_mode. Packaged build 9 configures and collects
that carrier; builds 11 and 12 reject it before fixture construction.
Build 13 accepts only the complete, unambiguous fixture form.

This is a proven supported-carrier regression and a plausible explanation for
the supplied initial-monitoring failure. **It is not proof of account 15903's
actual callback shape or restored live collection.** No live service, account,
credential, trust store, collector or inventory was contacted or changed.
No commit, push, tag, merge, publication or dependency download occurred.
Build 12 and all earlier nested PAKs remain preserved.

## Evidence matrix

| Candidate explanation | Offline finding | Limit |
|---|---|---|
| Expanded schema supplies exact empty optional fields | Proven: actual ResourceKindIdentifiers synchronization produces 12 nonunique identifiers from a 1-field legacy key, preserves fixture data and adds 11 empty values | Template registration is required |
| Empty-mode cold-start regression | Proven with actual packaged entry/framework JARs: build 9 collects, 11/12 reject, 13 collects | Actual collector input remains unavailable |
| Collector expands persisted account before initial configure | Possible, unobserved | Supplied SDK/libraries contain no identified persisted-account converter |
| Java serialization converts absent to empty/null | Ruled out for exercised genuine carriers | Round trips preserve absent, empty and null distinctly |
| Descriptor parsing itself builds persisted configuration | Ruled out in supplied SDK path | All 12 fields are metadata-only, optional, no defaults, identType 2 |
| Initial SDK fixture configure performs expansion | Ruled out on exercised path | Original configure preserves 1 field and absent mode; no verifier call in that chain |
| SDK cache can normalize keys | Proven public caller: after expanded incoming key registration, getMonitoringResource(legacyKey) expands lookup to 12 fields and empty mode | Does not prove collector preconfigure ordering |
| Empty credential is equivalent to absence | Unsupported | SDK constructors default null; an explicitly empty credential object remains nonnull through serialization |
| Constructor ID mismatch or another strict branch | Still possible, not observed | Preserve E4.9.2 identity guard and fixed failure reasons |
| Instance-less partial update causes cold first callback failure | Not established | Cold original also fails without cached full state; build 12 fixes only post-full updates |
| Unknown, whitespace, duplicate or unique-marked modes deserve fallback | Unsupported | Strict rejection remains |

The actual SDK configure chain registers templates from incoming ResourceConfig
keys; it does not seed them directly from AdapterDescribe. The verified
synchronization consumers are AdapterCache.getMonitoringResource(ResourceKey)
and getStoppedResource(ResourceKey), plus key-based metric/cache callers.
The test deliberately derives a template from the real descriptor and calls
the genuine public SDK API. Production dispatch never calls the normalizer:
doing so could erase malformed or ambiguous input.

The supplied account log remains only the timestamp
2026-10-16T02:57:22.346Z and RDM_DISPATCHER INVALID_CONFIGURATION. Targeted
authorized project records and log-name inventory revealed no additional
sanitized callback capture. Private fixture files were not treated as evidence
of the platform's configure carrier.

## Minimal correction and preserved contracts

Exact empty mode may enter the existing fixture validation path. It must have
one complete valid fixture, known/nonunique/nonduplicate identifiers, no
populated diagnostic settings and no target credential object or UUID reference.
Populated diagnostic boolean strings, including false, are not empty.
Raw null, whitespace, unknown/case variants, mixed settings and malformed
fixtures remain rejected. Only exact read_only_diagnostic selects diagnostic.
There is no fallback after a diagnostic failure and no input rewriting.

The UUID-reference restriction and raw snapshot component apply only to the
new exact-empty form. Existing absent-mode and exact-fixture UUID-only carrier
acceptance remains unchanged. Credential objects remain rejected on all fixture
forms; SDK-injected Operations identity remains separate. Mutation of the new
form's credential reference retires the route.

The public no-argument and exact public (String, Integer) constructors remain.
One adapter kind, descriptor, fixture parser, original fixture implementation,
resource keys, properties and additive relationships remain unchanged.
Diagnostic resources, relationships, metrics, properties and events remain
zero. Empty actual SDK resource-result maps exclude per-resource events:
CollectResult.addEvent creates/adds a ResourceCollectResult. Embedded and
explicit discovery plus resource-status payloads are also checked empty.

Build 12's independently qualified partial-update fix is retained: only after
a successful full fixture configure can matching instance-less updates be
forwarded unchanged, with before/after source guards. No completed collection
is required, but an initial partial callback cannot bootstrap a route.

Ten authored nested-adapter paths differ across E4.9.3: dispatcher; four test
classes (DispatcherTest, E493DispatcherTest, new E493ColdStartTest,
FixtureLifecycleProbe); run-dispatcher-tests.sh; adapter.yaml; CHANGELOG.md;
docs/same-kind-diagnostic.md; docs/configuration-compatibility-e493.md.
The runner passes the descriptor to the lifecycle probe and confines
ADAPTER_HOME/ALIVE_BASE to disposable /tmp. The ordinary build regenerates
its six existing generated documentation surfaces. No framework implementation
or immutable reference content was edited.

## Actual tests and independent review

| Check | Result |
|---|---|
| Preserved packaged builds 9/11/12 cold matrix | 86 scenarios, both constructors: 516 cold attempts, plus 12 separate partial sequences |
| Independent four-package 9/11/12/13 matrix | 704 configure attempts including partial sequences; 10 intended changes vs 12, 166 other outcomes unchanged |
| Cold acceptance, out of 172 per package | 9: 144; 11: 66; 12: 66; 13: 76 |
| Partial/rejection matrix | PASS, 325 assertions |
| New cold-start matrix | PASS, 392 assertions |
| Prior dispatcher/ABI/isolation matrix | PASS, 343 assertions; obsolete empty-rejection expectations replaced |
| Actual shim-free SDK fixture lifecycle | PASS, 3486 assertions, six scenarios across four routes |
| Independent diagnostic coordinator/SOAP framing | PASS, 243 + 22, genuine SDK/libraries and no network |
| SDK validation and build | PASS, 22 production sources and exact compiled constructor ABI |
| Guarded seven stock content validators | All return 0; seven Tier 2 projects valid |
| Pinned structural comparison | PASS, 0 BLOCKING / 4 WARNING / 21 INFO |
| Full factory suite, refined native guard | 2649 passed, 15 skipped, 1 deselected, 3 failed, 0 errors, 333 warnings |
| Two repository-writing tests in byte-identical isolated snapshot | 2 passed unchanged |

The six real lifecycle scenarios are mapping-only and version-2 LUN fixtures,
each absent/default, exact fixture or actual SDK-expanded empty mode, through
original/dispatcher and controller/collector constructors. Checks cover cold
configuration, discovery, repeated collection, refresh, both partial setters,
monitoring stop/remove/restore, property policies, raw source preservation,
UUID mutation retirement, exact identities, additive edges and stop/discard.

Five genuine SDK ERROR-level messages report missing appliance root file
appenders in the offline harness. Attempts are confined to disposable /tmp;
no logger shim, missing class or failed lifecycle assertion is hidden. This
does not qualify appliance logging configuration. Existing builder compiler
module-path/deprecation warnings remain. External SDK/platform libraries all
match their supplied manifest and stay outside Git and the PAK.

The three raw full-suite failures are not represented as a green run:

- The common_setup not-a-Git-repo message assertion is the exact preexisting
  E4.9.2 failure; neither its test nor setup_credentials implementation changed.
- Two rdm_lab_probe tests attempt real repository scratch writes. Native
  read-only restrictions denied them. Unchanged, byte-identical test/script
  copies passed both tests in an isolated /tmp snapshot.
- The single deselected wheel test is blocked, not attempted: the current
  interpreter lacks setuptools, setuptools_scm and wheel. The required
  setuptools>=64/setuptools-scm>=8 build backend cannot be supplied without
  an unapproved install/download. Disabling build isolation does not solve it.

The 15 normal skips and all exact commands are retained in the independent
full-suite report. Default slow-marker exclusions were cleared. Initial audit
false positives were fixed only in /tmp before the refined run. Landlock
restricts repository/source writes and real private reads; inherited seccomp
blocks native child networking, while Python guards also protect credential
loading. Only fixture credential files in the dedicated scratch root are
permitted. No real .env existence or content was inspected. Stock validation
would attempt dotenv discovery/loading; the guarded equivalent disables that
path without altering content validation. No green broader-suite claim is made.

SDK and security independently reproduced the new matrices and approved the
final source, documents and packaged build 13 with zero code findings.
Framework review approves unchanged E4.9.2 guards, records the complete broader
suite results and identifies no E4.9.3 framework regression. The SDK reviewer
independently rebuilt the candidate and verified all 126 recursively unpacked
file contents are identical. Only 107 archive timestamp entries differ;
whole-PAK reproducibility is not claimed.

Saved independent evidence:

- [SDK contract investigation](../../context/sdk-cold-configuration-contract-e493.md).
- [Final SDK review](../../context/reviews/rdm-topology-e493-startup-sdk-review.md).
- [Final security review](../../context/reviews/rdm-topology-e493-startup-security-review.md).
- [Full factory-suite review, exact commands and guard evidence](../../context/reviews/framework/rdm-e493-full-suite.md).

These follow-up records supplement the preserved
[build-12 report](vsphere-rdm-topology-e493-configuration-compatibility.md).

## Local candidate and packaging

Development PAK:
content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.13.pak

SHA-256:
96d6293f3858bb13e625f52188b515d72e73c9f87ae46debd2ba7e50b30c68ae

The adjacent `.pak.sha256` sidecar records this exact filename and digest.

Frozen dispatcher source:
8abe662cbc06423c359b19cffffaa29fdc072e010f9e1bbe2642074ba5596260

Reference Synology 1.0.0.30 SHA-256:
beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1

Four unchanged structural warnings remain: credential fields 2/5, instance
identifiers 12/3, traversal kinds 0/1 and empty/populated traversal container.
The 21 INFO findings are metadata/display/icon/JAR and data-kind differences.
No finding was suppressed or reclassified.

This is a local development preview, not a release. The uncommitted independent
adapter and proprietary local-only SDK inputs are required; factory Git alone
cannot reproduce it. Archive timestamps remain an existing whole-file
reproducibility limitation; the independent payload comparison is recorded by
the SDK reviewer, and the operator must use the exact root-candidate hash.

## Remaining precise evidence/action boundary

Relevant offline carrier, descriptor, serialization, actual cache/configure
paths and packaged cross-build cases have now been exercised. The remaining
live-attribution action is pending evidence/authorization, not denied or
uncertain. The supplied files lack the collector's persisted-account converter
and failing configure carrier. No more lenient null/credential/identity policy
can be justified by guessing those facts.

If already captured, supply only the failing callback's fixed reason and
sanitized shape: full instance present/absent; whether a prior full configure
succeeded on that Java object; identifier names, uniqueness and
absent/null/empty/populated categories; target credential object/UUID and
injected/custom/extended presence; constructor/config ID and UUID/key match
booleans; installed version, collector placement and callback timestamp.
Exclude values, fixture contents, endpoint/UUID/credential data and exception
payloads. A matching collector converter method supplied offline is another
possible evidence source; no filename or behavior is guessed here.

Otherwise obtain explicit approval for a controlled supported build-13
development-lab upgrade/retry. Verify the checksum; retain builds 9–12, the
private recoverable account configuration, identities, placement and fresh
baseline. Retain account 15903 and its exact fixture/mode/credential settings.
Do not uninstall/recreate, clear/re-save settings, restart collectors, delete
inventory or weaken TLS/trust.

After the supported update, verify actual installed version and fresh repeated
collection timestamps, exact resource keys/counts and additive relationships.
Retained ubuntu2404 to mapping 2001 inventory alone proves no new collection.
Stop the retry on failure or unexpected publication and capture only the fixed
reason and sanitized shape. Recovery changes and diagnostic execution require
separate authorization. This report authorizes no live action.

