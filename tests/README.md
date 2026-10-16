# Test conventions

## Setup

Test dependencies live in `requirements-dev.txt` (pytest + pinned
pytest-xdist):

```
pip install -r requirements.txt -r requirements-dev.txt
```

pytest-xdist is optional for serial runs — plain `pytest` works without
it. Passing `-n` requires it AND `--dist=loadgroup` (a conftest guard
refuses `-n` without loadgroup, because the `real_corpus` group would
otherwise race — see Markers below).

The ten `vcfcf_*` packages plus the `vcfcf_core` library (the pure parse/walk/render/build code, published as the `vcf-cf-tooling-core` wheel; see knowledge/designs/tooling-core-carveout-v1.md) live under `src/` and are never pip-installed
(an install would leak them into every subprocess via site-packages,
blinding the kit-isolation regression tests). Claude Code / agent shells
get `PYTHONPATH=src` ambiently from `.claude/settings.json`; a bare shell
needs it set explicitly:

```
PYTHONPATH=src python3 -m pytest ...
```

All commands below assume `PYTHONPATH=src` is set one way or the other.

## Running tests

### Fast subset (default local run)

```
python3 -m pytest
```

`pyproject.toml`'s `[tool.pytest.ini_options]` sets `addopts = -m "not slow"`.
Running plain `pytest` deselects tests marked `slow`; it is not the full
suite. Runtime depends on the host and selected tests.

### Full suite locally

```
python3 -m pytest -m "" --override-ini="addopts="
```

Or with parallelism (respects `real_corpus` isolation groups):

```
python3 -m pytest -m "" --override-ini="addopts=" -n auto --dist=loadgroup
```

### Guarded offline regression (opt-in Linux path)

When work forbids real credential loading, networking, downloads and source
writes, use the separate [offline runner](offline/README.md):

```sh
.venv/bin/python -B tests/offline/run.py --smoke
.venv/bin/python -B tests/offline/run.py --sdk-jar /absolute/path/to/authorized-sdk.jar
```

Use an already provisioned interpreter. The SDK path is optional and
nonsecret; no SDK is fetched. The runner requires externally read-only
inputs and working Linux native restrictions, and fails before pytest if
they are unavailable. It does not remount or alter host security settings.
It uses unique private scratch space and propagates raw pytest status.

The selected factory suite is serial, with the default slow filter cleared.
Exactly the wheel-alone test is deselected because its current fixture can
provision build dependencies, write source metadata and install a wheel.
Ordinary dependency/reference/fixture skips remain visible. Synthetic dotenv
fixtures work inside scratch; real dotenv discovery is suppressed. This is
an explicit guarded execution variant, not an unmodified ambient run, a
complete wheel gate or proof of live operation. Ordinary commands above
remain the local/CI workflow and do not provide those restrictions.

### Parallel fast subset

```
python3 -m pytest -n auto --dist=loadgroup
```

The `addopts` default filter (`-m "not slow"`) still applies, so only the
fast subset runs. `--dist=loadgroup` must be passed explicitly whenever
`-n` is used (it is not in `addopts` because xdist is a dev-only
dependency); the conftest guard turns a forgotten `--dist=loadgroup` into
a clear error instead of a flaky race.

## Markers

### `slow`

Applied to any test that individually takes more than ~2 seconds.  This covers:

- Tests that call `publish()` or `build_release()` (zip construction + validator
  passes over the full content corpus).
- Tests in `test_validate_content_hook.py` (subprocess calls to the full
  validator stack).
- Tests in `test_cli_phase4.py` (factory-copy construction + validator run).

Files currently marked `slow` at module level:

| File | Reason |
|------|--------|
| `test_third_party_routing.py` | zip builds + publish integration |
| `test_third_party_component_routing_phase5.py` | zip builds + publish integration |
| `test_cli_phase4.py` | factory copy + validators (~8s/test) |
| `test_release_builder_phase2.py` | zip construction (~5s/test) |
| `test_validate_content_hook.py` | subprocess validator calls |
| `test_discrete_builder_builtin_metric_enables.py` | discrete build/installer metric-enablement integration |

### `real_corpus`

An `xdist_group` marker.  Tests that **read** the real `content/` corpus through
subprocess validators (`publish(factory_repo=REPO_ROOT)`) must not run
concurrently.

`xdist_group("real_corpus")` colocates all affected tests on a single xdist
worker where they execute sequentially, preventing races where concurrent
validator scans interfere with each other.

Files that carry both `slow` and `real_corpus`:

- `test_third_party_routing.py`
- `test_third_party_component_routing_phase5.py`

The publish test files (`test_publish_phase3.py`, `test_publish_pr_mode_v4.py`,
`test_publish_seams.py`) are no longer slow-marked at module level: shape tests
inject the validator/build seam stubs (`tests/publish_seam_stubs.py`, issue
#125) so they neither run the ~200s validator chain nor touch the real corpus.
The exceptions inside `test_publish_phase3.py`:

- `test_real_run_zip_lands` is the #125 anti-drift end-to-end test (real
  validators + real zip build); it alone carries `slow` + `real_corpus`.
- `TestPolicyCaveatInReadme` injects the real builder (its assertions inspect
  README members inside the built zip), so it carries `real_corpus` but not
  `slow` (~3s/test with the validator stubbed).

`test_validate_content_hook.py` is marked `slow` but **NOT** `real_corpus`.
It reads the real content corpus to seed `tmp_path` copies, then sets
`VCFCF_CONTENT_ROOT` so validators operate on those copies. It does not
mutate the real corpus and is safe on any xdist worker.

`test_cli_phase4.py` and `test_release_builder_phase2.py` are marked `slow`
but **not** `real_corpus` because they operate on private temp-directory copies
of the corpus and are safe to run in parallel with other workers.

## Parallel safety

All tests that do NOT carry `real_corpus` are designed to be fixture-isolated:

- Publish/release tests create temporary git repos via `tmp_path`.
- `test_cli_phase4.py` copies the entire corpus into a temp directory for each
  test class.
- `test_validate_content_hook.py` builds a `tmp_path` workspace and sets
  `VCFCF_CONTENT_ROOT` so the hook subprocess resolves all `content/…` paths
  against that temp tree; initial fixture seeding reads real content, while
  validator writes remain confined to the copy.
- The RDM probe's report/handoff tests use a fixture-controlled module path
  beneath `tmp_path`, preserving permission and exclusive-create assertions
  without touching the real operator scratch directory.
- Tests are intended to isolate writes; the guarded offline command enforces
  read-only source inputs and scratch-only data writes. Keep new subprocess
  and filesystem tests within that contract instead of assuming isolation.

`tests/managementpacks/` and all the validator/loader unit tests are
stateless and safe for full parallelism with `-n auto`.

## CI

CI runs the full suite with parallelism:

```yaml
python3 -m pytest tests/ -v --tb=short -n auto --dist=loadgroup --override-ini="addopts=" -m ""
```

`--override-ini="addopts="` clears the local-default `not slow` filter.  
`-m ""` explicitly matches all tests regardless of marker.  
`-n auto` parallelises across available CPUs.  
`--dist=loadgroup` ensures `xdist_group("real_corpus")` tests are colocated on
one worker so the publish tests (which scan the real content/ corpus) never
execute concurrently.


## Offline full-suite triage

The [historical E4.9.3 run](../knowledge/context/reviews/framework/rdm-e493-full-suite.md)
reported 2,649 passed, 15 skipped, one deselected and three failed. That
history is retained unchanged. The two RDM writer tests used a real shared
scratch path; the Git-128/no-repository test assumed ancestor `.git` metadata
was inspectable on the host. Their fixture isolation is corrected without
changing production checks, expected messages, mode 0600, exclusive-create
or exact-content assertions. New runs must report their own raw results.

The wheel-alone test is not an allowed failure or a passing test. Its
explicit offline exclusion remains until an approved isolated packaging
run has preprovided build inputs; the current interpreter lacks setuptools,
setuptools_scm and wheel. Do not download/install dependencies or weaken
the test to remove that limit. See the
[priorities and cleanup record](../knowledge/designs/content-factory-next-work-2026-10-16.md)
and [runner limits](offline/README.md).
