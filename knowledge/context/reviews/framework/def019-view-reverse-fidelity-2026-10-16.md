# Framework review — DEF-019 view reverse fidelity

Date: 2026-10-16. Independent reviewer: `framework-reviewer`.

**Verdict: APPROVE. Findings: 0 BLOCKING / 0 WARNING / 0 NIT.**

This verdict covers the frozen local correction and its stated synthetic/current-model
contract. It is not a merge, release, installation, live-acceptance result or defect-registry
closure. The implementation author and this reviewer were separate agents; this reviewer
changed no implementation, tests, content or registry files.

## Scope and cause

The original three reverse parsers omitted subject filters, instanced-group metadata,
independent property/string flags and summary rows that the existing model/renderer can
express. Shared fidelity decoding in `vcfcf_core.dashboards.reverse` supplies the two
dictionary routes and the dataclass route; both YAML writers retain the established
`subject.filter` schema. No new top-level YAML key or vendor capability is introduced.

Source scope is exactly:

- `src/vcfcf_core/dashboards/reverse.py`
- `src/vcfcf_core/extractor/extractor.py`
- `src/vcfcf_core/extractor/reverse_local.py`

The accompanying change is one 264-case test module, three retained synthetic XML inputs,
and the bounded wire-contract document. Forward loader, renderer, template version,
packaging and adapter source are unchanged by this task. Existing unrelated dirty changes,
including `sdk_builder.py`, are preservation baselines, not part of this correction.

## Independent execution

Heavy work was serialized after the orchestrator's completed run. This review independently
executed the unchanged durable launcher:

```sh
.venv/bin/python -B tests/offline/run.py \
  --sdk-jar /home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar
```

| Check | Independently observed result |
|---|---|
| Guarded full regression | Exit 0; **2932 passed, 15 skipped, 1 deselected, 337 warnings**, 191.72 seconds |
| New matrix, `--test tests/test_view_reverse_fidelity.py` | Exit 0; **264 passed, 4 warnings**, 0.56 seconds |
| Same final matrix against exact original modules | Expected exit 1; **261 failed, 3 passed, 4 warnings**, 2.53 seconds |
| Seven actual validator CLI return codes | supermetrics, dashboards, customgroups, symptoms, alerts, reports, managementpacks: **all 0**; seven Tier-2 projects valid |
| Pure-core forward corpus | 26 current view YAML inputs, 41 current supermetric inputs, zero warnings, no factory imports or ID-minting callbacks; XML hash matches recorded historical output |
| Preservation | Eight candidate hashes, twenty unaffected baseline paths, six build-13 entries and PAK/sidecar hashes match |
| Whitespace check | `git diff --check`: exit 0 |

Full-suite process session `96071` actually returned exit 0; a log's final line alone was
not substituted for process completion. Source/SDK input mounts were externally read-only.
The unchanged runner installed inherited Landlock ABI 10 and seccomp restrictions, used
private scratch, scrubbed the environment and blocked actual dotenv discovery, credentials,
networking and outside-scratch content writes. No dependencies were downloaded or installed.

The validator check used the same reviewed native/startup guard functions, then imported
each `vcfcf_<package>.cli` and called its real `main(['validate'])`, capturing each result
individually and asserting all seven equal zero. This independently checks the actual CLIs;
the stock wrapper's exit-zero result alone is insufficient because its internal exception
handling can fail open. The orchestrator separately executed that unchanged stock wrapper.

For the red run, a private scratch copy of `vcfcf_core` had only the three modules replaced
with originals recovered from local Git and verified against the original recorded hashes.
The child preloaded all three modules and asserted their actual import paths were inside
that private copy before executing the same final test module. These are real source
parsers and model/renderer tests, not alternate parser shims. The red run's three passes
are the ordinary no-filter/no-group canonical cases. Its failures show the new matrix
detects the former omissions and missing rejection behavior.

The full run initially had about 5.65 GiB available RAM; sampled later checkpoints retained
about 5.0 GiB. Swap stayed unused, sampled swap-in/out were zero, and short-term memory PSI
remained 0.00. No concurrent full suite or heavy reviewer was launched.

## Output and caller review

The retained XML fixtures are parsed through exported content-ZIP extraction, saved local
XML maps and public dataclass content-XML APIs, including factory compatibility aliases.
Both dictionary writers write existing-schema YAML that is reloaded and rendered with the
unchanged loader/renderer; the dataclass itself also renders. Tests independently assert
stable UUIDs, subject and column order, typed values and specific fields alongside canonical
byte equality. There is no raw-XML cache or passthrough.

Selector decoding preserves ordered OR/AND groups, string/integer/finite-float values,
optional absence versus explicit `businessHours=false`, quoted boolean-looking strings,
supported transforms and matching `isStringMetric`. It rejects unknown/missing fields,
duplicate JSON keys, nonfinite values, bare booleans, malformed groups and heterogeneous
SubjectType filters. Errors are fixed, value-free and do not propagate validation payloads.

The group decoder preserves independent `isProperty`/`isStringAttribute`, one unambiguous
driver and subsequent members, explicit driver flags, group identity and member key
components, including later colons/pipes in a suffix. Expressions are retained by both
dictionary routes. Multiple drivers, members before a driver, malformed critical property
shapes, missing driver keys and malformed member keys are rejected. Ordinary colon-bearing
columns without a driver remain ordinary. A member cannot bind itself to a second driver
in this wire shape; a wider group contract is deliberately not inferred.

Summary decoding directly checks one explicit row and its supported scalar/list shapes,
label, aggregation and ordered in-range indexes. Missing summary, explicit empty indexes,
index zero and all-column indexes stay distinct. Unknown/duplicate/missing fields and
malformed/incomplete present rows fail instead of dropping information or inventing defaults.

A repository-wide caller sweep confirmed extraction parses pending views before YAML writes
and local port builds/parses the view map before output writes. The new fidelity exceptions
propagate before affected output can silently broaden a selector or lose group/summary
meaning. Public dataclass docstrings and the new wire contract state this narrow exception
to earlier WARN/None behavior; unrelated unsupported-shape warnings retain their behavior.

The pure-core modules add only standard-library JSON/math use and existing-model imports.
They introduce no factory imports, environment loading, repository-root discovery, global
renderer default changes or implicit ID minting. Existing core isolation, shim, multi-subject,
time-segment and renderer-regression tests passed within the full suite. The global-default
escape `00d3382` and localization-collision escape `6c59f6b` were inspected: the correction
changes neither forward defaults/coordinates nor localization derivation. Existing regression
anchors also run in the suite. No changed template, assembly or render source triggers stale
bundle/version work, and no PAK rebuild or pak-compare is warranted for this reverse-only change.

## Forward evidence and preservation

The pure-core forward check sorted `content/views/*.yaml` and `content/supermetrics/*.yaml`,
read existing supermetric names/IDs into an explicit map, loaded all 26 views without an ID
callback, and rendered their combined content XML. The actual output SHA-256 is:

`4448d9bcb3037e08845e706aef62912de3b6471e87ae46e7a654deec382bc288`.

It equals the historical checksum recorded before this source correction. The old actual
XML and per-input/output manifest were lost on reboot; this is a current-output-to-recorded-
checksum comparison, **not** a new byte comparison against a surviving old file or manifest.
A fresh per-input manifest and actual XML were retained locally for this run. The forward
loader, renderer and template-version hashes also match the original preservation baseline.

All eight candidate files are frozen as follows (also recorded in the durable evidence
`freeze.json`):

| Path | SHA-256 |
|---|---|
| `src/vcfcf_core/extractor/extractor.py` | `9b88687523e44f21177f02069353fd3ff585891b4f31a762d36728a087e6a06f` |
| `src/vcfcf_core/extractor/reverse_local.py` | `c0de95df8d58aa44da630d5678caf2e2c43ef38624a158aaad060104b858b52d` |
| `src/vcfcf_core/dashboards/reverse.py` | `5ddb1f3980b7ba2a54f14b54fdde5ac8bfac680f9a8a3e3c08a910c53094a1f5` |
| `tests/test_view_reverse_fidelity.py` | `e897e4960c2f2ea1435d0208101603575a44ed0e6b43a9d703396bd03758af49` |
| `tests/fixtures/view_reverse_fidelity_ordinary.xml` | `8ffcfd7a68cf7cb1c81a9af1f1b2c3f8c8556b68c7aafddb839209ba4fd00f92` |
| `tests/fixtures/view_reverse_fidelity_filtered.xml` | `7f0f77cb6a3eedfda429cc71ee7828f0ecf15f50788b4012b86a7e265578ea53` |
| `tests/fixtures/view_reverse_fidelity_instanced.xml` | `19e41fe7495c0b98dfbe0fdfecc9ea4f3afd035bb7a8164f7f28b061f60a45ae` |
| `knowledge/context/wire-formats/view_reverse_fidelity.md` | `e64e16efa3215c7365f154e452722fdcbec9daf9b643b70063d061aaaf23ceb0` |

All twenty other recorded original baseline paths matched, including prior test/runner/
roadmap work, the unchanged/open defect registry and preexisting dirty production probe,
SDK builder and management-pack test files. The six build-13 Java/test/runner entries also
matched. The existing RDM PAK remains:

`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.13.pak`

SHA-256 `96d6293f3858bb13e625f52188b515d72e73c9f87ae46debd2ba7e50b30c68ae`;
sidecar file SHA-256 `526838cb096c5be40a640add2d71182a883a5e925c6b75b8f042dbb31c389b1e`.
No proprietary SDK library was copied into the repository or artifact.

## Approved final documentation

The exact final handoff, one-row context-index addition and historical-checkpoint pointer
were independently read and approved before their repository save. Candidate-byte SHA-256:

| Draft basename | SHA-256 |
|---|---|
| `handoff.md` | `965eb5a1bcb94451afb1f5e2a603c308ee3fc8d8bbcdf9b59afaca2bdd474ec1` |
| `context-index.md` | `25ec2030467a586c85a14b12c259b1e167de29b4d6201c712785a3e2c19fd1f5` |
| `checkpoint.md` | `f3501384e35679d9619eec9033857c78dbc0f4bdcca51e5d3b0d3db15dd2200c` |

The evidence directory itself grants no approval: this separate report contains the verdict.

## Limits and next action

Exactly one test remains explicitly deselected by the unchanged runner:
`tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path`.
Its isolated build/install fixture is outside the authorized offline scope and verified local
`setuptools>=64`, `setuptools-scm>=8` and `wheel` prerequisites are absent. The 15 ordinary
skips cover four pending MPB build-number cases, three unavailable PAK comparison artifacts,
one SDK-cert-review fixture-path case, one missing-setuptools contract, one inapplicable shim
case, four missing-PowerShell cases and one protected operator RDM fixture. None is a new
DEF-019 exclusion. The 337 warnings are disclosed; four in the focused matrix are existing
aggregate-with-implicit-default-window warnings. This is a guarded suite with an explicit
exclusion, not a claim that every stock test passed.

The original private four-view extract and live platform acceptance were not available and
were not tested. One uniform view-wide selector, one unambiguous group and one explicit
summary row are the supported contract; heterogeneous owning-SubjectType injection or a
broader forward-model/PAK-origin view may correctly raise an explicit error. Canonical byte
identity is confined to the retained/current-model cases, not arbitrary vendor JSON key order
or whitespace. No live RDM recovery claim for account 15903 is added.

The review is grounded in `knowledge/context/wire-formats/view_reverse_fidelity.md`, the existing
`SubjectFilterCondition`, `InstancedGroupSpec` and `SummaryRow` model/renderer contracts,
`view_column_wire_format.md`, RULE-001/002/007/013/015/016, and the shared-helper caller-sweep
and defect-registry-coupling lessons. The final handoff and evidence provenance accurately
distinguish original recorded checksums, lost historical logs and new post-reboot outcomes.
The context index adds only discovery for the new wire document; the checkpoint retains
its historical blocked result and points to the later handoff.

**If shipped as-is:** supported reverse conversions retain the previously dropped semantics;
unsupported selector/group/summary cases stop explicitly for operator review. No existing
forward output behavior changes. Review the uncommitted correction for integration, then
reconcile DEF-019's historical private-fixture close condition and the registry's old YAML
spelling accurately. The registry remains open/unchanged; this reviewer does not close it.

Raw fresh full/validator/matrix results and provenance belong beside this report in
[the evidence directory](def019-evidence-2026-10-16/PROVENANCE.md); the independent result
receipt records exact raw-log hashes. Old `/tmp` logs did not survive and were not recreated.
The red tracebacks need not be archived: original/source/test hashes, verified import method,
actual summary and expected exit status above fully describe that local-only reproduction.
