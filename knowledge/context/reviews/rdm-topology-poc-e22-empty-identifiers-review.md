# E2.2 — independent empty-identifier compatibility review

**Verdict: APPROVE — zero implementation BLOCKING findings.** The narrow
correction faithfully supports explicitly empty, nonunique identifier strings;
it does not authorize live capture or installation and does not establish
foreign-relationship persistence.

## Scope and SDK evidence

Reviewed local changes against factory base
`322158b95e494a5c6707e978471f977e87582042` and independent adapter base
`31725abe68be7ec4420fc4952259a1d8314be1a8`. Source, tests, configuration and
package inspection were independent of the author. No source fixes, live
connections, credential reads, commits, pushes or publication were performed.
Authorities: RULE-001/005/008/012/014, the SDK reviewer doctrine,
`vcfops-sdk-adapter` stitching/build/gap contracts, and
`knowledge/lessons/cross-mp-foreign-key-uniqueness-flags.md`.

The supplied proprietary SDK is local-only and not redistributable or
registry-fetchable; relevant findings are summarized here in full. Its SHA-256
is `2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
Independent `javap` inspection and executable tests establish:

- `ResourceIdentifierConfig(String, String, boolean)` retains its value,
  including null, without conversion.
- `ResourceKey.addIdentifier` rejects a null-valued entry and returns false;
  it retains an explicitly empty string. Therefore null/absence cannot be
  claimed faithfully representable through this supported insertion API.
- Identifier-name collisions are checked ignoring case; the SDK sorts entries
  by name. Names, strings and uniqueness flags themselves remain unmodified.
- ResourceKey equality uses uniqueness-bearing identifiers. Different
  nonunique values or absence may compare equal, but equality is not evidence
  that those representations can be normalized or dropped.

## Implementation assessment

`RuntimeFixture` and `ForeignVmIdentity.Identifier` now allow exactly `""`
only with an explicit false uniqueness flag. Unique values, scoped
`VMEntityObjectID`/`VMEntityVCID`, optional `VMEntityInstanceUUID` evidence,
and the stable RDM tuple retain their previous nonblank, format and
consistency requirements. Missing/null/nonstring/whitespace-only values
remain rejected, with no default, omission or substitution. Duplicate names
are rejected with the SDK's case-insensitive comparator, and failed SDK
insertion cannot silently drop an entry.

The Python projector preserves input array order, every name/value and exact
boolean flag. It makes the same narrow empty-string exception; absent/null
values retain fixed sanitized failure categories. The exporter's mandatory
actual-Java-parser gate remains authoritative for complete fixture validation,
including SDK case aliases and identity-specific rules. The Python projection
helper alone is not presented as the full fixture validator. No Unicode name
normalization or approximate casefold was introduced.

Tests prove a six-entry fixture with two empty nonunique values survives into
the emitted foreign parent key with exact names/values/flags; array order is
retained until the SDK applies its documented sorting. Repeated collection
remains stable and additive. The descriptor, relationship implementation,
credential-free contract, file guards, no-overwrite behavior and secure cleanup
are unchanged. Real lab artifacts were not read or packaged.

## Independently rerun verification

| Check | Result |
|---|---|
| Focused Java | PASS: actual SDK null/empty/order/equality checks, six-entry exact roundtrip, 42 invalid-input lifecycle cases, 7 topology tests |
| Focused Python | PASS: 150 tests across lab probe, export, schema and diagnostics; actual Java parser exercised |
| Representation matrix | PASS: populated/empty/omitted/null with true and false flags, exact six-entry projection, identity-specific and case-alias rejection |
| `validate-sdk` | PASS: five runtime sources compile |
| Isolated development rebuild | PASS in scratch, explicit exact-reference structural gate |
| Exact candidate comparison | PASS, exit 0: **0 BLOCKING / 3 WARNING / 22 INFO** |
| Recursive archive integrity | PASS: 71 unpacked leaf paths/bytes identical between candidate and independent rebuild |
| Packaging exclusions | PASS: no SDK/vendor classes, test classes or compiled synthetic fixture; credential-free descriptor has required identType-2 field and no default or credential declaration/reference |
| Whitespace checks | PASS in factory and independent adapter |

Assessed candidate: `vcfcf_sdk_rdm_topology_poc.0.0.0.6.pak`, SHA-256
`0e77f1837cef68d6c40883fc5ff2359211307ef600940dd2ee140e25449aafc2`.
Independent scratch rebuild SHA-256:
`2991f0af008bdab9863bfe1fb95538fd5fd682b7e13453b0cff29e79171e07b4`.
Container timestamps differ; recursively unpacked payloads match. These are
local development artifacts, not published/reproducible release citations.
Build 5 remains unchanged at SHA-256
`7cfa0f9f829eade4bb6eaa3c0e5faf502b2bb288501b854e8c6cc3bcb0ebf9ae`.

Exact approved reference: Synology v1.0.0.30, SHA-256
`beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.
Both independent comparisons retained D8 (instance identifier count 1 vs 3),
D23 (traversal-kind count 0 vs 1), and D25 (absent traversal entries) warnings,
plus all 22 INFO findings. Nothing was suppressed or reclassified.

Existing test limitations remain explicit: SDK descriptor object loading is
SKIPPED without local log4j-api; DOM checks pass. Lifecycle tests bypass
appliance-only construction, not configuration/collector logic. The existing
javac source/target-11 warning remains. Compilation does not prove platform
acceptance, UI field roundtrip, failover or actual topology persistence.

## Registry and disposition

`knowledge/context/defects.md` was checked; no open defect affects this adapter
and no local override exists. No new implementation defect or registry closure
is proposed. The retained structural differences are the existing approved
comparator warnings, not new implementation findings.

**If used as-is:** a future separately authorized export can faithfully pass
explicit empty nonunique strings through the exact-key fixture; omitted/null
values still stop safely rather than being guessed or silently dropped.
READY for operator retry of the existing guarded read-only fixture capture;
actual lab contents and successful capture remain unverified by this review.
