# E4.2 — Native Java RDM discovery foundation

## Scope and evidence boundary

This increment implements the offline foundation approved in
[E4.1](vsphere-rdm-topology-e41-automatic-discovery.md), using its
[API map](../../context/api-maps/vsphere-rdm-automatic-discovery.md) and
[independent architecture review](../../context/reviews/rdm-topology-e41-automatic-discovery-review.md).
The independent implementation repository remains
`content/sdk-adapters/rdm-topology-poc`; no repository boundary is changed.

The new discovery code is intentionally separate from the registered POC adapter.
Its output is an in-memory graph, not discovered Operations resources or emitted
relationships. Existing fixture configuration, credential-free descriptor,
resource identities and the live-proven foreign-parent path are not activated,
rewired or migrated by this increment. No new PAK or development version is
required merely to compile/test dormant Java source.

## Required implementation contract

- Native Java HTTPS/XML vim25 SOAP only; no runtime external process, download,
  node-local fixture, Python, JAX-WS provider, storage-array client or sidecar.
- HTTPS must validate chain and configured hostname, support explicitly supplied
  in-memory enterprise trust, refuse credential-bearing redirects, and bound I/O.
  Local fake/TLS test servers are not live VMware endpoints.
- Harden XML before decoding: namespaces and SOAP structure, DTD/entity/external
  resolution rejection, bounded bytes/depth/nodes/text and safe request encoding.
- Session/view/pagination cleanup must not expose tokens, passwords, inventory or
  raw SOAP fault text, or obscure a primary failure.
- Complete bounded PropertyCollector traversal, exact typed VM/RDM/host-LUN
  joins, explicit missing/fault/ambiguity states, and VM host/config consistency
  checks. No inaccessible inventory becomes a successful zero-attachment result.
- Scoped Operations resolution is an explicit offline interface, not a guessed
  production authentication implementation. Preserve the entire supported VM
  ResourceKey and require vCenter UUID plus VM MOID with actual uniqueness flags.
- Keep mapping identity vCenter instance UUID + VM instance UUID + disk key and
  the unscoped `scsi-vpd83:naa:<complete-payload>` LUN token. Automatic evidence
  uses exact current-host backing/SCSI UUID join, full LU-associated NAA5/6
  descriptor proof and canonical agreement; it does not invent an independent
  storage-side reference. Provenance remains explicitly vSphere-derived.
- Graph data is immutable and cannot publish resources, replace relationships,
  delete inventory or imply that Operations accepted a new topology.

## Implemented surfaces

All adapter additions are under its own repository; no factory Python/tooling or
existing adapter runtime files were changed by E4.2:

| New surface | Responsibility |
|---|---|
| `src/com/vcfcf/adapters/rdmtopologypoc/discovery/DiscoveryException.java` | Static sanitized failure categories, no raw causes/payloads |
| `discovery/SecureSoap.java` in the same source package | Bounded streaming precheck plus hardened namespace-aware DOM, SOAP/typed-value helpers |
| `discovery/HttpsSoapTransport.java` | Fixed HTTPS `/sdk`, explicit in-memory CA trust, chain/host checks, bounded I/O and request watchdog |
| `discovery/VimDiscoveryClient.java` | One-shot session, view, paged bulk VM/host reads, consistency fence, cleanup and in-memory assembly |
| `discovery/DiscoveryGraph.java` | Immutable keys/descriptors/attachments/LUNs, exact scoped offline resolver and intrinsic qualifier |
| `tests/com/vcfcf/adapters/rdmtopologypoc/discovery/DiscoveryFoundationTest.java` | Synthetic wire, identity, lifecycle, XML and loopback-PKI regressions |
| `scripts/run-discovery-tests.sh`, `docs/native-discovery-foundation.md` | Standalone tests and exact implementation/limits/integration contract |

The graph retains ordered, unmodified foreign identifier entries, with supported
empty nonunique values. It rejects missing scope, ambiguous candidates, malformed
UUID/MOID values, duplicate mappings, conflicting extra uniqueness-bearing
identifiers and inconsistent forward/reverse VM identity. Mutable SDK ResourceKeys
are not exposed. LUN bytes and collections are defensively copied.

Malformed per-VM decoding is isolated from unrelated valid VMs; incomplete host
inventory leaves independently valid mappings unresolved. Globally incomplete VM
paging fails closed. Descriptive/UUID/token conflicts quarantine affected LUN
associations. Even zero-VM/zero-RDM responses still undergo source identity and
required-property validation; they are not an escape from those checks.

Native wire evidence was verified offline with the installed pyVmomi serializer
using synthetic `ScsiLunDurableName`: `namespaceId` is a byte and `data` is a
repeated signed-decimal byte array, not assumed base64. The transport declares
the versioned vim25 6.5 compatibility baseline. These checks do not establish
compatibility with every vCenter/collector build; real target qualification
remains separately authorized. No real private inventory was read or replayed.

Default limits are implementation budgets, not platform maxima: 4 MiB responses,
32 XML levels, bounded nodes/attributes/text, 64 pages/query, 10,000 objects/query,
128 primary requests and a 120-second cycle. Session retirement has a separate
bounded cleanup allowance. Request watchdogs disconnect expired/interrupted I/O;
provider-specific cancellation remains a runtime qualification requirement.

## Offline validation and dependency assessment

Run from the factory root:

```bash
bash content/sdk-adapters/rdm-topology-poc/scripts/run-discovery-tests.sh --no-network-tests
bash content/sdk-adapters/rdm-topology-poc/scripts/run-discovery-tests.sh
VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
  bash content/sdk-adapters/rdm-topology-poc/scripts/run-tests.sh
VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
  PYTHONPATH=src .venv/bin/python -m vcfcf_managementpacks validate-sdk \
  content/sdk-adapters/rdm-topology-poc
```

The full discovery script opens a temporary **loopback-only** HTTPS server and
uses the already installed JDK/keytool to generate a synthetic CA and signed
server certificate. Sandbox socket binding required explicit local-test execution
approval; no VMware endpoint was contacted. Test keystores are temporary and
removed. Keytool, test sockets and test logging shims are not production runtime
dependencies.

| Check | Actual result |
|---|---|
| Pure offline discovery tests | 54 passed |
| Full discovery script, including real loopback TLS/slow-response deadline checks | 55 deterministic cases passed, exit 0 |
| Existing Java POC suites | 8 topology/descriptor tests, 42 invalid-runtime cases, 34 invalid-LUN cases and existing positive matrices passed |
| Explicit Java 11 compilation / validate-sdk | Passed; 11 production sources compile, existing builder source/target-11 warning remains |
| Production `jdeps` analysis | New foundation depends only on `java.base` and `java.xml`; no JAX-WS/provider/third-party JAR dependency |
| Complete factory suite | 2489 passed / 20 skipped / 131 deselected / 1 unchanged setup-test failure |
| Full content validation, skill parity, whitespace checks | Passed |

The unchanged failure is
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`;
no unrelated test or implementation correction was made. Path-reference audit
retains six documented standing warnings.

No PAK build or structural comparison was appropriate: there is no new artifact
or install candidate. Build metadata, descriptor, registered entry point,
RuntimeFixture, ForeignVmIdentity and CanonicalLunIdentity hashes were checked
against the pre-E4.2 worktree and remain identical. The existing local build-9
PAK is unchanged, SHA-256
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
This is an existing local-only artifact record, not a newly published baseline.

Packaging assessment is static: the new production sources require no added
libraries; the existing builder excludes tests and provides the Operations SDK
from the platform. No proprietary SDK was copied or bundled, no independently
licensed managed-adapter source was copied, and no installation-time download is
needed. Local JDK class/dependency checks are not proof of the deployed provider,
FIPS, certificate-store or collector classloader matrix.

## Independent verdict and handoff

- [SDK implementation review](../../context/reviews/rdm-topology-e42-sdk-review.md):
  **APPROVE**, zero outstanding implementation findings.
- [Security review](../../context/reviews/rdm-topology-e42-security-review.md):
  **APPROVE**, zero outstanding findings; independently reran all 55 cases,
  including actual loopback TLS and slow-response deadline checks.

Review findings concerning SOAP namespace/header handling, abandoned cursors,
reserved cleanup budgets, cancellation/deadlines, UUID/full foreign-key
consistency, per-VM isolation and empty-inventory validation were fixed and
regression-tested before approval. No finding was waived to obtain a pass.

**COMPLETE for the offline foundation; not an install/production candidate.**
Only the new adapter sources/tests/script/document and this factory record/review
artifacts were authored by E4.2; earlier worktree changes remain intact. Nothing
was staged, committed, pushed, tagged or published. No live systems, real fixture
files, stored credentials or installed adapter instances were accessed or changed.

## Production boundary and next increment

Runtime authentication/RBAC and endpoint routing for the Operations lookup,
Operations-managed certificate/configuration binding, collector-provider/FIPS
qualification and failover remain separate integration work. No VMware
integration credential harvesting or maintenance-file fallback is permitted.

The E3.3/E4.1 single-authority restriction remains: no claim that overlapping
vCenter instances safely co-own a global LUN resource. Durable ownership,
authoritative coverage and safe stale-edge removal remain unimplemented. No
automatic LUN garbage collection or VMware resource deletion is introduced.

The smallest next E4.3 should close the strict Operations lookup/injected-identity
and normal adapter configuration/trust integration boundary, initially without
resource publication. A separately approved read-only runtime check must prove
that bridge on the intended collector placement before an automatic topology
publication experiment. It must not expand the temporary fixture mechanism.
