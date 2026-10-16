# DEF-019 implementation checkpoint — 2026-10-16

This is the historical 11:17 UTC checkpoint. See the later
[verified implementation handoff](def019-view-reverse-fidelity.md) and its
independent review for the post-reboot result.


**Status: blocked on host memory/execution capacity. Full regression and final
framework approval are pending. This is a checkpoint, not an approval or a
defect-registry closure.**

## Local candidate

The frozen correction restores supported subject filters, independent
property/string flags, one-driver instanced-group metadata and explicit summary
rows through the two dictionary/YAML reverse writers and the dataclass API.
It uses the existing `subject.filter`, `InstancedGroupSpec` and `SummaryRow`
model. Unsupported selector/group/summary semantics raise fixed, value-free
errors before affected view YAML is written.

Source changes are limited to `src/vcfcf_core/dashboards/reverse.py`,
`src/vcfcf_core/extractor/extractor.py` and
`src/vcfcf_core/extractor/reverse_local.py`. New coverage is
`tests/test_view_reverse_fidelity.py` and three explicitly synthetic
`tests/fixtures/view_reverse_fidelity_*.xml` inputs. No forward renderer,
loader, model, template-version, packaging or adapter change is part of this
correction. See the [supported contract](../context/wire-formats/view_reverse_fidelity.md)
for strict boundaries and focused commands.

The original private four-view extract and live acceptance were not verified.
The [DEF-019 registry](../context/defects.md) remains unchanged and open.

## Completed evidence

These results were completed before the interrupted full-suite attempts:

| Check | Result |
|---|---|
| Final synthetic matrix against preserved original source | 261 failed, 3 passed; the ordinary routes pass |
| Final synthetic matrix against frozen correction | 264 passed, 4 recorded warnings; independently repeated |
| Author's seven-file related selection | 388 passed, 10 recorded warnings |
| Independent related/core-isolation selection | 239 passed, 1 skipped, 1 wheel test deselected, 6 warnings |
| Seven actual validator CLI functions under native/startup guards | All returned 0; seven Tier 2 projects validated |
| Actual stock `scripts/validate-changed-content.sh --all` under the same guards | Exit 0; direct CLI results above separately verify all seven |
| Independent forward corpus comparison | All actual bytes and serialized input/output manifest fields identical: 26 views, 41 supermetric inputs, no factory imports or warnings |
| Independent static/focused review | No unresolved findings; final gate still pending |

Forward XML SHA-256:
`4448d9bcb3037e08845e706aef62912de3b6471e87ae46e7a654deec382bc288`.

The active interpreter lacks `setuptools>=64`, `setuptools-scm>=8` and `wheel`.
The unchanged guarded runner explicitly deselects
`tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path`.
Nothing was downloaded or installed. That wheel-only contract remains a
separate qualification gap; none of the incomplete full logs is a pass.

## Recovery and memory measurements

At approximately **11:17 UTC on 2026-10-16**, executor reads responded. Session
`32996` returned `Unknown process id`. Its log has no final summary/exit status.
A host read-only PID search found no matching authorized offline test processes;
no process was stopped. Read-only memory measurements showed:

| Measurement | Observed value |
|---|---|
| Physical memory | 15,189 MiB total, 1,638 MiB available |
| Swap | 8,191 MiB total, 8,171 MiB used, 20 MiB free |
| Two current `vmstat` intervals | Swap-out 8,140 and 12,376 KiB/s; I/O wait 39% |
| Memory PSI | `some` avg10 0.14%, avg60 0.25%, avg300 7.43%; `full` avg300 6.72% |

This is still material pressure despite a connected host and responsive small
reads. **No new heavy suite or reviewer was launched in this recovery.** No
OS/swap/security settings or unrelated processes were changed.

Earlier incomplete logs are retained, with these recovery-time fingerprints:

| Log in `/tmp/` | SHA-256 |
|---|---|
| `vcfcf-def019-full-root.log` | `5e17a2edac78556c28da16d5469858ae103d76621fe83fb12a56dd1c883a570e` |
| `vcfcf-def019-review-full.log` | `c77836e8c0f8c202341ae4a5c209717afdefd42cdd2eb1be4a48e9716b7d1d47` |
| `vcfcf-def019-full-root-recovery.log` | `6d478a272f1021ad7609c5ca63bd6656fa3f403bb05b14354214c01bb1d132c4` |
| `vcfcf-def019-full-root-recovery2.log` | `9218076c036ef5fe798a1f612d27930fc4cb9a82c2702d20319813d7ccdbb561` |

## Preservation verified during this recovery

All eight files match `/tmp/vcfcf-def019-author/frozen-v2/manifest.json`, whose
SHA-256 is `c50fb4ed09c866b2dd096fcd13e4c1f027aff410fefabb4fa220627a62caa23f`.
Among the 23 preserved task-baseline paths, only the three authorized core
modules changed; the other 20 match. Prior dirty work and the offline runner
remain intact.

All six entries of `/tmp/rdm-e493-build13-source-freeze.sha256` were rechecked
successfully in the nested adapter checkout. The existing build-13 PAK remains
`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.13.pak`,
SHA-256 `96d6293f3858bb13e625f52188b515d72e73c9f87ae46debd2ba7e50b30c68ae`.
Its checksum-sidecar hash remains
`526838cb096c5be40a640add2d71182a883a5e925c6b75b8f042dbb31c389b1e`.
No new PAK is required for this reverse-only change, and no live RDM recovery
evidence is added by this task.

## Bounded next steps

1. Have the operator provide memory headroom. Confirm with small read-only
   `free`, memory-PSI and three-sample `vmstat` checks that active paging has
   subsided; a connected status alone is insufficient.
2. Inspect existing logs/session state and matching test PIDs before any retry.
   Preserve incomplete logs. Do not kill unrelated work or change OS settings.
3. Run exactly one guarded full suite, serially, into a fresh log:
   `.venv/bin/python -B tests/offline/run.py --sdk-jar /home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar`.
   Check memory using small reads; if pressure returns, launch no additional
   heavy work and retain an explicit incomplete result.
4. Only after a verified exit/result, perform independent full validation
   serially. Resolve any findings without changing unrelated work.
5. Recheck frozen/baseline/build-13 hashes, save the final independent review
   and implementation handoff, and then propose accurately scoped registry
   reconciliation. Do not infer completion from focused tests or this record.

All work remains uncommitted. No live infrastructure, credentials, install,
reconfiguration, dependency download, security-policy change, push or publish
was performed.
