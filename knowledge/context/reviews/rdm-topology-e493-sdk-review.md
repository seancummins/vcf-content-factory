# E4.9.3 — Independent SDK adapter and artifact review

**Verdict: APPROVE the bounded offline build-12 candidate. Zero outstanding SDK code findings.** This approves neither installation nor a claim that account 15903 has recovered. Its actual failing configure callback was not supplied, so the live root cause remains unconfirmed.

If shipped as-is, matching SDK partial updates preserve an already validated active fixture route and configuration failures provide fixed reason codes; cold, stopped, retired, diagnostic and conflicting-owner partial updates remain closed. Existing collector constructors, resource identities, additive topology and diagnostic zero publication are retained. The operator must still authorize and verify a controlled live retry.

Authorities: `.claude/agents/sdk-adapter-reviewer.md`, shared reviewer doctrine, `.agents/skills/vcfops-sdk-adapter/SKILL.md` and its complete playbook, the actual SDK callback contract, RULE-005/007/008/012/014/015/016, E4.9.1/E4.9.2 records and the full authorized overnight handoff. The defect registry was checked: no open `Affects:` entry targets `rdm-topology-poc` or this management pack. No closure, waiver or comparator-policy change is proposed.

The reviewer changed no project source, tests, descriptor or documentation. Compilation, independent packaging and report scratch output stayed under `/tmp`; no live service, credentials, `.env`, download, installation, commit or publication was used. Guarded Python CLI executions disabled dotenv loading and rejected credential-file/network access; independent build writes were confined to `/tmp`.

## Independently established defect and correction

Actual SDK bytecode establishes that both `AdapterConfig.setAdapterInstResourceId(Integer, String)` and `(Integer, UUID, ResourceKey)` deliberately remove the instance `ResourceConfig` while retaining owner identification. `AdapterCache.update` replaces cached instance settings/credentials/custom configuration only when an incoming instance resource exists, and otherwise can apply monitoring, stopped/removed-resource and attribute-policy changes. `AdapterBase.applyConfiguration` skips the instance `onConfigure` invocation for such an update while retaining cached instance configuration.

The reviewer independently compiled the preserved pre-edit dispatcher and the frozen candidate against the genuine SDK/framework and eight verified external platform libraries, and ran the same partial-carrier probe against each:

| Route | Full configure | Matching partial configure | Subsequent fixture collection |
|---|---|---|---|
| Original fixture adapter | succeeded | succeeded | discovery payload present |
| Build-11 dispatcher | succeeded | failed, `RDM_DISPATCHER INVALID_CONFIGURATION` | empty |
| Frozen build-12 dispatcher | succeeded | succeeded | discovery payload present |

This proves a specific dispatcher compatibility regression. The account-15903 log at `2026-10-16T02:57:22.346Z` does not reveal its incoming callback shape or rejection phase; it cannot prove that this particular defect caused the live failure. Blank/null optional-mode serialization also remains unproven.

The production correction is confined to `RdmTopologyDispatcher.java`. `configureFixtureDelta` forwards the unchanged SDK carrier only after checking active fixture state and matching adapter kind/instance ID, with supplied UUID/key confirmation. It preserves the last validated full source and checks it before and after delegation. Incoming credentials, custom configuration and extended/trust updates are rejected; there is no implied mode/credential/trust update. Invalid or failed delegates retire the route. Partial input cannot initialize the fixture or choose diagnostic mode.

The actual SDK's `ResourceKey.equals` compares kinds case-insensitively and, when no identifiers are uniqueness-bearing, compares resource name; nonunique fixture/mode settings are not key identity. This is used only for owner-key confirmation. The partial carrier's key does not replace the retained instance settings or select a mode. Full-source identifier mutations remain fenced. Absent mode still selects fixture; explicit blank/null/unknown/duplicate mode remains rejected.

Fixed rejection reasons come from a private enum. Runtime/SDK exception messages, dynamic class names, input values and credential values are not copied into the dispatcher rejection status. The public no-argument and exact boxed `(String, Integer)` constructors remain available and fixture initialization stays lazy. Diagnostic execution still does not construct the fixture base or populate SDK publication carriers.

## Independent qualification

All checks below actually ran in this review:

| Check | Result |
|---|---|
| Eight external dependency `SHA256SUMS` entries | all verify |
| Preserved pre-edit vs frozen-candidate SDK partial probe | reproduced before/after behavior above, exit 0 |
| `run-dispatcher-tests.sh --fixture-lifecycle` | exit 0: 336 E493 carrier/reason assertions, 348 existing dispatcher assertions, 2324 actual fixture lifecycle assertions |
| Actual combined descriptor loader | exit 0: 3 resource kinds, 1 credential kind |
| Guarded `validate-sdk` on source and independent snapshot | exit 0: 22 production sources compile, exact public controller/collector ABI verified |
| Independent snapshot `build-sdk` | development version `0.0.0.12`, exit 0, pinned structural comparison passes |
| Final root PAK independently compared against pinned reference | exit 0: 0 BLOCKING / 4 WARNING / 21 INFO |
| Final PAK/inner ZIP/two embedded JAR CRC checks | pass |
| Packaged dispatcher `javap -public -s` | exact public `()` and `(java.lang.String, java.lang.Integer)` constructors |
| Independent rebuild vs final root PAK | all 126 recursively unpacked archive leaf contents byte-identical |
| Build-11 vs build-12 executable/descriptor scope | only existing dispatcher class changes; two new reason/rejection helper classes; descriptor/framework JAR identical |

The four actual fixture scenarios cover legacy mapping-only and version-2 LUN fixtures, each absent/default or explicit fixture selection, on four routes: original/dispatcher and no-argument/collector construction. Each exercises discover/collect/repeat/reconfigure, both partial setter forms, monitoring updates, stop/remove/restore, attribute-policy disable/restore, full-instance retention, stable resource/relationship keys, additive edges, initial properties and stop/discard. Reflection introspection confirms genuine SDK constructor logging initialization; it does not replace lifecycle execution. No logging/platform shim or synthetic publishing delegate is used in that lifecycle proof. Delegate-seam tests are clearly supplementary and cover stale-source mutation during delegation, failing statuses/exceptions, malformed configuration, owner checks, diagnostic rejection and zero SDK publication payloads.

Compiler output retains the existing source/target-11 system-module warning and deprecated-API notices. The test runner itself uses `--release 11 -proc:none`. Unexercised platform certificate/decryption branches and actual injected-credential/collector/UI behavior are not qualified here. The independent framework reviewer owns the wider factory suite and its preexisting unrelated failure; this SDK review does not claim that suite was entirely green.

## Frozen source and final artifact

Frozen production source SHA-256:
`3f465fd6abfe9c910fed7a55f0764ee271ec2ccad4dc6942d28bbb480ae798ba`.

Test SHA-256:

- `E493DispatcherTest.java`: `9fa5242bd47dc4ffccbaf2a3945f6da07a2079f9c812deb35a3a8d8e516b57ec`.
- `DispatcherTest.java`: `c1e97ff384a6dd83eac697de58f29c874f7b3ef068af483845ce2b9c78d59cfb`.
- `FixtureLifecycleProbe.java`: `1bf56567fab5910c8fef3d6d64443234ebc995ccbf443d2ef4af9e37c73b921d`.

Final operator candidate:
`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.12.pak`.

Independently verified SHA-256:
`a6aac9b73aa28e1f1e2c91c3cf24f09899a259681fe60a8cfee3e464a77b9752`.

The independent scratch build's SHA-256 is
`6ca77d5d5ab452b9a2a8ff82c430ad80eec6cf7a6ac754a3f13a447f866e94e9`.
Independent artifact scratch path: `/tmp/rdm-e493-sdk-review-build-t_o2tuvm/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.12.pak` (local-only).

Archive timestamps differ, so a byte-for-byte whole-PAK reproduction is **not** claimed. Recursive ZIP metadata comparison found 107 differing `date_time` entries and no differences in archive order, comments, extra fields, creator/extractor versions, flags, volume, attributes or compression method; nested archive CRC/size differences follow from the changed timestamp bytes. Every actual file inside all nested ZIP/JAR/packed archives matches, including class files and metadata. This is an existing builder timestamp/reproducibility limitation, not a new adapter change; no unrelated tooling rewrite was attempted.

Registration remains `ENTRYCLASS=com.vcfcf.adapters.rdmtopologypoc.RdmTopologyDispatcher` and `KINDKEY=vcfcf_rdm_topology_poc`. Exactly the entry JAR and `vcfcf-adapter-base.jar` ship. No proprietary SDK/platform `com.vmware`/`com.integrien`, Apache dependency, test or lifecycle-probe classes are present. Among 60 existing entry-JAR classes from build 11, only `RdmTopologyDispatcher.class` changes; `$Reason` and `$Rejected` are new. Descriptor SHA-256 remains `e2208997811428a5368fed66b5726986126092008d68f46a1a0275667e0251df`; framework JAR SHA-256 remains `b13cdfa98d5a23b1daf85485320b505bc38ce7a8c5ac269065d4f934a950004b`.

Preserved prior PAK SHA-256 values independently verify:

- Build 9: `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
- Build 10: `df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`.
- Build 11: `250d58894c624178863779f44d9fcea5a89c9f5e9774fa4b102251f0313392ce`.

The explicit approved Synology `1.0.0.30` structural reference has SHA-256 `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`. All comparator findings are preserved: W1 credential-field count 2 vs 5; W2 instance identifiers 12 vs 3; W3 traversal-kind count 0 vs 1; W4 empty vs populated traversal container. I1–I3 concern description/display/name; I4–I8 RDM icons/JAR additions; I9–I20 reference Synology icons/JAR absences; I21 data-kind count 2 vs 9. None was suppressed or reclassified. These cross-product differences are separate from this review's zero code findings.

All proprietary SDK/platform binaries and development/scratch PAKs are local-only artifacts, not published or reproducible from factory Git alone; their relevant findings and hashes are summarized here rather than redistributing binaries. No release approval is implied.

## Remaining live evidence and operator action

Review of the frozen E493 operator document confirms that it states the actual bounds and preserves strict mode/security policies. The remaining evidence action is to determine the failing account's callback shape and verify fresh collections after a separately authorized, checksum-verified controlled same-kind upgrade. Target: existing account 15903, with exact account/mode/fixture/credentials/identities preserved. This live action was **not attempted** and remains pending human authorization; it was not denied or executed with an uncertain outcome.

If the retry still fails, obtain only the fixed reason code plus sanitized shape: instance resource present/absent; identifier names/uniqueness flags and absent/null/empty/populated states; presence of credential/custom/extended carriers; owner ID/UUID/key agreement booleans; installed version/collector/time. Do not collect raw fixture, endpoint, identity or credential values. An initial partial update before any valid full fixture configuration remains correctly rejected. Retained `ubuntu2404 → mapping 2001` inventory is insufficient evidence of a successful new collection.

```
SDK ADAPTER REVIEW
  adapter: content/sdk-adapters/rdm-topology-poc
  build reviewed: 12
  verdict: APPROVE (bounded offline development candidate)
  findings: 0 BLOCKING / 0 WARNING / 0 NIT
  claims check: validate-sdk confirmed; independent build confirmed; pak-compare confirmed
  registry check: no open defect affects this pak; no closure proposed
  if shipped as-is: supported active-fixture SDK deltas continue collection with sanitized rejection diagnostics; actual account15903 recovery remains unverified.
```
