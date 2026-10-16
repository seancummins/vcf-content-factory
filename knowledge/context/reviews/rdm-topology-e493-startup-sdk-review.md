# E4.9.3 cold-start follow-up — independent SDK review

**Final verdict: APPROVE the bounded offline build-13 development candidate; zero outstanding SDK code findings.** This is not installation approval or proof of the live account's root cause/recovery.

This follow-up preserves the original build-12 review as history. That candidate fixed a supported post-full-configuration partial-update defect, but it did not fix the distinct exact-empty-mode cold-start incompatibility established below. No claim of account-15903 live attribution or recovery is made.

## Independent SDK and packaged evidence

Authorities remain the SDK reviewer role, shared reviewer doctrine, SDK-adapter skill/playbook, RULE-001/005/007/008/012/014/015/016 and the authorized overnight handoff. This reviewer remains read-only on project source/tests/docs. All scratch output is under `/tmp`. No live APIs, `.env`, credential files, network, downloads, installation, commits or publication are authorized or used.

The genuine SDK `ResourceKindIdentifiers` implementation has a conditional identifier synchronization mechanism. A registered kind template is compared with a key's identifier count/key order/uniqueness flags. When those differ, synchronization preserves existing values by case-insensitive key name, rebuilds the identifier list from the template, and turns missing or null values into the literal empty string. It does not trim whitespace, choose execution modes, or use descriptor defaults. When no mismatch exists, null values remain null.

The reviewer independently compiled and ran the SDK contract probe using the actual SDK and the eight checksum-verified external libraries. It loaded the real combined descriptor with `AdapterDescribe.make`, constructed the template with genuine `ResourceIdentifierDescribe` metadata and registered it through the public SDK API. Observed results:

- Legacy fixture-only key: 1 identifier / mode absent becomes 12 identifiers / mode exact empty, with 11 empty fields.
- Fixture value is retained exactly; all 12 identifiers remain nonunique.
- An incomplete key with a raw-null mode also becomes exact empty when synchronization runs.
- Ordinary Java serialization preserves absent, empty and raw-null states independently; it does not cause the expansion.
- An empty `CredentialConfig` object survives serialization as a nonnull associated object, even with null kind/name and zero fields.
- Actual descriptor metadata: 12 optional fields, null defaults and nonunique identifier type 2.

The reviewer also independently ran the genuine original-fixture cache probe. Full legacy configure succeeded and retained 1 identifier / mode absent. After a later expanded incoming resource registered the 12-field template, calling the actual SDK-backed public `getMonitoringResource(legacyKey)` changed the lookup key to 12 identifiers / mode exact empty, returned the existing resource and retained the fixture value.

**Caller-chain limit:** actual SDK `AdapterCache` registers templates from incoming `ResourceConfig` keys. It does not load descriptor metadata itself. Known verification callers are key-based monitoring/stopped-resource lookups. The full configure chain updates/registers incoming settings and then invokes the adapter's configuration callback without calling the verifier. Thus this is a proven genuine SDK transformation and a supported representable carrier, but the installed collector's use of it before initial configure remains unobserved. A test explicitly applying that transformation cannot establish that live preprocessing occurred.

## Independent packaged cold-start matrix

The reviewer compiled the frozen `ColdStartMatrix` source (SHA-256 `0beea808bc55816ed2b7b15e903611e353bbb8e3d7e6e219ef2053760955c542`) independently and extracted adapter/framework/descriptor inputs directly from the preserved PAKs. Each PAK hash matched its previously recorded value. No source-built replacement, logging shim or synthetic platform class was on the execution classpath.

A total of **528 attempts** ran: 516 cold configurations (86 scenarios through no-argument and collector construction on each of builds 9, 11 and 12), plus 12 full-then-partial follow-ups. All three JVM processes exited 0. The harness records deliberate negative rejections and does not call them successful configurations. Independent TSVs are local scratch under `/tmp/rdm-e493-startup-sdk-matrix-mqvr5kvs/`; the findings are summarized here so those ephemeral files are not required as authoritative citations.

| Carrier supplied to cold configure | Build 9 | Build 11 | Build 12 |
|---|---|---|---|
| Legacy fixture only; mode absent | accepts, topology 1 | accepts, topology 1 | accepts, topology 1 |
| Explicit fixture mode | accepts, topology 1 | accepts, topology 1 | accepts, topology 1 |
| Genuine SDK-expanded 12-field legacy carrier; mode exact empty | accepts, topology 1 | rejects | rejects, `EXECUTION_MODE_EMPTY` |
| Raw exact-empty mode with valid fixture | accepts, topology 1 | rejects | rejects, `EXECUTION_MODE_EMPTY` |
| Raw-null mode | accepts, topology 1 | rejects | rejects, `EXECUTION_MODE_NULL` |
| Cold instance-less ID/UUID/key carrier | rejects | rejects | rejects, `DELTA_REQUIRES_ACTIVE_FIXTURE` |
| Valid full configuration followed by matching partial carrier | accepts and retains topology | rejects and retires topology | accepts and retains topology |

Raw legacy configuration remains mode-absent before and after configure on all three builds. The expanded empty carrier remains 12-field/empty before and after configure; the dispatcher does not perform that expansion. This separates the demonstrated cold-start incompatibility from build 12's post-full-config partial correction. Retained inventory on account 15903 remains insufficient proof of a new collection.

The matrix also re-confirms that a credential UUID without a hydrated target credential object was accepted on builds 9, 11 and 12 when mode was absent or exact fixture. Coordinator refinement preserves that existing policy: this fixture implementation does not consume the target credential reference. The newly accepted exact-empty form alone must reject a nonnull target credential UUID as well as the existing rejection of any credential object. This limits the new acceptance without an unrelated backward-incompatible policy change.

## Proposed correction assessment

An exact-empty mode may take the existing fixture-default path only after all existing kind, identifier, uniqueness, duplicate and unknown-field guards pass, with valid complete fixture JSON, all diagnostic fields absent/null/empty, and, for this newly accepted exact-empty form, no associated target credential object **or UUID**. Existing absent/exact-fixture UUID-only handling remains unchanged. This is a narrow restoration of a genuine SDK-representable legacy form. It does not justify whitespace/unknown/null mode acceptance, diagnostic fallback, dummy credentials, trust changes or incomplete cold configuration.

Raw-null mode remains rejected. A null transformed to exact empty by actual SDK synchronization is distinguishable only by its resulting carrier, so tests/docs must say which state is passed to the dispatcher. The dispatcher should neither mutate/normalize the input nor invoke the vendor verifier itself. Mode/owner latching, full-source mutation checks, diagnostic isolation and fixed rejection diagnostics must remain intact.

**Proposal-stage assessment: acceptable for implementation and regression qualification; final source/artifact qualification is recorded below.** Full factory-suite execution belongs to the independent framework reviewer; it is not silently claimed here.

All proprietary SDK/platform files and PAKs are external/local-only artifacts, not reproducible from factory Git and not redistributed. Relevant behavior and evidence are summarized in full above.

## Frozen follow-up source qualification

Initial source verdict: **APPROVE, zero SDK code findings**, pending final build-13 metadata/documentation and artifact checks. All six entries in the author's frozen manifest independently verify. Production dispatcher SHA-256 is `8abe662cbc06423c359b19cffffaa29fdc072e010f9e1bbe2642074ba5596260`.

The production diff from build 12 removes only the exact-empty-mode rejection, retains raw-null and unknown-mode failures, and permits empty to flow through the existing strict fixture path. The added credential-UUID condition and snapshot component are limited to the newly accepted exact-empty form; absent/exact-fixture historical policy remains intact. No input settings are rewritten, no vendor normalization is called by production dispatch, and no new mode, API, dependency, identity or publishing path is introduced. The now-obsolete private `EXECUTION_MODE_EMPTY` enum reason is removed; fixed reasons remain for real failures.

Independent genuine-SDK runner result: **exit 0; 325 partial-carrier/rejection assertions, 392 cold-start assertions, 343 prior dispatcher assertions, 3486 actual fixture lifecycle assertions across 6 scenarios and 4 routes**. The runner compiles with `--release 11 -proc:none`, uses only the supplied SDK/framework/eight verified platform JARs, and binds `ADAPTER_HOME` and `ALIVE_BASE` to a disposable `/tmp` test directory. It uses no logging/platform replacement or constructor bypass.

The six lifecycle scenarios are legacy mapping and version-2 LUN fixtures, each absent/default, exact fixture and genuine SDK-expanded exact-empty selection, through original/dispatcher and no-argument/collector construction. Discovery, repeated collections, same-full reconfigure, both partial setter overloads, monitoring stop/remove/restore, attribute-policy disable/restore, property behavior, identity/additive topology and stop/discard continue to pass. Cold tests assert input graph/value preservation, old UUID-only behavior, new empty+UUID rejection, UUID mutation retirement, and malformed/ambiguous/mixed configuration rejection.

Five genuine SDK logger errors reported that its root logger has no file appender; attempted paths were entirely beneath the disposable `/tmp` SDK base. These are recorded, not recast as a logging qualification pass. They did not cause failed configuration, missing classes or test failures. Appliance logging configuration remains outside this offline qualification.

## Final packaged build-13 qualification

Final SDK verdict: **APPROVE the bounded offline development candidate, 0 BLOCKING / 0 WARNING / 0 NIT code findings**. Reviewed final operator documents accurately separate the two demonstrated compatibility defects from unknown collector preprocessing/live attribution, preserve the scoped UUID policy, and state strict diagnostic, logging, trust and live-operation boundaries. The defect registry contains no open entry affecting this adapter; no closure or waiver is proposed.

The reviewer independently copied only required authorized build inputs to a temporary snapshot, then ran guarded `validate-sdk` and development `build-sdk`. Both compiled 22 production sources and verified the exact public controller/collector constructor ABI. The builder's explicit pinned structural gate passed; no project source or generated documentation was overwritten by the reviewer. Full build output, including every comparator finding, is retained locally under the scratch build root.

Independent artifact (local scratch):
`/tmp/rdm-e493-startup-sdk-build-363d8cex/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.13.pak`.
SHA-256: `dec9034ab493bfcb686a7362fcaf5e9c7772e7fb7136b779a87f7ef919f5d420`.

Final operator candidate:
`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.13.pak`.
Independently verified SHA-256:
`96d6293f3858bb13e625f52188b515d72e73c9f87ae46debd2ba7e50b30c68ae`.

The reviewer executed the packaged build-13 cold-start matrix against its independently built payload. This adds 176 attempts to the earlier 528, for **704 packaged attempts** across builds 9, 11, 12 and 13. Exactly ten outcomes change relative to build 12: five scenarios through each constructor (current/expanded-schema synchronization, synchronized incomplete raw-null input, raw exact-empty mode and all optional values empty) now accept and collect topology 1. The remaining **166 outcomes and before/after shapes are unchanged**, with zero unexpected changes. Cold acceptance is build 9: 144/172; builds 11 and 12: 66/172; build 13: 76/172. The four per-build full-then-partial sequences are counted separately from those cold denominators. Raw-null input that has not been vendor-transformed remains rejected.

Final-root PAK checks independently pass:

- Outer PAK, nested adapter ZIP, both JARs and packed overview archive CRC/integrity.
- All **126 recursively unpacked file contents** are byte-identical to the independently exercised build-13 payload.
- Archive entry order and primary metadata agree except **107 `date_time` entries**; nested archive CRC/size changes follow those timestamp bytes. The existing builder timestamp limitation remains explicit: **whole-PAK byte reproducibility is not claimed** and was not rewritten in this increment.
- Registration remains `ENTRYCLASS=com.vcfcf.adapters.rdmtopologypoc.RdmTopologyDispatcher`, `KINDKEY=vcfcf_rdm_topology_poc`.
- `javap -public -s` on the actual packaged entry JAR confirms public `()` and exact `(java.lang.String, java.lang.Integer)` constructors.
- Exactly two JARs ship: entry JAR and factory adapter-base JAR. No SDK/platform `com.vmware`/`com.integrien`, Apache library, test or lifecycle-probe classes ship.
- All 62 preexisting entry-JAR classes remain present. Relative to build 12, only `RdmTopologyDispatcher.class` and its private `$Reason.class` change; no new runtime class is added or removed.
- Descriptor bytes remain identical to build 12, SHA-256 `e2208997811428a5368fed66b5726986126092008d68f46a1a0275667e0251df`; framework JAR remains identical, SHA-256 `b13cdfa98d5a23b1daf85485320b505bc38ce7a8c5ac269065d4f934a950004b`.

Final-root `pak-compare`, independently rerun with explicit `structural/1` policy and the pinned approved Synology 1.0.0.30 reference SHA-256 `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`, exits 0: **0 BLOCKING / 4 WARNING / 21 INFO**. W1 credential fields 2 vs 5, W2 instance identifiers 12 vs 3, W3 traversal kinds 0 vs 1, and W4 empty vs populated traversal container remain unchanged. I1–I3 concern display/description/name, I4–I8 RDM-specific icons/JAR, I9–I20 reference-specific Synology icons/JAR, and I21 data-kind count 2 vs 9. No finding is suppressed or reclassified. These cross-product comparison differences are distinct from the zero code-review findings.

Preserved artifacts independently retain their hashes:

- Build 9: `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
- Build 10: `df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`.
- Build 11: `250d58894c624178863779f44d9fcea5a89c9f5e9774fa4b102251f0313392ce`.
- Build 12: `a6aac9b73aa28e1f1e2c91c3cf24f09899a259681fe60a8cfee3e464a77b9752`.

All six final source/test/runner freeze hashes were rechecked after final artifact review:

| File | SHA-256 |
|---|---|
| `RdmTopologyDispatcher.java` | `8abe662cbc06423c359b19cffffaa29fdc072e010f9e1bbe2642074ba5596260` |
| `E493ColdStartTest.java` | `b64ccb9cd720ed5e0d266623c50b1c3635fc97d1d4dcf4431d1ce34a8a744b61` |
| `E493DispatcherTest.java` | `5253191539bda3a9e21d66877b0a8526d4a9c9c5bd3324b269e8cdc95015d72d` |
| `DispatcherTest.java` | `c2f5c613944b3b9cfa8f8a3b2596651bcce4ac82d3cbd69919ff7881ed3cb00d` |
| `FixtureLifecycleProbe.java` | `8d460403df10bf8ba2103491b77997b0290dbe3a2784d981da524b00b083a351` |
| `run-dispatcher-tests.sh` | `98b1aa53fc98d70938bdc00b3cc70415e3faa42e30d7f3b779b536924e6e1612` |

## Remaining operational boundary

If shipped as-is, the reproduced SDK-expanded exact-empty legacy fixture carrier can cold-configure and collect, and build 12's validated partial-update handling remains intact. Ambiguous/diagnostic inputs do not gain fixture fallback or publication. Real collector startup, UI/DB conversion, managed credentials/trust, appliance logging and persistence remain unqualified.

Pending action: after separate explicit human authorization, checksum-verify the final candidate and perform a controlled same-kind retry on existing account 15903 without modifying its exact configuration/identities. Require fresh collection timestamps and exact topology/resource keys. Retained inventory alone proves nothing about new collection. If it still fails, capture only fixed reason plus sanitized callback shape/owner-agreement booleans and installed version/collector/time. Never send fixture contents, endpoint/UUID/credential values, tokens or raw exception payloads.

That live evidence/retry action was **not attempted** because it is outside the authorized offline scope. It remains pending human authorization, not denied or executed with an uncertain outcome. The SDK code review is complete; the coordinator's independent framework review owns complete factory-suite results and any preexisting unrelated failure. This verdict does not silently replace that gate.

```
SDK ADAPTER REVIEW
  adapter: content/sdk-adapters/rdm-topology-poc
  build reviewed: 13
  verdict: APPROVE (bounded offline development candidate)
  findings: 0 BLOCKING / 0 WARNING / 0 NIT code findings
  claims check: validate-sdk confirmed; independent build confirmed; pak-compare confirmed
  registry check: no open defect affects this pak; no closure proposed
  if shipped as-is: genuine SDK-expanded exact-empty fixture cold-start and validated partial updates work offline; live account15903 attribution/recovery remains unproven.
```
