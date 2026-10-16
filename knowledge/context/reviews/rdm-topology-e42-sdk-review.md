# E4.2 — Independent native Java discovery SDK review

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT outstanding.**
Approval covers the inert, offline-tested discovery foundation, not production
collection, deployment, topology publication or global storage uniqueness.

## Scope and authority

Independently reviewed the five new Java classes under the independent RDM
adapter's `discovery` package, its deterministic test and test runner, and
`docs/native-discovery-foundation.md`. Authority: the SDK-adapter reviewer
contract/doctrine; RULE-001/002/005/007/008/009/012; SDK skill sections on foreign
identity, unreadable data, bulk reads, classloaders and resource hygiene; the
[approved E4.1 architecture](../../designs/managementpacks/vsphere-rdm-topology-e41-automatic-discovery.md)
and [API map](../api-maps/vsphere-rdm-automatic-discovery.md); E3.3/E3.4.1 and the
existing `RuntimeFixture`, foreign-key and mapping-key contracts.

The managed adapter is independently versioned, not factory-owned source.
The local proprietary SDK is supplied by the operator and cannot be redistributed;
relevant inspection findings are summarized here rather than requiring the JAR
as a published reference. No private inventory, credentials or live systems were
read. Source was reviewed read-only; no implementation repairs were made by this
reviewer.

## Independently verified behavior

- SOAP operations and typed PropertyCollector paths match the approved map.
  Paging, explicit-object completeness, duplicate/fault detection, exact
  current-host joins and the VM instance/change-version/host fence are bounded.
  Failed host/LUN qualification retains an independently valid VM/mapping with
  unresolved status; malformed individual VM data does not discard another
  validated VM. Incomplete query pages never become successful zero inventory.
- Descriptor bytes use the repeated signed-decimal SOAP representation, not a
  guessed base64 representation. Qualification checks namespace and byte bounds,
  binary code set, full header/length, LU association, NAA type/length and exact
  canonical agreement. The automatic provenance is intrinsic vSphere evidence;
  no independent storage reference is fabricated.
- Immutable DTOs retain complete ordered foreign identifiers and actual flags,
  including supported empty nonunique strings. Resolution requires exact vCenter
  UUID and VM MOID and rejects ambiguity. UUID/MOID and disk-key validation,
  scoped/reverse VM identity consistency and full uniqueness-bearing-key consensus
  preserve the existing identity contract without normalizing source values.
  Case-insensitive duplicate-name detection follows the SDK comparator. SDK
  bytecode inspection confirms ResourceKey matching skips nonunique identifiers;
  the new graph conservatively compares retained unique values exactly rather
  than claiming that this is the SDK's case-insensitive value comparison.
- The unscoped CanonicalLun token and mapping tuple are unchanged. Equivalent
  qualified observations converge; conflicting UUID/token or descriptive
  observations quarantine associations. No global-assignment, cross-vCenter or
  multi-writer empirical proof is implied.
- The new code does not call SDK discovery/collection/relationship publication
  methods, load node-local inventory, execute processes, read environment
  credentials or download dependencies. HTTP is confined to the fixed HTTPS SOAP
  transport. Diagnostics and object summaries do not expose credentials or raw
  inventory. SOAP/session/view/cursor cleanup has a bounded secondary allowance.

## Findings resolved before approval

Review iterations identified abandoned host pagination cursors overwritten by
the subsequent fence; overly loose UUID/MOID validation; missing reverse/full-key
identity consistency; per-VM parse failure aborting unrelated groups; and invalid
identity fields escaping validation in zero-VM/zero-RDM cases. These are corrected
and regression-tested in the final reviewed source. The test runner's invalid
`jdeps --summary` invocation is corrected to `-s`.

The parallel security review covers strict TLS/name verification, XML hardening,
absolute deadlines/slow responses, interruption and redaction. SDK review also
inspected the resulting fixed-endpoint trust boundary, watchdog and cleanup
paths. Actual collector provider/FIPS behavior remains a named runtime prerequisite,
not a defect hidden by offline compilation.

## Independent reruns

| Check | Result |
|---|---|
| Discovery runner `--no-network-tests` | **54 deterministic cases passed** |
| Existing Java/actual SDK tests | **8 topology/descriptor tests**, **42 invalid fixture cases**, **34 invalid LUN cases**, plus reported valid/idempotence/convergence matrices passed |
| `validate-sdk` | Passed; 11 production sources compiled; existing `-source 11` system-modules warning retained |
| Explicit discovery compilation `javac --release 11 -proc:none` | Passed |
| Production-class `jdeps --multi-release 11 --recursive -s` | Only `java.base` and `java.xml` |
| Adapter whitespace check | Passed |

These are independent executions, not repeated author claims. The loopback PKI
suite is separately executed/reported by the orchestrator/security reviewer;
this SDK reviewer did not open sockets. Test-only keytool and logging shims are
not production dependencies. No new PAK was built or compared: publication is
disabled, build 9 is unchanged, and building an inert foundation was explicitly
unnecessary. This is not a new install-gate or PAK certification.

The orchestrator's pre/post hash audit additionally confirms that adapter metadata,
descriptor, entry point, existing fixture/identity classes and build-9 PAK were
unchanged by E4.2. Pre-existing worktree changes remain separate from this increment.

## Registry and next boundary

Registry check: `knowledge/context/defects.md` contains **no open defect affecting
the RDM POC**. Historical DEF-005/006 are closed and do not certify the new RDM
transport or injected-identity integration; those lessons remain prerequisites.
No finding survives acceptance requiring defect registration.

Remaining production work is explicit: Operations-managed credential/trust binding,
strict Suite API transport with injected-identity RBAC/routing, deployed SOAP/JDK/
classloader/FIPS qualification, publication/adoption, multi-writer ownership and
safe stale-edge cleanup. No future deletion may be inferred from caller-visible
empty or incomplete inventory.

**If shipped as-is:** existing fixture-driven behavior remains unchanged; the new
foundation cannot activate automatic collection or publish topology. Recommend
E4.3 configuration/trust and read-only scoped Operations resolver integration,
still without publication, under separate authorization.
