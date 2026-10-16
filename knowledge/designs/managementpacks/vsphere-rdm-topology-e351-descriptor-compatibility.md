# E3.5.1 — CanonicalLun descriptor compatibility correction

## Observed failure and root cause

The operator reports that development build 8 failed installation with
`ResourceAttributeDescribe.load: Illegal symbols in attribute key: identity|format`,
followed by failed resource-kind/descriptor loading. Build 6 remains registered
in the UI; no live state was independently inspected or changed in E3.5.1.
The [E3.5 offline record](vsphere-rdm-topology-e35-canonical-lun-poc.md) describes
the earlier checks, not proof of successful installation.

All eleven new CanonicalLun attributes had the same defect: a full property
path was used as an individual `ResourceAttribute/@key`. The supplied legacy
SDK's `ResourceAttributeDescribe.isValidAttributeKey(String)` rejects either
reserved separator `|` or `:` in an individual key. Full runtime `MetricKey`
paths legitimately use group separators. Those are different contracts.
Working SDK descriptors use a `ResourceGroup` with unqualified attribute leaves.
The [SDK evidence and bounded guard](../../context/sdk-describe-key-contract.md)
records the exact classes, local SDK checksum and the same group-segment rule;
it imposes no guessed alphanumeric whitelist.

This was missed because previous DOM/compilation/package comparison checks did
not exercise this SDK semantic rule. The prior real descriptor-loader check
explicitly skipped unavailable log4j-api. Neither Java compilation nor a zero-
BLOCKING cross-adapter structural comparison proves platform descriptor loading.

## Minimal correction

Preserve every published full path and all identity/relationship behavior:

| Descriptor before (illegal flat leaf) | Descriptor after | Unchanged emitted full key |
|---|---|---|
| `identity\|format` | group `identity`, leaf `format` | `identity\|format` |
| `identity\|canonical_name` | group `identity`, leaf `canonical_name` | `identity\|canonical_name` |
| `identity\|provenance` | group `identity`, leaf `provenance` | `identity\|provenance` |
| `identity\|assessment` | group `identity`, leaf `assessment` | `identity\|assessment` |
| Seven `storage\|…` leaves | group `storage`, existing unqualified leaves | All seven `storage\|…` paths |

Storage leaves remain vendor, model, revision, serial_number, lun_type,
device_type and capacity_bytes. Existing attribute nameKeys and string-property
types remain. Group localization labels are added. No production Java property
rename is needed: the original composite emissions now match the hierarchy.

VM foreign key values/flags, scoped mapping tuple, unscoped LU NAA token,
qualification, build-6 fixture compatibility, credential-free configuration and
both additive SDK relationship paths must remain unchanged. Build 8 is retained
as a rejected artifact; the correction uses a distinct development build number.

Factory validation must check the SDK's general individual-key contract, not
special-case a resource kind or literal `identity|format`. This is bounded
SDK-semantic validation, not a claim of complete XSD/platform validation.

### Exact changed surfaces

- Independent adapter `describe.xml`: replace the eleven flat declarations with
  two noninstanced groups, `identity` (`nameKey=33`) and `storage` (`nameKey=34`),
  containing the same eleven leaves with only their prefix/separator removed.
  Leaf nameKeys remain 22–32, `dataType=string`, `isProperty=true`.
- `resources/resources.properties`: add labels 33 and 34 for those two groups.
- `adapter.yaml`: build number 8 → 9; changelog and generated version/reference/
  documentation surfaces updated. No release/CI policy changes.
- **No production Java changes** from build 8. Independently unpacked production
  class bytes are identical between the two PAKs, including identity and both
  relationship implementations. Fixture schemas are unchanged.
- Adapter descriptor regression tests compare all eleven reconstructed paths
  with the emitted property map and run the actual supplied SDK loaders against
  valid groups and illegal attribute/group keys. Two `tests/org/apache/logging/`
  API linkage shims supply only no-op logging; no descriptor logic is replaced.
  These test-only classes and synthetic fixtures are excluded from the PAK.
- Factory `src/vcfcf_managementpacks/sdk_builder.py`: add bounded XML segment
  checking to `validate_sdk_project` and direct `build_sdk_pak`, before compile,
  version stamping and packaging, after the existing release/warn-only policy
  guard. Buildkit already delegates to these functions. No comparator edits.
- `tests/managementpacks/test_sdk_describe_key_contract.py`: 26 cases covering
  pipe/colon rejection, groups/leaves, canonical/legacy namespaces, unaffected
  identifiers/extensions, valid characters, missing keys, malformed XML, CLI
  failure and direct build refusal before output generation.

## Offline candidate and validation

New local-only candidate:
`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.9.pak`.
SHA-256:

`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`

The rejected build-8 artifact remains unchanged, SHA-256
`de78efc3715244a1f2b101c721ff9ab70cdfd22a728cf84a9e4fca167e04d849`.
These are local development artifacts, not published releases or redistributable
SDK citations. Relevant findings are recorded here without raw lab data.

| Check | Result |
|---|---|
| Focused Java tests | PASS: 8 topology/descriptor tests, 42 invalid runtime cases, 34 invalid-LUN cases and existing positive/idempotence/convergence checks |
| Actual supplied SDK loaders | PASS: corrected hierarchy accepted; all 11 illegal flat leaves and colon/group negatives rejected; test-only logging shims, no loader skips |
| New factory guard tests | 26 passed |
| Wider SDK/framework tests | 336 passed / 8 skipped |
| Seven RDM probe/helper suites, actual SDK enabled | 319 passed / 1 skipped |
| Full factory suite, independent rerun | 2489 passed / 20 skipped / 131 deselected / 1 unchanged setup failure |
| validate-sdk / development build | PASS; six production sources compile, existing source/target-11 compiler warning remains |
| Package inspection | CRC passes; two legal groups/11 leaves; unchanged production bytecode and full property paths; only adapter/framework JARs; no proprietary SDK, logging shim, tests or fixture files |
| Approved structural comparison | 0 BLOCKING / 3 WARNING / 23 INFO, exit 0 |

Approved Synology v1.0.0.30 reference SHA-256 was verified:
`beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.
Warnings remain W1/D8 (one vs three adapter-instance identifiers), W2/D23
(zero vs one TraversalSpecKind), W3/D25 (empty vs populated TraversalSpecKinds).
INFO remains I1–I2 optional valid credential-contract differences, I3–I5 manifest
values, I6–I22 adapter-specific icons/JARs and I23 two-vs-nine data-kind count.
No suppression, waiver or reclassification was used. A passing comparator does
not itself check this newly enforced SDK key rule.

The full-suite failure remains
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
the test expects a no-repository verdict but receives conservative unknown. No
setup code/test was changed. Full content validation, skill parity, diff checks
and path-reference audit pass, with six documented standing path warnings.

[Independent framework review](../../context/reviews/framework/sdk-descriptor-keys-e351.md)
is APPROVE, zero outstanding findings. It caught and independently retested a
fixed release/warn-only error-precedence regression in the initial guard placement;
no tests or release controls were weakened. `.claude/`, immutable `reference/`,
CI configuration and repository boundaries remain unchanged; nothing staged.

[Independent SDK review](../../context/reviews/rdm-topology-poc-e351-build-9.md)
is also APPROVE, zero implementation findings. Its isolated rebuild matches all
73 recursively unpacked payload leaves; archive timestamps differ, so archive
bytes are not claimed reproducible. All 52 production class leaves are unchanged
from build 8. No open registry defects affect this adapter. **READY for a
separately authorized controlled upgrade retry**, not an installation-success
or live CanonicalLun topology claim.

## Controlled retry boundary

No retry is executed here. After separate explicit operator approval:

1. Verify the final corrected development artifact's recorded SHA-256. Do not
   retry build 8 or rebuild an artifact under its old version.
2. Capture the currently registered pack version, adapter status, existing VM
   and mapping counts/relationships privately. A failed update leaving build 6
   visible does not prove every installation stage was rolled back cleanly.
3. Use the same management-pack update UI and previously approved development
   unsigned-PAK option to upload the corrected artifact. Do not uninstall or
   delete the working build-6 adapter/resources. Do not change fixture settings
   as part of this descriptor-only retry.
4. Confirm installation completion and the new version in the repository; check
   analytics/collector logs for descriptor-load errors. If metadata registration
   still fails or existing topology changes unexpectedly, stop and preserve the
   logs. Do not repeatedly force installation or delete VMware resources.
5. Confirm existing build-6 mapping-only fixture behavior and topology remain.
   Supplying a qualified v2 fixture and testing the new local edge is a separate
   explicitly authorized experiment under the E3.5 procedure, not evidence
   established by this compatibility fix.

No live requests, installation, reconfiguration, topology changes, commits,
pushes, tags or publication are authorized by this record.
