# E2.1 — runtime fixture configuration

**E2.2 correction:** build 6 supports explicit empty-string values only for
nonunique, nonidentity identifiers, without normalization or omission. See the
[SDK-backed compatibility addendum](vsphere-rdm-topology-e22-empty-identifiers.md)
for evidence, limits, the new candidate and operator retry. Build-5 validation
results below remain historical; build 5 does not support that representation.

Local development candidate only; no installation or live access authorized.
This addendum replaces the build-4 fixture-binding blocker in the
[E2-P procedure](vsphere-rdm-topology-e2p-lab-evaluation.md), not its identity,
baseline, persistence, stop-condition or cleanup requirements.

## Supported binding and evidence

One required ordinary string identifier, `fixture_json`, belongs to the POC
adapter-instance ResourceKind. `identType="2"` makes it configuration rather
than part of instance uniqueness. There is no default fixture, credential,
endpoint, collector-node file or environment-variable input.

Evidence: the existing compliance adapter uses ordinary string/identType-2
settings; the factory's `VcfCfAdapter.onConfigure` passes the instance
`ResourceConfig` into `configureAdapter`, and `getIdentifier` reads its
`ResourceIdentifierConfig` list. SDK inspection confirms this list API,
boolean uniqueness flags, nonunique identifier updates and descriptor
`type`/`identType` parsing. The proprietary SDK is local-only and cannot be
redistributed; these findings summarize its relevant interfaces. Framework
evidence is in `src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/VcfCfAdapter.java`.

Operations-managed configuration is expected to travel with the instance
across collector placement/failover; no per-node synchronization is required
by this design. Actual UI round-trip, accepted field length, platform
initialization and failover delivery remain **unverified lab outcomes**.
No undocumented textarea or file-loading descriptor extension is used.

## Schema — synthetic example only

```json
{
  "foreign_vm": {
    "adapterKindKey": "VMWARE",
    "resourceKindKey": "VirtualMachine",
    "name": "synthetic-vm",
    "resourceIdentifiers": [
      {"identifierType": {"name": "VMEntityObjectID", "isPartOfUniqueness": true}, "value": "vm-1001"},
      {"identifierType": {"name": "VMEntityVCID", "isPartOfUniqueness": true}, "value": "11111111-1111-4111-8111-111111111111"}
    ]
  },
  "mapping": {
    "vcenter_instance_uuid": "11111111-1111-4111-8111-111111111111",
    "vm_instance_uuid": "22222222-2222-4222-8222-222222222222",
    "virtual_disk_key": "2000"
  }
}
```

Copy the **complete actual** uniquely resolved Suite API `resourceKey` into
`foreign_vm`, preserving every identifier name/value/boolean uniqueness flag
and resource name. The abbreviated synthetic key above is not a template for
dropping additional identifiers. `name` is descriptive, never identity proof.
Supply the verified SOAP stable tuple separately in `mapping`; VM instance
UUID is not the Operations resource UUID or VM MOID.

Strict parsing rejects missing/extra fields, duplicate JSON keys or identifier
names, trailing input, coercions, absent/false required uniqueness flags,
wrong resource kinds, bare MOIDs, malformed/zero UUIDs, conflicting vCenter
or optional `VMEntityInstanceUUID`, and noncanonical/nonpositive/out-of-range
disk keys. Bounds: 32,768 input characters, 4,096 per string, depth 12 and
512 parsed values. UUID strings and foreign identifiers are not normalized.
Both scoped identifiers must be uniqueness-bearing. Every additional supplied
identifier and flag is retained exactly.

This checks schema and internal consistency, **not live existence or unique
resolution**, nor whether an operator omitted an unknown native identifier.
The existing pre-install exact-key proof remains mandatory. Errors contain
no fixture values. Invalid reconfiguration clears the previous fixture;
discovery and collection reject missing or stale configuration before emission.
Identical input retains the same mapping key and additive foreign-parent edge.
No foreign definition or VMware-owned child list is replaced.

## Operator steps — only after separate lab authorization

1. Use the E2-P complete baseline and exact-VM proof. Keep actual fixture JSON
   in approved restrictive local scratch only, never Git, logs or chat.
2. Install the checksum-pinned candidate below through the existing management
   pack UI. Add one POC account on the designated development collector.
3. Enter the compact JSON into **Runtime Fixture JSON (lab only)** (`fixture_json`), an
   ordinary required configuration field; supply no credentials or endpoint.
   The UI label/location and length acceptance are to be verified, not assumed.
   If absent, truncated, rewritten, or credential prompts appear, stop.
4. Save and allow a completed POC collection. Test Connection is not fixture
   validation or evidence of emitted topology; the POC has no remote tester.
   Follow E2-P exactly for one mapping, the exact VM edge, unchanged VMware
   topology, repeated collection, subsequent VMware collection and cleanup.
5. Treat a different target fixture as a different experiment: stop collection
   and complete existing POC-only cleanup before switching. Full obsolete-
   resource lifecycle remains out of scope. Never repair VMware topology.

Acceptance, API persistence and topology UI visibility are separate results.
Placement/failover testing, if later authorized, must verify the same key/edge
without node-local input; offline tests do not prove this behavior.

## Candidate and validation record

Local-only candidate: `vcfcf_sdk_rdm_topology_poc.0.0.0.5.pak`.
SHA-256: `7cfa0f9f829eade4bb6eaa3c0e5faf502b2bb288501b854e8c6cc3bcb0ebf9ae`.
Source base: independent adapter commit
`160f6461541ca312708ee880f3b5837b7ccfd312`, plus uncommitted E2.1 changes.
Build 4 remains unchanged and unsuitable for real-target binding. Neither
candidate is an approved release or registry-fetchable artifact.

- Seven topology tests and the runtime matrix passed: 35 invalid-input
  lifecycle cases plus valid input, idempotence, scoped-VM and reconfiguration
  guards. Tests invoke real `onConfigure` with SDK ResourceConfig objects,
  using the framework's existing test-only constructor-bypass pattern because
  local Log4j dependencies are unavailable. This is not platform bootstrap.
  SDK descriptor `load` test was explicitly skipped for missing Log4j API;
  DOM assertions, working examples and SDK bytecode support the descriptor.
- `validate-sdk` and development `build-sdk` passed. Existing javac warning:
  source/target 11 without `--release 11`; no toolchain change made here.
- Recursive package integrity and unchanged CI package inspection passed:
  only adapter/framework JARs, no Broadcom SDK/vendor bytecode, test classes,
  compiled synthetic fixture or credential declarations/references. No real
  lab payload was read or supplied during this increment.
- Approved structural comparison passed, **exit 0: 0 BLOCKING / 3 WARNING /
  22 INFO**. Reference Synology v1.0.0.30 SHA-256:
  `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.
  Warnings retained: D8 instance identifier count 1 vs 3; D23 traversal count
  0 vs 1; D25 absent traversal entries. No finding was suppressed or changed.
- Full factory content chain, skill parity and path audit passed; path audit
  retained six documented standing warnings. No framework or CI policy changed.
  The unchanged adapter CI helper suite also passed all 24 tests.

Independent review and final readiness disposition are recorded in the
[E2.1 SDK review](../../context/reviews/rdm-topology-poc-e21-runtime-fixture-review.md).
**APPROVE, zero implementation blockers. READY for a separately authorized
controlled development-lab installation**, not proof of platform acceptance,
relationship persistence, UI visibility or failover. The reviewer independently
rebuilt in scratch and found identical unpacked package leaves; archive hashes
can differ with container timestamps. Use the exact candidate checksum above.
No source commit, publication, live query or installation is performed.
