# E2.2 — SDK-backed empty identifier compatibility

This offline correction supersedes only the value-validation restriction in
the [E2.1 runtime fixture contract](vsphere-rdm-topology-e21-runtime-fixture.md).
It does not authorize live capture, installation, account creation or collection.

## Evidence and decision

The operator confirmed `IDENTIFIER_VALUE_EMPTY`. Earlier sanitized evidence
showed six VM identifiers, two with absent-or-empty nonunique values; those
reports alone did not distinguish omitted, null and empty. E2.1 incorrectly
required every identifier value to be nonblank, including nonidentity metadata.
The Suite API schema in `reference/docs/operations-api.json`, definitions
`resource-identifier` and `resource-identifier-type`, permits optional values;
that does not establish which representations the Java SDK can retain.

Actual SDK bytecode inspection and executable synthetic tests established:

| Representation | SDK behavior | POC contract |
|---|---|---|
| Populated string | Retained verbatim | Existing validation unchanged |
| Exactly `""`, explicit nonunique flag | `ResourceKey.addIdentifier` succeeds and retains the entry/value/flag | Accept unchanged |
| Exactly `""`, uniqueness-bearing flag | SDK can store it; unsuitable for this POC's required stable identity | Reject |
| Explicit null | `ResourceIdentifierConfig` stores null, but `ResourceKey.addIdentifier` returns false without adding the entry | Reject; never convert or drop |
| Omitted value | No SDK API for an identifier's omitted-value presence distinct from its String value | Reject; never supply a default |
| Whitespace-only string | No equivalence to empty is assumed | Existing rejection unchanged |

The supplied SDK is local-only proprietary material, not redistributed or
registry-fetchable. These findings summarize the relevant interfaces in full:
`ResourceIdentifierConfig(String,String,boolean)` stores its value without
conversion; `getValue()` returns it; `ResourceKey.addIdentifier` delegates to
`addOrUpdateIdentifierImpl`, which rejects null keys/values and duplicate names
using `equalsIgnoreCase`. Non-null entries are sorted by the SDK comparator.
`ResourceIdentifierList.compareTo` skips nonunique entries. Thus SDK key equality
ignores changes/absence in nonunique metadata, but **representation equivalence
does not follow**. Every supplied entry must still survive construction.

SDK SHA-256:
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
No conclusion here proves the server's foreign-resource resolver or persistence.

## Minimal coordinated correction

- `RuntimeFixture` and `ForeignVmIdentity.Identifier` accept exactly empty
  strings only when the supplied Boolean uniqueness flag is false.
- `VMEntityObjectID` and `VMEntityVCID` remain mandatory, populated and
  uniqueness-bearing; exact vCenter scope and MOID matching are unchanged.
  Any supplied `VMEntityInstanceUUID` remains valid, nonblank UUID evidence
  matching the mapping, even if its flag is false. Additional unique values
  cannot be empty. Malformed/conflicting identities still fail closed.
- Fixture list ordering, names, values and flags are preserved. The SDK sorts
  its own identifier list; no application-level renaming or reordering is used
  to manufacture a match. SDK-case-insensitive duplicate names are rejected,
  and failed `addIdentifier` calls now throw instead of silently losing entries.
- Python preserves exactly `""` for explicit nonunique identifiers and still
  rejects missing/null values and absent/nonboolean flags. It does not infer
  the API's default-true flag. Its final offline gate executes the **actual
  Java parser**, avoiding a second full UUID/Unicode/parser implementation.
  Python does not casefold identifiers to approximate SDK Unicode comparisons.
- The one-mapping rule, stable RDM tuple, credential-free configuration and
  additive `parentForeign` relationship remain unchanged. Export diagnostics,
  fixed ignored path, exclusive `0600` creation and failure cleanup remain.

If a future capture returns omitted or null values, **stop**. This increment
does not provide a faithful SDK representation for those entries and does not
authorize substituting `""`, omitting identifiers or inventing values.

## Offline candidate and verification

Independent adapter source base: `31725abe68be7ec4420fc4952259a1d8314be1a8`,
plus uncommitted build-6 changes. Factory and adapter remain separate Git repos.
Local-only development candidate (not an approved release or fetchable artifact):
`vcfcf_sdk_rdm_topology_poc.0.0.0.6.pak`, generated in the factory's ignored
`dist` output directory. SHA-256:
`0e77f1837cef68d6c40883fc5ff2359211307ef600940dd2ee140e25449aafc2`.
Build 5 remains unchanged at
`7cfa0f9f829eade4bb6eaa3c0e5faf502b2bb288501b854e8c6cc3bcb0ebf9ae`.

- Java: seven topology tests, 42 invalid-input lifecycle cases, actual SDK
  storage/order/matching tests and six-identifier exact roundtrip, additive
  relationship and repeated-collection checks passed.
- Python: 150 focused tests passed, including populated/empty/omitted/null
  parity against the actual Java parser and preservation of six entries.
- `validate-sdk` and local development `build-sdk` passed. Existing javac
  source/target-11 warning remains. Descriptor object loading remains skipped
  without local Log4j API; lifecycle tests bypass platform construction.
- Approved structural comparison: exit 0, **0 BLOCKING / 3 WARNING / 22 INFO**.
  Synology v1.0.0.30 reference SHA-256:
  `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.
  Unchanged warnings: D8 instance identifiers 1 vs 3, D23 traversal count 0 vs
  1, D25 no traversal entries. No comparator rule or finding changed.

Package inspection and independent disposition are recorded in the
[E2.2 SDK review](../../context/reviews/rdm-topology-poc-e22-empty-identifiers-review.md).
**APPROVE, zero implementation blockers.** Recursive package inspection passed:
no proprietary SDK/vendor bytecode, compiled test fixtures, credentials or raw
lab data were supplied or bundled. Full content validation, skill parity and
path-reference checks passed, with six documented standing path warnings.
Full platform startup/configuration delivery, UI behavior, failover and foreign
relationship persistence remain separately authorized lab outcomes.

## Operator retry — not executed by this increment

From the factory root with the already configured development credentials/TLS
environment; do not put credentials on argv or source them in a logged command:

```bash
PYTHONPATH=src \
VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
.venv/bin/python scripts/rdm_lab_probe.py \
  --execute --allow-read-only-lab --mode fixture-export --profile devel
```

This retry is live read-only capture and is for the operator under an applicable
authorization, not automatic execution here. It validates with the corrected
Java parser and writes only the fixed ignored `tmp/rdm-lab-probes/rdm-fixture-vm-71.json`
handoff with `0600`, never overwriting an existing file. It prints no payload.
Any omitted/null/ambiguous/conflicting identity remains a stop condition.
Build 5 cannot consume the corrected empty-value fixture; a later, separately
authorized installation experiment must use the checksum-pinned build 6.
