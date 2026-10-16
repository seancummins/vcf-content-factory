# Content Factory next work — offline assessment, 2026-10-16

## Recommendation

After the bounded test cleanup below, the highest-value next **offline
development task is DEF-019: make view extraction and reverse conversion
preserve the source's subject filters and instanced property members**.
It fixes silent semantic loss in an existing workflow and in the shared
`vcfcf_core` library. It does not require a new widget or product feature.

The highest-value next **operator action** is separate: a specifically
approved, controlled build-13 retry on existing RDM account 15903, or an
already captured sanitized failing callback. The offline candidate does
not establish the live cause or recovery. Keep build 13 frozen until that
evidence identifies a defect; another speculative build adds little value.

This assessment uses the local working tree on `feature/rdm-topology-mp`,
the governance corpus, existing reports, source and tests. It uses no live
service, remote issue tracker, credential file or dependency download.
Issue/registry states below are the local recorded states, not a claim of
fresh remote verification. Recommendations are not authorization to modify
another adapter repository, install, publish or resume a parked line.

## What the roadmap had wrong

| Earlier statement | Current repository evidence | Consequence |
|---|---|---|
| Java SDK adapters are future work | [Tier 2 architecture](../context/tier2_architecture.md), [managed registry](../context/managed_paks.md), Java builder and RDM reviewed artifacts already exist | Improve qualification and existing adapters before adding another build path |
| PropertyList and ResourceRelationshipAdvanced are missing | Both are accepted in [dashboard loader](../../src/vcfcf_core/dashboards/loader.py) and emitted in [renderer](../../src/vcfcf_core/dashboards/render.py) | Do not implement them again; SparklineChart is still outside the accepted type set |
| There are zero automated tests and CI is future work | [Test conventions](../../tests/README.md), [CI workflow](../../.github/workflows/ci.yml), and [actual full-suite review](../context/reviews/framework/rdm-e493-full-suite.md) | Improve repeatability and isolation, rather than create a duplicate test pipeline |
| Named profiles are future work | [Profile resolver](../../src/vcfcf_common/_env.py) already implements named prod/qa/devel profiles | Distinguish future multi-target orchestration from existing profile selection |
| Packaging SDK-pointer crash still requires the original code fix | DEF-017/FB-018 remain open, but [_build_release_to_dist](../../src/vcfcf_packaging/cli.py) already branches on `art.is_sdk_pointer` | Verify regression coverage and propose evidence-backed registry reconciliation before reimplementing |
| Version-line guard is entirely absent | [version_line_guard.sh](../../scripts/version_line_guard.sh) already refuses a tagged 0.x line and checks tag commits | FB-008's stronger exact tag/version equality promise still needs separate verification; existence is not full completion |

The roadmap is reconciled to these capability facts. The widget section of
[known limitations](../context/known_limitations.md) is corrected as well.
Other old backlog entries are not silently declared complete.

## Prioritized work

| Priority / work | Achievable acceptance criteria | Dependencies and approval boundary | Risk / scope control |
|---|---|---|---|
| P0 operational: qualify RDM build 13 | Verify exact PAK hash and installed version; preserve account/configuration/identities; obtain fresh repeated collection timestamps, exact resource keys/counts and additive edges, or fixed failure reason plus sanitized callback shape | Explicit operator approval for the supported development-lab upgrade/retry. Existing captured sanitized evidence can be reviewed offline. [Build-13 report](managementpacks/vsphere-rdm-topology-e493-startup-compatibility.md) supplies the exact procedure | Retained inventory is not collection proof. No reinstall/recreation, credential/configuration edit, collector restart, inventory deletion or trust change |
| P1 foundation: durable offline regression and test isolation | One opt-in command reruns serial factory tests with default slow exclusions cleared; native network denial and read-only inputs verified before tests; failures propagated; wheel exclusion explicit; all three host-dependent fixtures repaired without production changes | Completed by this cleanup, subject to independent review recorded below. Existing installed dependencies only. Linux runner requires externally read-only inputs and native restrictions; unsupported hosts fail closed | Do not turn a guarded subset into a full release/CI or live qualification claim; retain raw counts and skips |
| P1 next development: DEF-019 lossless view reverse | Synthetic nonsecret source XML with subject filters and instanced property members survives both reverse writers, YAML reload and deterministic re-render; include multi-subject, absent-field and ordinary-view regressions. Registry close condition also requires resolving the recorded residual `summaryInfos` difference for the chosen fixtures, not ignoring it | New focused tooling task; shared core/extractor change, independent framework review, corpus validation and full regression. No live access needed for the conversion defect | Silent filter loss changes which objects a view selects. Preserve UUIDs, member types, ordering and defaults; do not expand the content model speculatively |
| P2 correctness bookkeeping: DEF-017 / FB-018 and FB-008 | Locate or add a direct CLI SDK-pointer regression demonstrating no dereference/copy of `zip_path=None`, plus ordinary ZIP-route regression. Independently compare guard tests to exact tag/version requirements. Propose registry updates with concrete evidence | Source guard is already present; do not duplicate it. Defect/feedback updates remain orchestrator-owned and corpus-coupled. Tag, hook-policy or release changes require a separate implementation brief | An open entry can outlive its fix; conversely an existing partial guard can be mistaken for the whole requirement. No release or tag is part of the verification |
| P2 adapter correctness: DEF-025 retired-control cancellation and DEF-023 paging proof | DEF-025: repeated retired-key nontriggering samples across later cycles, followed by separately approved evidence of alert cancellation within its configured three cycles. DEF-023: deterministic multi-page/malformed-body fixtures and observed paging/incomplete-alert behavior required by its registry close condition | These are separate `compliance` repository tasks, outside tonight's permitted edits; SDK author/reviewer gates apply. Live alert/paging verification requires separate approval | Do not mark code-only or fixture-only proof as live alert closure. DEF-023's code fix is already recorded as landed; the remaining proof differs from DEF-025's remaining implementation |
| P3 existing workflow parity: alert recommendations and policy targeting | First reproduce REST/content-zip recommendation fidelity using source-supported carriers; for policy targeting, preserve Default Policy behavior and add explicit selected-policy tests before changing interfaces | Product choice and tooling/framework review; live import/enablement verification separately approved. Current [installer](../../src/vcfcf_packaging/templates/install.py) and [limitations](../context/known_limitations.md) document the gap | Do not guess endpoints or select a policy by first XML element. Installer/template changes require template-version/staleness review and rebuild planning |
| P3 user-driven expansion | Reconfirm a concrete requested dashboard/API use case, source-supported wire contract and target-version support before additional widget or adapter features | Follow existing recon/design/approval gates. MPB `buildNumber` remains a product decision; four skipped spec tests remain unchanged | Old survey counts and estimated line counts are not sufficient priority evidence. Additional product features were not implemented tonight |

DEF-004 remains an open **blocking** local registry entry for
`vcommunity-os`; do not release that artifact while it is open. DEF-020/021
remain separate existing vcommunity content issues. They were not examined
by editing or connecting to those adapters in this assessment.

The Summary-dashboard workaround/#200 line remains parked per the owner's
[recorded decision and later evidence](../context/investigations/2026-10-13-summary-dashboard-parked.md).
Its [framework review](../context/reviews/framework/2026-10-13-issue-200-bind-after-materialization.md)
has unresolved findings. Broad priorities-review permission does not resume
it, authorize a rebind, or justify deleting devel dashboards. TLS/credential
changes, notification rules and automatic remediation remain separate
features/security decisions.

## Bounded cleanup executed tonight

The test cleanup preserves existing production behavior and assertions:

- The two RDM writer tests use a private test-loaded module path beneath
  `tmp_path`; they still check mode 0600, exclusive creation/refusal and exact
  handoff content. They no longer write or unlink fixed real-repository files.
- The Git-128/no-repository test supplies absent `.git` facts for the explicit
  synthetic ancestor chain and verifies every ancestor was visited. It still
  exercises the real traversal and asserts the original message. Unreadable
  ancestors continue to produce the conservative production verdict.
- [Offline runner and operating limits](../../tests/offline/README.md) codify
  the audited temporary harness as opt-in test support. Stock CI and product
  defaults are unchanged. The runner requires Linux, existing native support,
  externally read-only input mounts and a unique private scratch directory.
  Landlock alone does not cover native metadata changes; the read-only input
  prerequisite is essential. Credential-loader interception is explicit:
  synthetic fixture roots may load, real dotenv discovery is suppressed.
- Test documentation distinguishes ordinary local/CI commands from the guarded
  offline path, and retains the complete failure/exclusion triage.

No `src/` implementation, `.claude/`, content YAML, nested adapter source or
artifact is changed by this cleanup. Prior dirty work remains in place.

## Full-suite triage and remaining gap

The preserved [E4.9.3 full-suite report](../context/reviews/framework/rdm-e493-full-suite.md)
records 2,649 passed, 15 skipped, one deselected and three failed. The two
RDM failures were fixed-location repository writers, and the remaining
Git-128 failure assumed the host's ancestor metadata was inspectable. Those
are test-isolation issues; neither called for weakening production checks.
Both complete affected test modules passed after cleanup: 108 tests under
the unchanged temporary native guard.

The wheel-alone test remains an explicit **not-run** item. Its current fixture
can download isolated build dependencies, write build metadata into the source
tree and install into a scratch site. The active interpreter lacks setuptools,
setuptools_scm and wheel. Do not install or download them under this handoff.
The next approved packaging task should run the unchanged wheel contract from
an isolated source snapshot with preprovided, verified offline build inputs;
then prove only `vcfcf_core` ships and its import/reverse path works without
the factory. A guarded suite excluding it is not that proof.

## Final validation and independent review

| Check | Actual result |
|---|---|
| Changed fixture modules, unchanged temporary native guard | 108 passed |
| New runner contract tests | 16 passed |
| Durable runner native/child smoke | PASS, coordinator and independent reviewer |
| Coordinator durable full factory selection | **2,668 passed / 15 skipped / one deselected / zero failed**, 333 warnings, 173.83 seconds, exit 0 |
| Independent reviewer durable full factory selection | **2,668 passed / 15 skipped / one deselected / zero failed**, 333 warnings, 173.69 seconds, exit 0 |
| Guarded seven stock content validators | All seven return 0; seven Tier 2 projects validate |
| Skill parity, path audit, whitespace and local document links | PASS; six existing path-audit standing-exception warnings retained |
| Independent focused cleanup review | APPROVE, zero findings; [complete report](../context/reviews/framework/offline-regression-priorities-2026-10-16.md) |
| Preserved prior state | All five originally modified tracked paths retain their baseline hashes; all six frozen build-13 source/test/runner hashes and the exact PAK/checksum are unchanged |

Both complete runs use the checked-in command, not the earlier temporary
launcher. All three former failing cases are included; none was excluded,
xfail-marked or granted an allowed-baseline exception. The 333 warnings and
15 ordinary skip reasons remain visible. The excluded wheel-alone contract
is still not qualified; do not describe these results as an unqualified
stock-suite, release or live-platform pass.

Exact coordinator commands from the repository root:

```sh
.venv/bin/python -B tests/offline/run.py --smoke
.venv/bin/python -B tests/offline/run.py --sdk-jar /home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar
```

The SDK is a preexisting authorized proprietary local input, not shipped
in Git or a PAK. No credentials are inputs to these commands. Supporting
execution logs are `/tmp/rdm-next-offline-smoke.log`,
`/tmp/rdm-next-offline-full.log`, `/tmp/rdm-next-content-validation.log` and
the independent reviewer's `/tmp/content-factory-priorities-full.log`.
These are historical local execution records, not prerequisites for the
durable command.

The adapter already has its own repeatable genuine-SDK regression entry:
[run-dispatcher-tests.sh](../../content/sdk-adapters/rdm-topology-poc/scripts/run-dispatcher-tests.sh).
From that independent checkout, the command is:

```sh
bash scripts/run-dispatcher-tests.sh --fixture-lifecycle
```

It uses explicit nonsecret `VCFCF_SDK_JAR` and verified
`VCFCF_DESCRIPTOR_CLASSPATH` inputs plus the existing framework JAR. It
does not read a credential file or fetch dependencies. Its build-13
qualification remains the [separate SDK review](../context/reviews/rdm-topology-e493-startup-sdk-review.md);
the factory runner does not replace that actual-SDK lifecycle evidence.
The adapter and its candidate were not rebuilt or changed tonight.

Build-13 PAK SHA-256 remains
`96d6293f3858bb13e625f52188b515d72e73c9f87ae46debd2ba7e50b30c68ae`.
Historical review counts and prior artifacts were preserved. This cleanup
is uncommitted working-tree work for human review; no new release, registry
closure, live action, installation, dependency download, security-policy
change, commit, push, tag or publication occurred.
