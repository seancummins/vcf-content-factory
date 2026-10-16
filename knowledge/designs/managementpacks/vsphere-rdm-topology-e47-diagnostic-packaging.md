# E4.7 — Same-kind diagnostic packaging readiness

## Decision

**NO-GO for a diagnostic PAK/install candidate in this increment.** Prefer the
existing `vcfcf_rdm_topology_poc` kind. The SDK does not require a second kind,
but the current diagnostic cannot simply be packaged under the existing kind.
A same-kind, publication-free route needs an explicitly implemented and tested
lifecycle dispatcher and compatible descriptor. Actual full descriptor loading
is also blocked by missing local platform dependencies. No runtime, registered
metadata, build number or release workflow is changed; no PAK is generated.

This supersedes the **separate-kind recommendation**, not the implementation or
test evidence, in [E4.6](vsphere-rdm-topology-e46-read-only-diagnostic.md).
Its distinct-kind descriptor remains an unregistered historical candidate, not
an authorized new management pack. No second adapter kind is implemented here.

## Alternatives and upgrade safety

| Alternative | Isolation and upgrade effect | Credentials/networking | Migration, maintenance and removal | Decision |
|---|---|---|---|---|
| Flag inside existing `onCollect()` | Fails zero-output requirement: SDK base adds output outside callback | Can use SDK configuration, but not publication-free | Small apparent change hides base-class side effects | Reject |
| Same-kind direct-interface dispatcher, unchanged fixture delegate | Diagnostic route bypasses base; package upgrade still replaces code/descriptor for **all** instances | Exercises real associated vCenter and injected Operations credentials | Optional configuration migration and explicit mode tests needed; reuses existing diagnostic runtime | Preferred next implementation |
| Same-kind diagnostic-only replacement | Removes existing fixture implementation from every upgraded instance | Real SDK credentials possible | Disrupts working collection; difficult restoration | Reject |
| Distinct diagnostic kind | Best code/configuration isolation from build 9 | Real SDK credentials possible | Parallel identity and temporary lifecycle/cleanup overhead | Last resort; not authorized |

Actual supplied SDK `AdapterBase` declares final lifecycle methods, including
`collect`, `configure`, `discover` and `test`. `collectBase()` appends system
properties and adapter metrics; certificate-event paths also exist. Therefore
an empty `onCollect()` is insufficient. The public `AdapterInterface3` permits
a thin dispatcher in principle. This is an implementation option, **not proof
of controller/collector acceptance or a nondisruptive upgrade**.

The smallest inspectable implementation would change `adapter.yaml`'s
`entry_class` to a direct-interface facade and leave `RdmTopologyPocAdapter`
unchanged as the fixture delegate. Keeping the public entry-class name instead
would require extracting/renaming its existing implementation; it does not
eliminate lifecycle migration risk. Prefer unchanged fixture code over claiming
that an unchanged class name makes an upgrade safe.

## Proposed implementation contract — not yet implemented

- Preserve the existing adapter kind, `RdmMapping` and `CanonicalLun`
  declarations, identifier keys, fixture parsers and additive relationships.
- An optional, ordinary `execution_mode` selects `fixture` or
  `read_only_diagnostic`. Missing mode retains build-9 fixture behavior; an
  unknown, duplicate, mixed or malformed setting fails closed. Never select
  diagnostic because fixture parsing failed, or fall back to fixture after a
  diagnostic error.
- Route diagnostic callbacks directly to the existing bounded diagnostic
  runtime. Do not construct, configure, discover or collect through the fixture
  delegate/SDK base on that route. Return empty SDK publication payloads on
  success, failure, disabled, repeated, concurrent and cancelled paths. Only
  sanitized adapter status/counts may leave the graph boundary.
  Read-only source enumeration (bounded Suite API candidate pages and SOAP
  inventory reads) is necessary and permitted; enumeration into SDK discovery
  results or platform inventory publication is not.
- Latch mode for the configured object and reject in-place mode switches;
  serialize lifecycle retirement so an old delegate cannot publish concurrently.
  A new diagnostic instance, not modification of the working fixture instance,
  is the operator model. Object-local latching is not a durable cluster guard.
- The union descriptor needs `fixture_json` optional in metadata but still
  required by fixture runtime. Diagnostic fields and credential association
  must be optional in metadata but required conditionally by diagnostic code.
  Preserve `isCredentialRequired="false"`; do not add dummy credentials.
  Test absent, explicit blank, default-inserted and populated optional settings
  using real SDK carriers. UI serialization is still an empirical prerequisite.
- Adapt the E4.6 hardcoded diagnostic-kind binding checks explicitly to this
  approved owner/mode; do not relabel SDK objects, copy credentials or broadly
  accept arbitrary adapter kinds. Reuse the coordinator/transports, not duplicate
  their discovery, authentication, timeout or redaction machinery.

Necessary regression evidence: old build-6 fixture and version-2 fixture payload
equivalence; configuration-only validation; complete lifecycle dispatch;
unknown/mixed configuration rejection; no delegate construction or publication
in diagnostic mode; failed/disabled/concurrent/cancelled mode output; stable
resource identities; preserved credential-free fixture mode; actual descriptor
load and package entrypoint/localization parity. Removal later means retiring
diagnostic instances and the mode branch, not uninstalling the shared pack.

## Configuration, credentials and strict trust

Reuse [E4.6's target and endpoint settings](vsphere-rdm-topology-e46-read-only-diagnostic.md):
explicit HTTPS vCenter `/sdk`, Operations FQDN `/suite-api`, independent trust
mode choices, `single_vm_current_host`, exact vCenter UUID/VM MOID/disk key and
two initially false execution flags. No fixture JSON in diagnostic mode.

The vCenter username/password belongs in an Operations-managed associated
`rdm_vcenter_readonly` credential. The Suite API principal comes only from
`AdapterConfig.getAdapterCredentials()`; it is not an operator-entered ordinary
field, another integration's account or a node-local maintenance credential.
Real injection, secret decryption, token acceptance and RBAC remain untested in
this adapter. Fail closed if absent; do not substitute an identity. Minimum
rights are selected VM/current-host inventory reads and caller-visible VMware
VM ResourceKey reads, not administrator/resource-write/relationship-write rights.
No exact privilege IDs are invented.

**The present descriptor does not establish an operator-complete enterprise-CA
setup.** E4.6 accepts actual SDK `CertificateConfig` CA PEM material, rejects
opaque IDs, leaf-only pins and disable flags, and returns `NOT_SUPPORTED` from
certificate checking. A `trust_mode` field alone does not deliver CA bytes.
If both endpoints already chain to approved JVM roots on every intended
collector, strict JVM trust is a possible bounded initial lab route; verify that
fact rather than changing collector-local files. Otherwise qualify supported
Operations-managed CA material delivery first. A separate persisted CA-PEM
property is a possible future contract, not implemented or assumed to fit the
UI. Test size limits and cluster persistence before selecting it. No node-local
CA files, TLS-insecure defaults, trust-all fallback or automatic downloads.

## Offline artifact and loader evidence

The supplied proprietary SDK is local-only, not reproducible from Git and not
redistributed. Its SHA-256 is
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
The clean SDK-only `AdapterDescribe.make(InputStream)` attempt first fails on
`org.apache.logging.log4j.LogManager`. The E4.6 test classpath supplied test-only
logging linkage and reached a downstream Commons Configuration dependency;
neither result establishes full loading with real platform dependencies. No
missing library is installed, stubbed or bundled to turn that into a passing
result.

Two adapter-local test/readiness files were added, not production code:
`scripts/check-sdk-descriptor-load.sh` and
`tests/com/vcfcf/adapters/rdmtopologypoc/diagnostic/DescriptorLoadingProbe.java`.
The standalone child JVM excludes the preexisting test logging shims, invokes
the actual supplied SDK, and reports sanitized status. An optional explicit
`VCFCF_DESCRIPTOR_CLASSPATH` may point only to already legitimately available
local platform dependencies; it does not fetch or redistribute them. Both the
active descriptor and E4.6 candidate return **exit 2 / BLOCKED_PLATFORM_DEPENDENCY**
with the Log4j class above. Malformed input/arguments fail; no positive full
descriptor load is claimed.
The standalone child disables external DTD/schema/stylesheet access before the
SDK's own second parse as well as hardening its preflight parser; inability to
establish restrictions blocks execution. Synthetic DOCTYPE/external-entity input
is rejected without forwarding parser or SDK diagnostic output.

Operator-executable **offline** retry after supplying the legitimate dependencies:

```bash
VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
  bash content/sdk-adapters/rdm-topology-poc/scripts/check-sdk-descriptor-load.sh \
  content/sdk-adapters/rdm-topology-poc/describe.xml vcfcf_rdm_topology_poc
```

Set `VCFCF_DESCRIPTOR_CLASSPATH` privately to the authorized local dependency
classpath if supplied. Do not include test shims or bundle these platform jars
in a PAK. Even a future PASS here is descriptor-loader evidence, not successful
installation, credential injection or controller lifecycle proof.

Existing artifact inspected, **not** an E4.7 diagnostic artifact:
`vcfcf_sdk_rdm_topology_poc.0.0.0.9.pak`, SHA-256
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
In-memory ZIP inspection confirms outer/inner integrity, existing
`RdmTopologyPocAdapter` registration under the existing kind, three resource
kinds (instance/mapping/LUN), only `fixture_json` instance configuration and no
credential-kind declaration. Its two JARs are the entry JAR and factory base;
no SDK-named JAR or bundled `com/integrien` classes were found. It cannot execute
the diagnostic. No diagnostic checksum or comparison gate result is invented.

## Conditional operator procedure — do not execute now

There is **no E4.7 PAK to install**. The following becomes executable only after
the dispatcher, compatible descriptor, loader and package checks above pass and
the operator separately authorizes a controlled upgrade and read-only attempt.

1. Retain build-9 artifact/checksum and private Operations-managed fixture
   configuration. Record existing solution version, fixture-instance identity,
   resource counts, topology, collector placement and health. Do not export
   passwords or raw keys to transcripts. Stop if a recoverable baseline is
   unavailable.
2. Schedule the shared-kind upgrade: stop existing fixture collection for its
   duration with explicit authorization. Install the verified newer development
   PAK through the supported UI. Do not uninstall build 9 first. Confirm the
   actual installed version, registered kind and descriptor, then verify the
   unchanged fixture instance resumes with its old identities and topology.
   A same-kind upgrade cannot be represented as zero disruption.
3. Create a **new instance of the same kind**, explicitly selecting diagnostic
   mode, associating only its read-only vCenter credential and strict supported
   trust. Set both execution flags false. Confirm Validate Connection is
   configuration-only, not discovery/authentication proof. Stop if UI saving,
   optional credential handling, CA delivery or injection cannot be verified.
4. On separate one-attempt authorization, set both flags true and allow one
   collection. Record timestamp, placement and sanitized status. Expected
   evidence: `PASS / GRAPH / READ_ONLY_GRAPH_QUALIFIED`, counts **1/1/1**.
   Collecting/Data Receiving/Validate Connection alone is insufficient.
5. Stop the diagnostic immediately and reset both flags false before any
   restart/failover. Repeated collection on the same object must not make new
   API requests. Confirm no new mappings/LUNs, relationship changes, properties,
   metrics or events from the diagnostic; a platform-created adapter instance
   itself is a separately authorized configuration object, not graph output.

Stop on unexpected publication/inventory changes, fixture regression, scope
expansion, ambiguous/partial identities, timeout, TLS/auth/RBAC failure, changed
collector placement or unavailable sanitized evidence. Never relax TLS or VM/LU
matching, widen privileges automatically, or retry by modifying the working
fixture instance. Cloud Proxy reachability is an empirical prerequisite, not
inferred from generic endpoint failures.

## Rollback/removal boundary

First stop/disarm only the new diagnostic instance. If an unexpected shared-kind
regression occurs, stop affected collection and preserve sanitized evidence;
do not delete mappings or VMware objects to repair it. Retain the existing
fixture configuration and exact build-9 artifact. A separately authorized,
platform-tested roll-forward or downgrade/recovery procedure is required; a
same-kind downgrade cannot be assumed safe merely because the PAK is available.
Verify solution version, fixture collection, resource counts and topology after
recovery, accounting for asynchronous reconciliation.

Do **not uninstall the shared management pack** or delete kind-wide credentials
as diagnostic cleanup. That could remove the working POC and cascade credential
deletion ([documented lesson](../../lessons/pak-uninstall-cascades-credentials.md)).
After a successful test, separately authorized cleanup may remove only the exact
diagnostic instance and its dedicated unshared credential, after verifying
references. Do not delete shared/injected credentials or any VM/mapping/LUN
resource. Remove temporary mode code only after no instances depend on it.

## Validation and independent disposition

| Check | E4.7 result |
|---|---|
| Actual SDK full descriptor load, active and historical candidate, no logging/platform shims | Both BLOCKED, exit 2, missing real `org.apache.logging.log4j.LogManager` |
| New readiness probe negative checks | Expected sanitized failure for invalid arguments, unavailable SDK, malformed XML and DOCTYPE/external-entity input; successful-load/wrong-kind post-load branches unverified |
| Existing diagnostic | PASS, 243 coordinator + 22 SOAP wire assertions; independent security rerun also passed 19 synthetic localhost TLS/integration assertions |
| Existing provider / runtime / discovery | PASS, 281 provider assertions, 62 runtime cases, 54 discovery cases without sockets |
| Existing fixture/topology | PASS, 8 topology/descriptor tests, 42 invalid runtime cases, 34 invalid LUN cases plus positive matrices |
| SDK validation | PASS, 21 production sources; existing source/target-11 and deprecation warnings remain; standalone test compiles with `--release 11` |
| Complete factory tests | 2,500 passed, 15 skipped, 131 deselected, 293 warnings; one unchanged failure |
| Changed/full content validation, skill parity, path audit | PASS; 5 paired/7 Codex-only skills, six standing path warnings and no dead references |

The unchanged factory failure is
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
expected no-repository prose differs from the conservative unknown Git-ignore
verdict. It was not weakened or modified. Old topology tests' limited real SDK
key loaders use test-only logging linkage; their PASS is not substituted for
the full shim-free loader result above.

Hash comparison with the E4.6 source/test/script and active artifact snapshots
shows no pre-existing file changed: only the two new test/readiness files were
added to the adapter. Factory changes are this design and independent review
records. No active descriptor, production source, adapter metadata, fixture,
PAK, Git index, `.claude/`, immutable reference material or release workflow was
changed by E4.7. Both independent repository boundaries are retained; no commit,
push, live query, installation or reconfiguration occurred.

Independent [SDK review](../../context/reviews/rdm-topology-e47-sdk-review.md)
and [security review](../../context/reviews/rdm-topology-e47-security-review.md)
approve this bounded design/readiness disposition, with zero outstanding
findings in the proposal. This is not implementation, package or installation
approval. Packaging is **NO-GO**; no structural comparison result is claimed for a
nonexistent candidate. Recommended next step is approval of the same-kind
dispatcher implementation contract above and provision of the legitimately
available platform descriptor-loader dependencies for offline verification,
with strict managed-trust qualification retained as a lab prerequisite.
