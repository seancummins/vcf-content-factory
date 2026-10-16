# DEF-019 — view reverse fidelity, local handoff

Date: 2026-10-16. Status: local candidate for integration review.

## Result and scope

The original reverse parsers omitted modelled selector, instanced-column and
summary fields. The frozen correction restores them through both YAML writers
and the dataclass API. It emits the existing `subject.filter` schema, retains
property/string flags independently, reconstructs the supported driver/member
shape, and carries explicit summary labels, aggregation and ordered indexes.

A shared decoder in `src/vcfcf_core/dashboards/reverse.py` supplies both
dictionary reverse paths. Only that source file and
`src/vcfcf_core/extractor/{extractor,reverse_local}.py` changed. No forward
model, loader, renderer, template-version, packaging, adapter or production
security change is included. There is no raw-XML cache or passthrough.

Unsupported semantics now fail with fixed, value-free errors instead of
silently broadening a selector or dropping group/summary meaning. The supported
contract is one uniform filter across subject entries, one group driver before
its colon-instance members, and one explicit summary row. Heterogeneous
selectors, ambiguous groups and malformed/incomplete rows are rejected.
The [wire contract](../context/wire-formats/view_reverse_fidelity.md) documents
the boundaries and focused commands.

Three explicitly synthetic retained XML inputs exercise actual exported
content-ZIP/local-XML/dataclass parsers, both YAML writers, the unchanged loader
and renderer, and compatibility aliases. The historical private four-view
extract and live import acceptance were not verified. Canonical byte equality
is claimed only for supported retained fixtures/current model cases.

## Validation

The fresh post-reboot guarded full suite completed with **2,932 passed, 15
skipped, one explicitly deselected and 337 warnings**, exit 0, in 197.69 seconds.
The independent serialized full run completed with the same counts and exit 0
in 191.72 seconds. Swap stayed unused; both runs retained about 5 GiB or more
available RAM at the sampled checkpoints.
The unchanged stock `scripts/validate-changed-content.sh --all` also completed
under the same native/startup guards with exit 0. Its direct CLI results are
verified separately by the independent reviewer because the stock wrapper is
fail-open on internal exceptions.

```sh
.venv/bin/python -B tests/offline/run.py \
  --sdk-jar /home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar
```

Raw completed output, exact command/receipt and integrity entries are retained
in [the durable evidence directory](../context/reviews/framework/def019-evidence-2026-10-16/PROVENANCE.md).
Historical completed evidence is preserved in the
[11:17 checkpoint](def019-view-reverse-fidelity-checkpoint-2026-10-16.md).
Fresh independent checks also completed serially:

| Check | Actual result |
|---|---|
| All seven real validator CLI functions, under the native/startup guards | Every return code 0; seven Tier 2 projects valid |
| Same 264-case matrix on exact recovered original modules in a private core copy | Expected exit 1: 261 failed, 3 passed, 4 warnings; ordinary routes remain green |
| Same matrix on frozen corrected source | Exit 0: 264 passed, 4 warnings |
| Forward corpus using pure core | 26 views, 41 supermetric inputs, no factory imports or warnings; SHA-256 matches the recorded historical output |

The fresh forward XML SHA-256 is
`4448d9bcb3037e08845e706aef62912de3b6471e87ae46e7a654deec382bc288`.
This compares a fresh output digest with the recorded historical digest;
the old XML capture and per-input manifests were lost on reboot, so no fresh
two-file byte comparison or old-manifest comparison is claimed. The retained
canonical synthetic XML fixtures independently require byte-identical
round-trips through all three routes.

The [independent framework review](../context/reviews/framework/def019-view-reverse-fidelity-2026-10-16.md)
records the verdict and exact verification details. The review requires zero
unresolved findings for this local candidate; it does not approve an install,
release or claim unavailable private/live evidence.

## Recovery, preservation and remaining limits

The reboot removed `/tmp` logs, original manifest files and draft reports.
Historical results in the checkpoint remain historical; no lost log was
recreated. Recorded checksum entries were recovered from the trusted task
record and checked against actual files. The three original source modules
were recovered from local Git and verified against their recorded original
hashes before use. All eight candidate files, the other 20 preserved baseline
paths, six frozen build-13 source/test/runner entries and the PAK/sidecar match.

The post-reboot health check found about 7.0 GiB available RAM, zero swap use,
zero sampled paging and zero short-term memory PSI. No old test process was
found. New heavy runs are serialized; independent work waits for the first
suite's verified completion. Earlier interrupted attempts are not pass evidence.

The wheel-alone contract remains explicitly excluded by the unchanged guarded
runner because verified local build prerequisites are absent. Nothing was
downloaded or installed. Ordinary environment-dependent skips are disclosed
with the final counts. The 15 skips cover four pending MPB build-number cases,
three missing reference-PAK integrations, one separate scaffold SDK-location
prerequisite, missing setuptools, one wrapper-coverage condition, four absent
PowerShell cases and the operator fixture deliberately left untouched. This
is not an assertion that every stock test passed. The 337 recorded warnings
include four expected default-window warnings in the new matrix; the existing
forward-model defaults and output remain unchanged.

The [DEF-019 registry](../context/defects.md) remains unchanged/open. Integration
should cite the supported synthetic evidence and reconcile the historical
private-fixture close condition accurately; its old `subject_filter` YAML
spelling should be interpreted as the existing `subject.filter` contract.

The separately reviewed RDM artifact remains
`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.13.pak`,
SHA-256 `96d6293f3858bb13e625f52188b515d72e73c9f87ae46debd2ba7e50b30c68ae`.
No rebuild is needed for this reverse-only correction. No new live recovery
evidence for account 15903 is added.

Next human action after final approval: review the uncommitted correction and
its independent report, then decide on integration and accurately scoped
registry reconciliation. No live infrastructure, credentials, install,
reconfiguration, dependency download, OS/swap/security change, commit, push,
tag or publication was performed.
