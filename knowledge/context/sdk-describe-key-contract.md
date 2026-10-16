# SDK descriptor key segments versus runtime MetricKeys

E3.5.1 finding: the operator reported that the development build-8 descriptor
failed installation with `Illegal symbols in attribute key: identity|format`.
This is a descriptor-load failure, not evidence against the qualified LUN
identity, ResourceKey, or additive relationship mechanisms.

## Evidence and bounded rule

The locally authorized Broadcom SDK JAR has SHA-256
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
It is proprietary, local-only, not redistributable and not reproducible from
Git; the relevant findings are summarized here in full. Offline `javap -c -p`
inspection establishes:

- `com.integrien.alive.common.adapter3.describe.ResourceAttributeDescribe.load`
  rejects an absent `key`, calls its private `isValidAttributeKey(String)` and
  returns false for an invalid result.
- `ResourceAttributeDescribe.isValidAttributeKey(String)` rejects any value
  containing `|` or `:`. It imposes no alphanumeric-only whitelist.
- `com.integrien.alive.common.adapter3.describe.ResourceGroupDescribe.load`
  and `isValidGroupKey(String)` apply the same missing-key and reserved-character
  checks to group segments.

These are **bounded runtime descriptor-loader checks**, not a claim that every
describeSchema XSD or Operations installation constraint has been validated.
In particular, this rule does not validate localization, all attribute types,
descriptor ordering, or live controller registration.

## Correct representation

A descriptor declares a `ResourceGroup key="identity"` containing a
`ResourceAttribute key="format"`. Java emits the fully qualified runtime
`MetricKey(true, "identity|format")`. The runtime separator is legitimate;
putting that composite path into one descriptor attribute's `key` is not.
Nested groups use additional separate segments in the same manner.

Working factory examples are emitted by
`src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/describe/DescribeBuilder.java`
and `src/vcfcf_managementpacks/builder.py`: groups and leaf attributes are
distinct XML elements. Advice that pipe characters are safe in Tier 2 runtime
metric/property keys must not be applied to descriptor segment declarations.

## Factory guard and compatibility

`src/vcfcf_managementpacks/sdk_builder.py` now checks ResourceGroup and
ResourceAttribute declarations in the standard SDK namespace or legacy
namespace-free descriptors. It does not apply this rule to ResourceIdentifier,
TraversalSpec, foreign XML extension elements, or runtime MetricKey strings.
Malformed/unreadable XML fails the guard rather than silently passing.

The guard runs in `validate-sdk` and direct `build-sdk` before compilation and
packaging; buildkit delegates to these same functions. No comparator rules or
finding severities change. A formerly accepted descriptor containing a reserved
separator now fails locally, matching the documented live rejection instead of
producing another uninstallable PAK.

Deterministic coverage lives in
`tests/managementpacks/test_sdk_describe_key_contract.py` and checks both reserved
characters, nested valid groups, namespace handling, unrelated keys, missing
keys, malformed XML, absence of an invented whitelist, CLI failure, and direct
build fail-closed behavior before generated output.
