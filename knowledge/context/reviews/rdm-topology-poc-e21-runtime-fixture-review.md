# E2.1 — independent runtime-fixture SDK review

**Verdict: APPROVE — zero implementation BLOCKING findings.** Build 5 is
ready for a separately authorized controlled development-lab installation,
not proof of installation acceptance, relationship persistence, UI visibility,
or collector failover. No live test was performed.

## Scope and independence

Reviewed the independent RDM adapter checkout based on
`160f6461541ca312708ee880f3b5837b7ccfd312`, with uncommitted E2.1 changes.
The reviewer did not edit adapter code or comparator rules. The source review,
focused tests, SDK validation, isolated development rebuild, archive inspection
and exact-candidate structural comparison were independently executed offline.
No SDK download, endpoint access, installation, commit or publication occurred.

Authorities: `.claude/agents/sdk-adapter-reviewer.md`, the shared reviewer
doctrine, `vcfops-sdk-adapter` stitching-identity/build/gap contracts,
RULE-001/005/008/012/014, and the cross-MP uniqueness-flag and scoped-MOID
lessons. The user authorized runtime fixture binding, not a production collector.

The independent adapter repository remains separate from the factory; its
source is publicly identified at
<https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology>.
Build-5 source changes are local and uncommitted, not yet reproducible from that
remote. The SDK and development PAKs are local-only, not redistributable SDK
evidence or approved release artifacts; relevant results are summarized here.

## Implementation assessment

- `describe.xml` declares one required ordinary string `fixture_json` on
  the adapter-instance kind with `identType="2"`, no default and explicit
  `isCredentialRequired="false"`. No CredentialKinds, credential reference,
  endpoint or authentication was introduced.
- The mechanism is evidenced, not invented: compliance's descriptor uses
  identType-2 string configuration; `VcfCfAdapter.onConfigure` supplies the
  instance's SDK `ResourceConfig`, whose `getResourceIdentifiers()` exposes
  `ResourceIdentifierConfig` values. SDK inspection confirms the relevant
  methods and `ResourceIdentifierDescribe`'s type/identType parsing. An SDK
  declaration establishes a configuration contract, not a UI acceptance proof.
- `RuntimeFixture` parses exactly one bounded structured fixture before
  any discovery or relationship emission. It rejects unknown/duplicate keys,
  incomplete or wrong kinds, missing/nonboolean flags, missing scoped unique
  MOID/vCenter identifiers, malformed/zero UUIDs, conflicting UUID evidence,
  malformed JSON/escapes/surrogates, trailing input and invalid disk keys.
  Input/depth/value/string bounds precede uncontrolled growth or recursion.
  Exceptions are generic and do not retain fixture values or chained causes.
- Every supplied foreign identifier's exact name, value and boolean flag is
  preserved, including nonunique and additional unique identifiers. Names
  remain descriptive, never the disambiguation key. The stable local key
  remains vCenter instance UUID + VM instance UUID + virtual-disk key.
- Configuration is immutable after validation. Failed reconfiguration clears
  the previous fixture; absent/stale config or a mismatched resource key
  cannot emit a relationship. SDK bytecode inspection confirms
  `AdapterBase.configure` queues configuration and uses the same semaphore as
  collection before applying it; configuration arriving during collection is
  deferred. No framework synchronization modification was necessary.
- `RdmTopologyRelationships` is unchanged: one foreign VMware VM parent and
  one local `RdmMapping` child through `parentForeign(...).build()`. Tests
  confirm additive, non-clear-first output and stable repeated payloads.
  No foreign resource definitions, metrics or child-list replacement occur.
- Compiled runtime synthetic fixtures were removed; synthetic data now lives
  only in tests. Runtime source has no node-file, environment-variable or
  network input. README, installing instructions and reference documentation
  describe the new field and limitations consistently.

Fixture validation cannot prove live VM existence, unique resolution, omitted
unknown native identifiers, or truth of operator-supplied flags. The existing
exact-key pre-install proof is retained, not replaced by parser success.

## Independent verification

| Check | Observed result |
|---|---|
| Focused Java suite | PASS: 7 topology tests; 35 invalid-input lifecycle cases plus valid, exact-flag, scoped-VM, stable-repeat and stale/reconfiguration guards |
| Actual config binding | Tests execute real `onConfigure`, SDK ResourceConfig and collection/discovery hooks; no live services |
| SDK descriptor object loading | Explicit SKIP: local log4j-api unavailable; DOM contract tests pass, SDK methods/bytecode and working examples inspected |
| `validate-sdk` | PASS, five runtime Java source files compile |
| Independent development `build-sdk` | PASS to isolated temporary output, explicit structural gate; no overwrite of the author's candidate |
| Candidate archive | Recursive ZIP/JAR integrity PASS; correct credential-free fixture descriptor; no SDK/vendor bytecode, test classes or compiled synthetic fixture |
| Rebuild equivalence | All recursively unpacked file paths and leaf bytes match the author's candidate; ZIP/JAR container checksum differs |
| Exact candidate `pak-compare` | PASS, exit 0: **0 BLOCKING / 3 WARNING / 22 INFO** |
| Adapter whitespace | `git diff --check` PASS |

Tests bypass SDK constructor/platform initialization with the established
test-only allocation idiom and a null-return logging-factory test proxy because
appliance logging dependencies are absent. This is honest binding-logic
coverage, not a successful platform startup or complete collect-result
ingestion test. No logging library was installed or bundled to disguise the gap.
The existing javac source/target-11-without-`--release 11` warning remains.

Assessed deployment candidate: `vcfcf_sdk_rdm_topology_poc.0.0.0.5.pak`, SHA-256
`7cfa0f9f829eade4bb6eaa3c0e5faf502b2bb288501b854e8c6cc3bcb0ebf9ae`.
Independent temporary rebuild SHA-256:
`b7bd0c73274d14dee590054558b4f714327c7c5032cf76fbc184b7c84a1d0482`.
The latter verifies source/build mechanics; it does not replace the assessed
candidate or establish byte-identical archive reproducibility.

Reference: approved Synology v1.0.0.30 PAK, SHA-256
`beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.
The exact structural comparison explicitly supplies this digest. Both the
candidate and independent rebuild report all three existing warnings:
D8 adapter-instance identifier count 1 versus 3; D23 traversal-kind count 0
versus 1; D25 absent traversal entries. None was suppressed/reclassified;
these are not evidence of missing relationship persistence or UI success.
Build 4 remains unchanged at SHA-256
`5354acc09b4afa5a2fad5aed9429adebd8fe0f0e751b0b64b909c59854381d61`.

## Registry and remaining lab evidence

`knowledge/context/defects.md` was read; no open defect affects this adapter.
No local registry override was present. No new implementation defect or
proposed closure is introduced by this review.

The [E2.1 addendum](../../designs/managementpacks/vsphere-rdm-topology-e21-runtime-fixture.md)
and existing E2-P experiment retain the necessary unresolved outcomes:
ordinary field acceptance and nontruncated JSON round-trip, actual platform
initialization/config delivery, exactly one mapping, correct VM relationship,
preserved VMware-owned edges, repeated-collection idempotence, persistence
after VMware collection, UI visibility and verified POC-only cleanup.
Collector placement/failover delivery is expected from instance-managed
configuration but unproven. Test Connection is explicitly not fixture or
topology validation. Changing targets requires stopping and cleaning up the
old experiment; full obsolete-resource lifecycle remains out of scope.

**If used as-is:** the operator can supply one fully validated runtime fixture
without a target-specific rebuild or node-local file; only a separately
authorized lab experiment can establish whether Operations accepts and
retains its additive foreign-parent edge. This review grants no live access.
