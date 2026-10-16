# E4.9.3 cold configuration SDK evidence

Read-only api-cartographer investigation, 2026-10-16. Local-only proprietary SDK
SHA256 2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54.
All eight supplied external descriptor libraries matched their SHA256SUMS.
No live connection, environment/credential read, repository edit, or PAK change.

## Proven normalization mechanism

`ResourceKindIdentifiers.addResourceKindIdentifiers(template)` records the
ResourceKey identifier list for adapter-kind/resource-kind (case-insensitive
TreeMaps). `verifyResourceIdentifiers(key)` compares identifier count and each
case-insensitive key/uniqueness position. On mismatch,
`synchronizeResourceIdentifiers` builds a case-insensitive map of old values,
clears the key, and adds identifiers for the registered template. Old values
are retained; missing OR null values become literal `""`; template key names and
uniqueness flags are used. Template values and descriptor defaults are unused.
If no template exists, it returns true without expansion. If no mismatch exists,
a null value is not changed. The method does not trim whitespace or select modes.

`/tmp/E493ColdCarrierProbe.java` loads the actual combined describe through
`AdapterDescribe.make(InputStream)`, maps its identifiers to a template with
actual `ResourceIdentifierConfig(key,"",identType)` calls, registers the template,
and passes a legacy fixture_json-only key through the genuine SDK verifier.
Results:

- absent mode -> EMPTY; identifiers 1 -> 12; 11 empty fields;
- explicit null mode with incomplete schema -> EMPTY;
- fixture value preserved and all 12 flags nonunique;
- Java ObjectOutputStream/ObjectInputStream alone preserves ABSENT/EMPTY/NULL,
  id/UUID and credential absence exactly;
- empty CredentialConfig remains nonnull, with null name/key and zero fields;
- all 12 descriptor fields: isRequired false, getDefaultValue null, identType 2.

Repeat with `bash /tmp/run-E493ColdCarrierProbe.sh` (explicit eight-library
classpath, no wildcard, downloads or hidden platform shims).

## Caller chain and cold-start boundary

Known SDK registration: AdapterBase.configure -> applyConfiguration ->
AdapterCache.update -> addResourceKind ->
ResourceKindIdentifiers.addOrUpdateResourceKindIdentifiers(incomingResourceKey).
Registration uses incoming account/monitoring/stopped resource keys, never an
AdapterDescribe. AdapterCache contains no descriptor references.

Known SDK normalization calls: AdapterCache.getMonitoringResource(ResourceKey)
and getStoppedResource(ResourceKey) -> verifyResourceIdentifiers -> sync.
AdapterBase key lookups and AdapterCache key-based metric checks can reach those.

The full instance configure path is update/register -> initTrust ->
configureBase(ResourceStatus,ResourceConfig) -> VcfCfAdapter.onConfigure ->
RdmTopologyPocAdapter.configureAdapter. It does not call verifyResourceIdentifiers.
ResourceStatus construction reads id/name/interval; it does not change identifiers.
The original fixture parser reads exactly one nonunique fixture_json and ignores
other identifiers and credential carrier fields.

`/tmp/E493CacheNormalizationProbe.java` exercises actual public original-adapter
calls with the genuine SDK and eight libraries, no shims/constructor bypass:

`cold_status=as_succeeded cold_after_count=1 cold_after_mode=ABSENT
expanded_status=as_succeeded lookup_before=1 lookup_after=12 lookup_mode=EMPTY
found=true fixture_preserved=true`.

Thus the verifier is an actual SDK mechanism capable of the hypothesized shape;
its preconfigure use by the deployed collector is not established. The supplied
SDK/libraries do not include an identified UI/DB-to-AdapterConfig converter.
All eight libraries have no bytecode references to AdapterConfig, ResourceConfig,
or ResourceIdentifierConfig. Relevant SDK classes expose no readObject/writeObject,
readResolve/writeReplace hooks. ConfigBase is Serializable only. The SDK has no
isValueRequired symbol; the actual descriptor accessor is isRequired().

## Evidence matrix

| Candidate | Classification | Evidence / limit |
|---|---|---|
| Dispatcher rejects cold legacy full config with execution_mode empty/null | Proven code-level incompatibility | Original fixture ignores these optional fields; build 11/12 selection rejects them before constructing fixture. Packaged cross-build probe belongs to adapter author. |
| SDK can add empty new optional fields to a legacy key | Proven conditional mechanism | Actual ResourceKindIdentifiers verifier plus loaded combined descriptor, 1 -> 12 fields. |
| Installed collector used that transform before failed initial configure | Possible, unobserved | No captured callback shape or matching collector converter provided. |
| Java default serialization turns absent mode into blank/null | Ruled out on exercised carriers | Genuine roundtrip preserves all three states; no carrier hooks. |
| Descriptor parsing itself creates persisted config values | Ruled out in supplied SDK path | Descriptor only stores metadata; no AdapterConfig/ResourceConfig builder. |
| Fixture.configure internally expands initial omitted mode | Ruled out on exercised original path | Cold configure preserves count1/modeABSENT; bytecode has no verifier call on configure chain. |
| Blank optional diagnostic fields alone activate diagnostic route | Ruled out by dispatcher selection | Only exact read_only_diagnostic can choose diagnostic; empty/null ordinary fields remain neutral. |
| Empty resource credential is generated from absent optional credential | Possible carrier, no generation evidence | New CredentialConfig can be empty and persists through serialization; SDK ResourceConfig defaults credential null and never creates it. |
| Collector constructor/config resource ID mismatch | Possible rejection, not observed | Integer constructor value initializes logger context; configured id comes from ResourceConfig; SDK has no equality guarantee. Preserve E492 guard absent evidence. |
| Incremental instance-less update explains initial callback failure | Unproven initial cause | Confirmed post-full-config compatibility gap only; cold original base also lacks cached instance and fails. |
| Unknown/whitespace/duplicate/unique mode should become fixture | Unsupported | Normalizer emits exact empty only; strict rejection remains defensible. |

## Correction boundary supported offline

An exact-empty mode can be treated as the legacy default only when there is one
complete valid nonunique fixture, no populated diagnostic fields, no resource
credential, and all existing kind/identity/unknown/duplicate constraints pass.
This restores a real SDK-representable schema-expansion form. Null mode is also
a supported carrier state through update/list/serialization but the verifier
usually changes missing/null to empty when schema expansion runs; accepting it
requires the same exclusive fixture conditions, not an implicit diagnostic route.
No evidence warrants unknown/whitespace/duplicate/unique mode leniency, dummy
credentials, trust changes, fallback after diagnostic failure, or a second kind.

A corrected passing offline candidate is not evidence of live recovery of 15903.
Retain fixed rejection codes for the next separately authorized controlled retry.
Smallest missing evidence: sanitized initial-callback shape/reason code, or the
matching installed collector method that builds ResourceConfig from persisted
account/descriptor fields. Fixture JSON, endpoint strings and secrets are not
needed to establish that shape.
