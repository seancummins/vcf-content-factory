# E4.9.3 — Offline configuration compatibility result

> Historical build-12 result. The [build-13 cold-start follow-up](vsphere-rdm-topology-e493-startup-compatibility.md) adds a reproduced
> initial-configuration compatibility correction and complete factory-suite
> results. Its exact checksum is the current candidate. Statements below
> about blank-mode uncertainty and the unrun broader suite describe the
> earlier investigation. Stock validation would attempt dotenv discovery;
> no real .env existence or content was inspected.

## Disposition

A reviewed offline development candidate fixes a reproduced SDK compatibility
regression. **The exact cause of account 15903's 2026-10-16T02:57:22.346Z
failure, and its live recovery, remain unconfirmed.** No live infrastructure
was contacted or changed.

The full 280-line authorized overnight handoff was read from the supplied
Library attachment before development. Work stayed on outer branch
`feature/rdm-topology-mp` and the existing nested adapter branch `main`.
Existing unrelated modifications, old artifacts and both repositories'
branches were preserved. No commit, push, tag, merge, publication or install.

## Proven SDK defect and evidence

Build 11 assumed every `AdapterConfig` was a full instance snapshot.
The supplied genuine SDK deliberately supports both
`setAdapterInstResourceId(Integer, String)` and
`setAdapterInstResourceId(Integer, UUID, ResourceKey)` carriers with a null
instance `ResourceConfig`. `AdapterCache.update` retains the prior instance
and applies monitoring/stopped/removed-resource and attribute-policy deltas.
`AdapterBase.applyConfiguration` skips instance reconfiguration when the
instance resource is absent.

Independent actual-SDK before/after reproduction established:

| Route | Full configure | Matching partial configure | Subsequent fixture discovery |
|---|---|---|---|
| Original fixture adapter | succeeds | succeeds | present |
| Preserved build-11 dispatcher source | succeeds | fails, INVALID_CONFIGURATION | empty |
| Build-12 dispatcher | succeeds | succeeds | present |

Two independent SDK investigations reproduced the original divergence; the
SDK reviewer also reran the identical probe against the corrected source.
This proves a supported configuration-contract regression. It does **not**
prove that the failing live callback had this shape.

Blank/null `execution_mode` remains an alternative hypothesis. The SDK can
represent blank values and nonunique `updateValue(null)`, but the descriptor
has no defaults and no evidence establishes the collector's actual serialized
values. Acceptance was therefore not loosened.

SDK/platform dependencies are proprietary local-only inputs and are not
reproducible from factory Git; findings are summarized here in full.
SDK SHA-256 is
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
All eight external dependencies match the supplied SHA256SUMS manifest.
No proprietary dependency was added to source, Git or the PAK.

## Minimal correction

Only the active fixture route accepts matching partial configuration.
It retains and checks the validated full configuration before and after
forwarding the exact incoming delta to the original SDK delegate.
Adapter kind and ID must match; supplied UUID/key must agree.
Cold, stopped, retired, diagnostic and conflicting-owner updates fail closed.
Credential, custom and extended/trust deltas are rejected rather than silently
claiming they were applied. No mode or configuration is synthesized.

Configuration rejection retains the existing INVALID_CONFIGURATION prefix
and appends a fixed reason code. Reasons distinguish owner/carrier/identifier,
null/empty/unknown mode, fixture/mixed settings, delegate and linkage failures.
No input values, exception text, credentials or dynamic class names enter
these statuses.

Both public constructors, including exact `(String, Integer)`, remain.
The descriptor, single adapter kind, resource identifiers, mapping/LUN keys
and additive relationship logic remain unchanged. Diagnostic mode still
publishes zero resources, relationships, metrics, properties and events.

Eight authored paths in the nested adapter:
dispatcher; DispatcherTest; new E493DispatcherTest; FixtureLifecycleProbe;
adapter.yaml (11 to 12); CHANGELOG.md; docs/same-kind-diagnostic.md;
new docs/configuration-compatibility-e493.md.
The ordinary build also regenerated its existing generated documentation.
No E4.9.3 framework source edit was needed.

## Actual offline validation

| Check | Result |
|---|---|
| New real-SDK carrier/rejection regression matrix | PASS, 336 assertions |
| Existing dispatcher/reflection/diagnostic-isolation matrix | PASS, 348 assertions |
| Genuine SDK fixture lifecycle, no platform/logging substitutes | PASS, 2324 assertions; 4 fixture scenarios across 4 routes |
| Diagnostic coordinator and SOAP framing, genuine SDK/no network | PASS, 243 + 22 assertions |
| Operations provider / discovery / runtime binding | PASS, 281 / 54 / 62 assertions |
| Existing limited fixture/LUN/topology suites | PASS; 42 invalid fixture cases, 34 invalid LUN cases, 8 topology/descriptor tests plus positive matrices |
| Descriptor dependency guards | PASS, 15 tests |
| Actual combined descriptor load | PASS, 3 resource kinds / 1 credential kind |
| Historical separate diagnostic descriptor load | PASS, 1 resource kind / 1 credential kind |
| validate-sdk and build compilation | PASS, 22 production sources; both exact constructor ABIs verified by javap |
| Independent management-pack factory suite | 339 passed / 8 skipped |
| Guarded full content validation equivalent | PASS, all seven content validators and seven Tier 2 projects |
| Skill parity / path audit / whitespace | PASS; standing-exception path warnings retained |
| Explicit pinned structural comparison | PASS, 0 BLOCKING / 4 WARNING / 21 INFO |

The real lifecycle checks include both partial setter APIs, repeated
collections, monitoring/stop/remove/restore and property-policy disable/restore.
They compare original and dispatcher routes, default/explicit fixture modes,
legacy/version-2 fixtures, exact foreign VM and owned resource keys, additive
edges, initial properties, retained full configuration and stop/discard.
Old constructor-bypass/logging-linked tests are supplementary only; they are
not the evidence for the complete fixture lifecycle.

The stock preflight/doctor and unmodified full content-validation script were
not run because they read .env. The independent validation harness disabled
only credential loading, invoked the real seven stock validators, and refused
credential-file opens, networking and repository writes. The changed-content
hook was invoked for adapter.yaml; SDK paths intentionally skip that hook,
so actual SDK validation is the substantive gate.

Existing source/target-11 module-path and deprecated-API compiler warnings
remain. Network/TLS integration tests were not executed. No unqualified
certificate/decryption/JWT dependency branch is claimed as exercised.

No broader factory-suite green claim is made. E4.9.2 documented the unchanged
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`
failure; it was not modified or rerun here.

## Independent review and artifact

SDK, security and framework reviews independently APPROVE with zero new
BLOCKING, WARNING or NIT findings. The SDK/security reviewers reproduced the
actual SDK matrices. Framework source hashes match the E4.9.2 reviewed state.
No open defect-registry entry names this RDM adapter.

- [SDK review](../../context/reviews/rdm-topology-e493-sdk-review.md)
- [Security review](../../context/reviews/rdm-topology-e493-security-review.md)
- [Framework review](../../context/reviews/framework/rdm-configuration-e493.md)
- [Adapter evidence and controlled retry](../../../content/sdk-adapters/rdm-topology-poc/docs/configuration-compatibility-e493.md)

Development candidate:
`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.12.pak`

SHA-256:
`a6aac9b73aa28e1f1e2c91c3cf24f09899a259681fe60a8cfee3e464a77b9752`

The pinned independently approved Synology 1.0.0.30 structural reference is
SHA-256 `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.
Four existing comparison warnings are retained without suppression:
credential-field count 2/5, instance-identifier count 12/3,
traversal-kind count 0/1, and empty versus populated traversal kinds.
The 21 INFO findings remain metadata, icon/JAR and data-kind-count differences.

Both ZIP layers and both embedded JARs independently pass integrity checks.
Only the entry JAR and factory base JAR are packaged; SDK/platform/test/native
payloads are excluded. Descriptor and framework bytes match build 11. Of the
60 previous entry-JAR classes, only the dispatcher changes; its two private
Reason/Rejected helper classes are added and the other 59 remain identical.

The independent SDK review also rebuilds the candidate offline in a temporary
copy. All 126 recursively extracted payloads match byte-for-byte. The whole
PAK checksum differs because the existing builder records archive timestamps;
byte-reproducible archive output is therefore not claimed. This is an existing
toolchain limitation, not a reason to broaden this adapter correction into a
framework packaging change. The operator must use the exact candidate hash
recorded above, not the independent rebuild's hash.

The independent rebuild is SHA-256
`6ca77d5d5ab452b9a2a8ff82c430ad80eec6cf7a6ac754a3f13a447f866e94e9`.
Archive ordering/comments/extra fields/flags/attributes/compression metadata
match; 107 ZIP date_time entries differ, with nested CRC/size differences
following the changed timestamp bytes. All extracted leaf content matches.

Preserved earlier PAK hashes:
- Build 9: `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`
- Build 10: `df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`
- Build 11: `250d58894c624178863779f44d9fcea5a89c9f5e9774fa4b102251f0313392ce`

The candidate is a local development preview, not a CI release. The independent
adapter working tree and external proprietary inputs are needed to reproduce
it; factory Git alone is insufficient.

## Exact next human action and remaining blocker

The live-attribution portion is **pending evidence/authorization**, not denied.
The supplied generic status does not expose the failing callback or field.

If already captured, supply only the sanitized callback shape: full instance
resource present/absent; identifier key names, uniqueness flags and
absent/null/empty/populated value categories; credential/custom/extended-config
presence; and ID/UUID/key match booleans. Include installed version, callback
time and collector placement. Exclude fixture contents, endpoints, credential
or UUID values, tokens and raw exception payloads.

Otherwise, the next operational decision is explicit approval for a controlled
development-lab upgrade/retry of this checksum-verified build 12, retaining
account 15903 and its exact configuration and identity. Follow the supported
platform upgrade process; preserve the prior PAKs and private baseline.
Do not uninstall, recreate the account, edit mode/fixture/credentials, restart
collectors, delete inventory or weaken trust to test the candidate.

Require a new timestamped collection and unchanged exact keys/additive
relationships over repeated cycles. The retained ubuntu2404 to mapping 2001
edge alone is no proof of new collection. If configuration still fails, stop
the retry and return the fixed reason plus sanitized shape; do not speculatively
clear or re-save optional settings. Diagnostic execution is separately
authorized and remains disarmed.

UI serialization, collector routing/upgrade, credential injection, managed
trust delivery and live topology persistence remain unqualified. This record
authorizes no live action.

