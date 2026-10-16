# Roadmap

The roadmap tracks capabilities and remaining work. It does not authorize an
installation, release, live investigation or changes to a managed adapter.
The [dated next-work assessment](designs/content-factory-next-work-2026-10-16.md)
contains the current evidence, priorities, acceptance criteria and dependencies.
The [defect registry](context/defects.md) remains the release-gate authority;
the [feedback queue](context/feedback_queue.md) is intake, not a commitment.

## Implemented foundations

- **Content workflows:** super metrics, custom groups, views, dashboards,
  symptoms, alerts, recommendations and reports have authoring/validation and
  packaging support. Live sync fidelity varies by content type; recommendation
  REST parity is still a gap. See [known limitations](context/known_limitations.md).
- **Stable identities and cross-references:** UUIDs travel with authored
  content; name references resolve through the existing loaders and renderers.
  [UUID contract](context/authoring/uuids_and_cross_references.md).
- **Dashboard rendering:** the loader/renderer support ResourceList, View,
  TextDisplay, Scoreboard, MetricChart, HealthChart, ParetoAnalysis, AlertList,
  ProblemAlertsList, Heatmap, PropertyList, ResourceRelationshipAdvanced,
  Section and AlertVolume. A supported factory type is not a guarantee that
  every Ops version imports it; Section is absent on the documented 9.0.2 build.
  [Loader](../src/vcfcf_core/dashboards/loader.py),
  [renderer](../src/vcfcf_core/dashboards/render.py),
  [target-version lesson](lessons/unknown-widget-type-aborts-pak-dashboard-import.md).
- **Distribution:** bundle/release manifests, content-zip assembly, Python and
  PowerShell installers, dependency/staleness checks and SDK-pointer routing
  already exist. Official SDK artifacts remain the managed repositories' CI
  releases; local PAKs are development previews.
- **Management packs:** both MPB and native Java SDK author/build paths exist.
  SDK adapters are independent registered repositories; reference and
  proprietary inputs retain their existing ownership restrictions.
  [Architecture](context/tier2_architecture.md),
  [managed registry](context/managed_paks.md).
- **Shared library:** pure parsing, rendering, graph and offline reverse code
  lives in `src/vcfcf_core/`; factory wrappers own environment, credentials,
  live clients and output paths. The main carve-out is implemented, with
  management-pack pure-code extraction deferred.
  [Carve-out design and completion rows](designs/tooling-core-carveout-v1.md).
- **Named profiles, tests and CI:** prod/qa/devel profile selection exists.
  Automated loader/render/packaging/SDK and corpus tests plus CI validation
  already run. [Test commands](../tests/README.md),
  [CI](../.github/workflows/ci.yml). Counts and per-run limitations belong in
  dated reviews, rather than this capability map.

## Next priorities

1. **Keep qualification repeatable.** Preserve the build-13 evidence, make
   offline regression commands durable, isolate test output and report every
   skip/failure/exclusion. The opt-in [offline test path](../tests/offline/README.md)
   complements stock CI; it does not replace the wheel, install or live gates.
2. **Fix existing semantic loss before new features.** DEF-019 covers subject
   filters and instanced property-member flags lost by reverse conversion.
   Both reverse writers need lossless nonsecret fixture round trips and
   independent framework review.
3. **Reconcile backlog status with code and tests.** DEF-017/FB-018's original
   SDK-pointer guard is already in the CLI; verify regression evidence before
   proposing closure. FB-008's version-line protection is partly implemented;
   exact tag/version equality must be assessed separately. Do not close a
   registry entry because a similarly named helper exists.
4. **Finish evidence on current adapters.** RDM needs a separately approved
   controlled retry or sanitized failing callback; retained topology alone is
   not fresh collection proof. Compliance DEF-023/025 have distinct remaining
   implementation/verification obligations. DEF-004 blocks vcommunity-os
   release. Use the per-artifact registry and reviews, not a blanket roster
   health claim.
5. **Resolve existing workflow parity on demand.** Recommendations on the REST
   alert path and non-Default Policy targeting remain useful scoped work.
   Confirm source-supported wire behavior, preserve existing defaults, test
   both installer paths when relevant and obtain separate live-operation
   approval for acceptance.

## Decisions and deferred work

- **MPB exchange buildNumber:** four skipped `TestBuildNumberExport` cases in
  `tests/managementpacks/test_gap_b_f_d.py` retain the expected contract.
  Emission remains a product decision; do not edit or unskip the specification
  merely to make a run green. The renderer is the implementation boundary.
- **Additional widgets:** SparklineChart and other unsupported types need a
  concrete user requirement and source-supported target-version contract.
  PropertyList and ResourceRelationshipAdvanced are already implemented.
  Dashboard authoring still requires the applicable design approval.
- **Dry-run/orphan tooling and multi-target deployment:** distinguish existing
  per-command dry-run/profile support from a comprehensive sync diff, orphan
  audit or multi-instance deployment workflow. Scope those from actual demand;
  cleanup/deletion remains separately approved.
- **Notifications, remediation actions and extension models:** possible future
  features, with separate design, credentials and execution boundaries. They
  were not implemented as priorities-review cleanup.
- **Summary dashboard workaround/#200:** remains parked per the
  [owner decision and later evidence](context/investigations/2026-10-13-summary-dashboard-parked.md).
  Resume only under a specific new brief and resolve its existing review
  findings; do not interpret this roadmap as a rebind or inventory-cleanup go.

## Gates that apply to every item

Read rules and lessons; reuse existing capabilities; ground vendor behavior
in repository evidence. `src/vcfcf_*/` changes go through tooling and
framework review. Tier 2 changes use the SDK workflow and independent review.
Validate the content corpus and the affected tests, preserve UUIDs and
credentials, and retain explicit approval for live infrastructure, installs,
destructive actions, publication and releases. `.claude/` remains authoritative
and Codex support remains additive.
