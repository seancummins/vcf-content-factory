# E4.1 — Native automatic RDM topology discovery

**Architecture proposal; no implementation or live action.** Recommend a native
legacy Java SDK adapter, installed as a self-contained PAK and running on supported
Operations collector nodes. Customers configure a vCenter endpoint, read-only
credential and certificate trust, then enable collection. No manual topology JSON,
Python runtime, containers, registry, sidecar, external discovery service, array
API or installation-time download is part of this architecture.

## Evidence and decision boundary

The [automatic-discovery API map](../../context/api-maps/vsphere-rdm-automatic-discovery.md)
records exact API fields, methods and source provenance. Retain
[E3.3 identity/ownership](vsphere-rdm-topology-e33-canonical-lun.md),
[E3.4.1 qualification limits](vsphere-rdm-topology-e341-integer-compatibility.md),
[E3.5 semantics](vsphere-rdm-topology-e35-canonical-lun-poc.md) and the
[E3.5.1 descriptor correction](vsphere-rdm-topology-e351-descriptor-compatibility.md).

- E2 proved the additive foreign VM parent relationship in the development lab;
  precise VMware collection ordering, failover and cleanup remain unverified.
- The operator now confirms build 9 installed successfully, but still uses the
  original mapping-only fixture: the v2 fixture exceeds the UI's approximately
  1,900-character field limit. This is not live proof of the complete LUN chain.
- E3.4.1 qualifies one saved host observation with independent storage-side NAA
  agreement. Cross-host, cross-vCenter and temporal equivalence are not proven.
- Native-LUN discovery found no exact match in inspected caller-visible inventory;
  it did not prove Operations categorically lacks LUN objects.

Tier 2 remains explicitly authorized: typed SOAP inventory, cross-request joins,
strict composite foreign identity and owned topology require Java. No new MPB
design, repository or release infrastructure is needed. Existing independent
repository `content/sdk-adapters/rdm-topology-poc` remains the implementation home;
its owner remains `seancummins`, not the role prompt's historical organization.

## Native API and dependency decision

Prefer supported **vim25 SOAP at HTTPS `/sdk`**. It exposes all required typed
VM/RDM and host SCSI data. Implement a bounded JDK HTTPS/XML client against that
contract, adapting working native Java request/TLS patterns rather than assuming
generated bindings are safe on the collector classpath.

`content/sdk-adapters/compliance/src/com/vcfcf/adapters/compliance/VSphereClient.java`
documents a deployed `javax.xml.ws`/Jakarta provider collision under parent-first
loading. Generated Java SOAP/vim25 bindings are an alternative only after a
specific distribution passes Java/classloader, transitive dependency, license
and disconnected-packaging qualification. They are not the initial dependency
choice. Raw SOAP still uses the supported vim25 service, not an invented API.
Inspected compliance source checkpoint: `e92baab438ddb8058c74c4e0e39333fb3431cd6b`;
managed sources are retrieved through `knowledge/context/managed_paks.md`.

Use JDK HTTPS and hardened namespace-aware XML facilities: prohibit DTDs, external
entities, XInclude and external schema resolution; bound document bytes, depth,
arrays and text. Encode requests safely; validate SOAP faults and typed values.
Unsupported hardening features must fail closed; parse direct typed properties,
not first matching descendants. Do not copy compliance's permissive parser setup.
The working compliance client's older per-property `RetrieveProperties` walk is
not the proposed bulk algorithm. VIM JSON parity is deferred; generic vAPI REST
has no repository proof of equivalent RDM/durable-descriptor coverage.

The PAK contains adapter/framework code and every necessary non-platform runtime
dependency plus required license notices. Do not bundle proprietary Operations
SDK/platform libraries. No unresolved Maven/provider fetch occurs at installation
or collection. Before implementation, verify supported collector JDKs, bytecode
target, XML providers, FIPS behavior and framework linkage on the actual matrix.
The local compile SDK is not proof of every deployed runtime's compatibility.
Retain Java-11-compatible production compilation unless the supported matrix
requires otherwise; manifest build-JDK versions do not establish that matrix.
Managed compliance/RDM checkouts expose no license/NOTICE file: establish code
reuse rights and attribution before copying; the factory license does not by
itself establish rights to independently versioned adapter source.

## Configuration, authentication and TLS

Proposed ordinary adapter-instance fields: vCenter FQDN/port, optional bounded
inventory scope, collection budget and advanced Operations API endpoint when
placement requires it. These are new pack configuration, not vendor identifiers.
Reject URL userinfo, arbitrary schemes and redirects carrying credentials.

Declare a required vCenter username/password `CredentialKind`, bind it on the
adapter-instance ResourceKind and set `isCredentialRequired="true"` for automatic
mode. Use SDK `ResourceConfig.getResourceCredential()` and
`CredentialConfig.getCredenialFields()` through framework `getCredentialField`;
password fields must be declared sensitive/password-type using verified examples.
No existing VMware integration credential is read, copied or implicitly reused:
no inspected supported sharing mechanism establishes that permission.

Operations lookup uses the distinct collector-injected per-instance identity:
`getAdapterConfig().getAdapterCredentials()`, documented in the
[SDK credential contract](../../context/api-surface/per-instance-suiteapi-credential-contract.md).
Require that injection; do not fall back to maintenance credential files or ask
customers for a second Operations password. SDK
`AdapterCredentialConfig.getPassword()` internally calls platform
`com.vmware.vcops.security.Crypt`; qualify that runtime linkage and effective
inventory-read RBAC before adoption.

Existing `SuiteApiStitchClient`/`openPlatformConnection` transport is not accepted
unchanged: its permissive TLS paths conflict with this design. Build a dedicated
strict read-only client or an independently reviewed framework extension. Permit
resource GETs and token acquire/release only; token release is authentication
cleanup, not inventory mutation. Cache tokens in memory, retry authentication
once on expiry, and ensure cleanup failures never mask primary results.

Both vCenter and Operations connections require trusted chains **and explicit
configured-host certificate-name verification**; never default trust-all/TOFU
acceptance. The native compliance `VCenterCertificates.java` build-94 pattern
addresses providers lacking peer-host metadata; chain validation alone is not
sufficient. Support enterprise PKI and explicit administrator certificate review
using Operations-managed trust/configuration, not collector-local files. Prove
accepted trust survives collector relocation/failover; do not claim it yet.
Use framework `certificateCheckUrls(ResourceConfig)` through
`getConnectionURLs(AdapterConfig)` to expose the normal Operations Validate
Connection certificate-review workflow; acceptance is explicit, never automatic.
Cloud Proxy routing to the Operations API FQDN and injected-identity RBAC remain
empirical prerequisites. A configured reachable cluster endpoint may be needed.

Read-only privileges must cover the configured vCenter scope and every requested
property; validate the exact role in a separately approved test. Missing privilege
is a collection failure, not successful empty inventory. No storage credentials.

## Discovery and cycle architecture

Use one immutable, bounded cycle snapshot; no HTTP lookup per disk:

1. `RetrieveServiceContent`, authenticate, retain `about.instanceUuid/version`;
   establish a session, view and PropertyCollector state with bounded lifecycle.
2. Enumerate caller-visible VMs in the configured scope using a container view;
   bulk `RetrievePropertiesEx` and every `ContinueRetrievePropertiesEx` page.
   Fetch MOR, `config.instanceUuid`, `config.changeVersion`, `runtime.host` and
   `config.hardware.device`; select typed RDM virtual disks/backing only.
3. Fetch `config.storageDevice.scsiLun` once per relevant current host. Join exact
   backing `lunUuid` to exactly one current-host `ScsiLun.uuid`. Other-host matches
   are visibility evidence, never proof of accessibility on the VM's host.
4. Decode `durableName`/`alternateName`, canonical name, descriptor metadata and
   available descriptions/capacity using the API map's typed field contract.
   Recheck VM host/changeVersion before publication; bounded retry after vMotion
   or reconfiguration, otherwise quarantine that VM's unstable associations.
5. Read all paged Operations `GET /api/resources` results for
   `VMWARE::VirtualMachine`, index complete keys by the scoped tuple below, and
   resolve each VM in memory. Do not reuse a one-field/last-match resolver.
6. Validate all associations for each independently publishable resource group,
   deduplicate owned keys and edges, then emit using unchanged additive semantics.
   Close abandoned pagination/views and log out on discard/session retirement.

Required object/property omissions, `missingSet`, faults, duplicate objects or
properties, unrecognized backing types and inconsistent pagination are explicit
unknown/error states. Never turn them into zero RDMs or evidence of removal.
Failure of a host/VM does not suppress unrelated validated VM groups, but a failed
Operations inventory page prevents claiming unique resolution from that snapshot.

Proposed initial tunable budgets, **not platform limits**: 5-minute interval,
10-second connect/60-second read deadlines, 120-second cycle budget, 64 objects
per SOAP page, two transient retries with jitter within that budget. Explicitly
bound VM/host counts, response bytes and emitted edges during implementation;
exhaustion reports incomplete and disables reconciliation, never silent truncation.
Use bounded concurrency and one in-flight cycle; discard/interrupt closes work.

## Exact identity and publication contracts

| Resource | Stable contract |
|---|---|
| Existing VM | Adapter `VMWARE`, kind `VirtualMachine`; exact `VMEntityVCID = about.instanceUuid` **and** `VMEntityObjectID = VM MOR value`, both uniqueness-bearing. |
| Owned RdmMapping | Adapter `vcfcf_rdm_topology_poc`, kind `RdmMapping`; existing vCenter UUID + VM `config.instanceUuid` + virtual-disk key tuple, unchanged. |
| Owned CanonicalLun | Same owned adapter, kind `CanonicalLun`; sole unique `identity_token=scsi-vpd83:naa:<complete-lowercase-payload>`; no source/instance scope. |

For the foreign VM preserve **every** returned identifier name, value, order and
actual boolean uniqueness flag. Preserve supported empty-string nonunique values;
reject absent/null unsupported values, duplicate/conflicting identifiers, false
or missing required flags, incomplete keys and multiple matching resources.
Never resolve by display name, bare MOID or guessed partial key. Do not reuse the
current generic resolver's false-coercion/empty-value handling without correction.

The automatic qualifier is an explicit proposed evidence-policy change, not a
fixture workaround: exact current-host backing UUID join + one unambiguous
LU-associated binary NAA5/6 designator + full canonical-payload agreement.
Validate namespace, complete VPD83 header, association zero, type three, length,
reserved bits and signed-byte bit preservation. `namespaceId` is not designator
type. Opaque UUIDs are not decoded as NAA. Reject conflicts/unsupported claims.
Do **not** synthesize the POC's independent `storage_reference` from canonicalName;
automatic provenance says vSphere-derived, not independently array-corroborated.

If LUN qualification fails but VM/mapping identity is valid, preserve/publish
VM → RdmMapping with unresolved LUN assessment; emit no guessed LUN/new edge.
Cross-observation identity conflicts quarantine all affected candidate edges.
Foreign VM absence is unresolved, not permission to invent a VM or attach another.

Keep `parentForeign(vm,mapping).build()` and owned
`parent(mapping,lun).buildDelta(false)`. Deduplicate repeated edges explicitly;
no VMware-owned resource writes, broad relationship replacement or VMware-owned
credential access. Group/leaf descriptor keys remain legal E3.5.1 segments; runtime full
property paths retain their separators. The known two-edge topology is unchanged.

Publish intrinsic format/canonical identity on the LUN. Mutable vendor/model/
capacity descriptions require same-cycle consensus under a single authority;
absence is unknown, conflict is surfaced, and capacity expansion is not an ID
change. Source-specific host/path/display observations belong on mapping/source
provenance, not last-writer-wins global properties. Array volume/pool names and
array serial numbers are not guaranteed by vSphere.

## Multi-host, multi-vCenter and lifecycle limits

Shared RDMs within one authority converge by exact qualified token; every mapping
retains its independent VM/disk identity. A host join never uses another host as
a substitute. Repeated identical complete observations produce identical keys.

Practical connection model: one vCenter credential/endpoint per adapter instance.
**Initial publication remains one logical writer for potentially shared LUNs.**
The customer's eight-vCenter target is not solved by launching eight writers:
cross-instance coalescing, ownership, conflicting property publication and shared
LUN relationship survival must be proven first. No vCenter/instance suffix may be
added to hide the conflict. Nonoverlapping deployment requires proven disjoint
LUN scope; overlapping multi-vCenter publication is BLOCKED pending those proofs.
Cross-vCenter cloned/reused NAA collisions cannot always be detected without
visibility of conflicting observations; strict token validation alone is not
proof that all independently administered storage assigns unique identifiers.
Do not invent an external coordinator or unsupported credential-store API.

Initial automatic collection adds only; explicitly expose stale/unresolved status.
Safe removals require durable owned-edge provenance, two complete successful
same-scope observations plus a proposed grace period, then narrowly targeted SDK
`buildDelta(true)` removals after deployed proof. Never delete from outage,
permission loss, scope change or partial pages. Lost ownership on restart fails
closed. Retargeting, ownership storage API and race-safe shared-LUN cleanup remain
implementation prerequisites; no automatic LUN garbage collection or VMware
resource deletion. Additive edges otherwise outlive removed attachments.
Two successful caller-visible snapshots alone cannot prove deletion: permission
changes can hide objects without per-object faults. Removals stay disabled until
authoritative coverage and durable ownership backend/API are established; two
empty lists are not sufficient evidence.

## Migration and smallest next implementation

Keep the existing independent repository and adapter kind to preserve full keys;
a separate kind would change those keys and require migration, not simplify it.
Fixture mode becomes test-only, not an exposed production workaround. Do not
expand fixture fields or split JSON to evade UI limits.

No automatic change to the installed development instance: a later authorized
transition must privately snapshot exact keys/relationships, quiesce old collection,
deliberately configure endpoint/credential/trust, and prove adoption without duplicate
owned keys. Do not delete the old instance/resources as a migration shortcut.
Adding required credentials to formerly credential-free metadata needs controlled
instance-upgrade tests and rollback; fail closed until configuration is complete.

**Recommend E4.2:** implement Java transport, bounded typed SOAP decoder and strict
composite Operations resolver into an in-memory graph, tested with local fake
SOAP/HTTP/PKI endpoints. No publication engine or live PAK is needed initially.
Test pagination/faults, XML attacks, auth expiry/redaction, TLS chain/name failures,
descriptors, identical MOIDs across vCenters, full key flags/empty values, vMotion,
shared RDMs, conflicts, capacity overflow, limits and deterministic repeated output.

GO only to that separately approved implementation increment. Production readiness
remains blocked on runtime dependency/TLS/ambient-RBAC proofs, intrinsic qualifier
review, cleanup/ownership design and multi-writer qualification. Live local-edge
acceptance/persistence and migration/failover remain distinct future experiments.

## Independent disposition and validation

[Independent technical architecture review](../../context/reviews/rdm-topology-e41-automatic-discovery-review.md):
**APPROVE**, zero outstanding findings, for the architecture and proposed offline
E4.2 boundary only. Operator implementation approval is still required. This is
not certification of a customer-ready collector or authorization to change the lab.

Changed-document and full content validation, Codex skill parity and diff checks
passed. Path-reference audit is clear with six existing standing warnings.
Only the API map, this design and its independent review were added by E4.1;
pre-existing worktree changes were preserved. No adapter/source modifications,
builds, live queries, fixture expansion, installation, commits or pushes occurred.
