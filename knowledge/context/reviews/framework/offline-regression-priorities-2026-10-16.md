# Content Factory offline regression and priorities cleanup review

Date: 2026-10-16

Reviewer: independent `framework-reviewer` agent, read-only on the repository.

**Verdict: APPROVE. Zero unresolved findings (blocking, warning or nit) in the scoped cleanup.**

This approves the test-isolation repairs, opt-in guarded test runner and corrected planning/documentation. It does not qualify the excluded wheel contract, change production security policy, approve a release/install or establish live RDM recovery.

## Scope and authorities

Reviewed `tests/test_common_setup.py`, `tests/test_rdm_lab_probe.py`, `tests/offline/{run.py,sitecustomize.py,README.md}`, `tests/test_offline_runner.py`, `tests/README.md`, `knowledge/ROADMAP.md`, `knowledge/context/known_limitations.md`, and `knowledge/designs/content-factory-next-work-2026-10-16.md`.

The final evidence-only design footer was independently reviewed as `/tmp/content-factory-next-work-final.md`, SHA-256 `88f9f1b81ce101adc203dd78e03b2215590fd156e9d9ea06dc3de3051761fd5a`. It replaces the pending-results paragraph with actual command/results, explicit limits, the review link and the separate existing genuine-SDK regression entry. Approval includes saving exactly that candidate.

Authorities consulted include `AGENTS.md`, `knowledge/rules/INDEX.md` and relevant rules, `knowledge/lessons/INDEX.md`, `knowledge/HOW_IT_WORKS.md`, `STRUCTURE.md`, `.claude/agents/framework-reviewer.md`, the shared reviewer doctrine, and the local validation/SDK-adapter skills. Credentials, immutable reference material, live actions, releases and independent-review boundaries were preserved. The source/output regression anchors do not gain new production paths: this cleanup changes no renderer, loader, builder, adapter or production CLI implementation.

Only this report was written by this reviewer, under `/tmp` as instructed. No repository edits, infrastructure connections, credential reads, dependency installation/download, candidate rebuild, commit, push, tag or publication were performed by this reviewer.

## Findings and acceptance assessment

The Git-128 regression test supplies absent `.git` metadata only for its explicit synthetic ancestor chain. It still executes the real traversal, verifies each ancestor was visited and asserts the original expected message. Neighboring unreadable-metadata tests retain the conservative production verdict; the product was not weakened to accommodate the host sandbox.

The two RDM writer tests relocate the test-loaded module's `__file__` beneath private `tmp_path` storage. They still execute the real writer helpers and assert mode 0600, exclusive creation/refusal and exact handoff contents. They no longer create or unlink fixed real-repository paths. Existing operator fixture data is untouched.

The new runner is opt-in and bounded to trusted project tests. It derives its checkout, limits selection to Python test paths below `tests/`, rejects invalid/escaping selections and nested runs, clears inherited application configuration, uses unique mode-0700 scratch storage and propagates the child guard. It provides no arbitrary command or pytest-flag passthrough. Ordinary product entry points, stock CI and user defaults are unchanged.

The native guard fails closed unless the existing Linux Landlock/seccomp facilities and externally read-only input mounts are available. Writable inputs are refused before Linux mount metadata is read. The physical read-only requirement is essential: Landlock alone does not cover native chmod/chown/utime/xattr operations. No writable-checkout fallback, remount, policy weakening or dependency fetch is implemented. System runtime reads are intentionally broader than project reads; the documented scope is audited project regression execution, not a general sandbox for arbitrary hostile commands or all host secrets.

Inherited native filesystem rules restrict writes to owned scratch; native socket creation/connection/send primitives are denied in children, including Python `-S` and non-Python executables. The Python startup guard additionally rejects sensitive paths and outside writes, handles child environments and explicit raw/resolved-path cases, and exits on invalid startup state. Smoke probes use synthetic sentinel files only. Sentinel creation is exclusive, no-follow and mode 0600.

Credential-loader interception is explicit and test-only: real dotenv discovery/loading is suppressed; synthetic fixture `.env` files inside owned scratch still use the real parser. This is an intentionally guarded suite, not an assertion that unmodified stock CLIs are credential-free. No actual `.env` existence or contents were inspected. The README accurately describes these semantics and prerequisites.

The 16 runner contract tests cover environment construction, bounded selection and symlink escapes, exact exclusion behavior, exclusive sentinel creation, early writable-input refusal, unsupported native facilities, nested-run refusal, raw child exit propagation, missing local wheel prerequisites and inherited native smoke. The complete run includes all three previously failing cases, with no added xfail, allowed-baseline exception or exclusion for them.

The revised roadmap describes capabilities already present in source/CI, including native Java SDK adapters, PropertyList/RRA and the test suite. Platform/wire behavior is qualified by captured evidence rather than invented. Known-limitations text distinguishes the previously observed empty clone and later binding behavior. The new plan selects DEF019 semantic-loss repair as the next offline feature priority, distinguishes implementation already present from unresolved evidence/coverage, leaves registries open and retains the separately authorized operator-controlled RDM action. It neither silently closes defects nor resumes parked release/live work.

The final design footer accurately distinguishes factory regression from `bash scripts/run-dispatcher-tests.sh --fixture-lifecycle`. The latter remains a separate frozen genuine-SDK lifecycle command requiring explicit nonsecret SDK/descriptor classpath inputs. Static inspection confirms it does not source credentials or fetch dependencies; it was not rerun or modified in this cleanup review.

## Independent execution evidence

Both commands below were run from `/home/scummins/Documents/vcf-content-factory`, using the final frozen checked-in harness and fresh private scratch directories:

```sh
.venv/bin/python -B tests/offline/run.py --smoke > /tmp/content-factory-priorities-smoke.log 2>&1
.venv/bin/python -B tests/offline/run.py --sdk-jar /home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar > /tmp/content-factory-priorities-full.log 2>&1
```

Native smoke: **exit 0**. It reported Landlock ABI 10, externally read-only inputs, inherited native child read/write/socket denial, dir-fd/symlink behavior and synthetic dotenv behavior, ending `OFFLINE_SMOKE_PASS`. No packed-ctypes warning remained.

Full guarded factory selection: **exit 0; 2,668 passed, 15 skipped, one deselected, 333 warnings in 173.69 seconds**. The runner invokes:

```text
['/home/scummins/Documents/vcf-content-factory/.venv/bin/python', '-B', '-m', 'pytest', 'tests', '--override-ini=addopts=', '-m', '', '-p', 'no:cacheprovider', '--basetemp=/tmp/vcfcf-offline-ikgbxfqz/pytest', '--deselect=tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path', '-q', '-ra']
```

The configured slow/default marker filters are cleared. Execution is serial, with bytecode/cache disabled and scratch basetemp. This is the full factory test-tree selection with the one disclosed wheel exclusion, rather than only the managementpack subtree. The coordinator's separate complete run recorded the same counts in 173.83 seconds; that is independent corroboration, not the reviewer's timing.

The 15 ordinary skips are unchanged environment/product conditions: four pending MPB buildNumber cases, three absent reference-PAK integration cases, one scaffold test expecting a different local SDK location, one missing-setuptools contract, one wrapper-coverage condition, four PowerShell-unavailable cases and one existing operator fixture that the test explicitly leaves untouched. The explicit SDK input enables applicable SDK tests but does not rewrite the scaffold test's independent path prerequisite.

The sole deselection is `tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path`. The active interpreter lacks `setuptools>=64`, `setuptools-scm>=8` and `wheel`; nothing was installed. Its unchanged fixture can fetch isolated build dependencies and write source metadata. The runner does not pretend to qualify that contract. A future approved isolated-source task with preprovided verified offline build inputs must test the unchanged wheel-only import/reverse contract. This review does not treat that planned gap as a passing test or a new product failure.

Additional independently executed checks passed:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/check_skill_parity.py
bash scripts/path_reference_audit.sh
git diff --check
```

Parity reports five paired and seven Codex-only skills. The path audit has no dead references; six documented standing-exception warnings remain. The seven guarded stock content validators were run by the coordinator, not rerun in this focused review. Their `/tmp/rdm-next-content-validation.log` records all seven module return codes as 0 and seven Tier 2 projects valid; this report distinguishes that supplied evidence from the independent runs above.

Log SHA-256 values:

| Log | SHA-256 |
|---|---|
| `/tmp/content-factory-priorities-smoke.log` | `a7d8a303571e476ef48f2fdf37dcd5dee85c46b1e812e9a9eb214929b005d7f5` |
| `/tmp/content-factory-priorities-full.log` | `ff544a150f4939db56ab20faade00f677a06bda9dd32517211a417a38ae86b4c` |

The historical E4.9.3 scoped-managementpack and earlier full-suite reports remain separate historical records. Their original failures/counts have not been rewritten as this later success.

## Reviewed freeze and preservation

Post-run hashes match the author/coordinator freeze:

| Path | SHA-256 |
|---|---|
| `tests/offline/run.py` | `41ebce1be173f3bf6fd9709657ab35b635a596ac460b10ce657c763e20930571` |
| `tests/offline/sitecustomize.py` | `9a20023b3da2069cec2d56d131d9dedba160f42632b9df9aaf0e0c1ec14d50c7` |
| `tests/offline/README.md` | `6912b555389b3f1f909d5ee6e5d742e22132efb96aa690cb76c737ef7a7e8a6c` |
| `tests/test_offline_runner.py` | `7c7b37c9031f7dd46f17d0e98e88bd104953f5c037bdb8ffa99a3e8d2cc808a8` |
| `tests/test_common_setup.py` | `e78bd34ba9050869bf87d73340ffe0a73a16990b6ae4eb27c1b26d65cfb93966` |
| `tests/test_rdm_lab_probe.py` | `b6d1800ad51b5fd9b6eaa69efd550e0d4bbc8e03683a7ff0ceea28c203955f56` |

All five originally modified tracked paths match `/tmp/rdm-next-priorities-baseline.json`: the existing RDM lab-validation document, production probe script, SDK builder and two managementpack buildkit test files. The authorized cleanup adds no new `src/`, production script, `.claude/`, `.agents/`, CI, reference-material or defect/feedback-registry changes. Existing dirty work was preserved.

After the complete run, `sha256sum -c /tmp/rdm-e493-build13-source-freeze.sha256` in the independent adapter checkout reports all six frozen Java/test/runner paths OK. The preserved build-13 PAK remains:

`content/sdk-adapters/rdm-topology-poc/dist/vcfcf_sdk_rdm_topology_poc.0.0.0.13.pak`

SHA-256: `96d6293f3858bb13e625f52188b515d72e73c9f87ae46debd2ba7e50b30c68ae`.

No remaining blocker prevents accepting this scoped offline cleanup. Remaining qualification limits are the disclosed wheel contract, environment-dependent skips and separately controlled live/platform evidence; approval does not expand those permissions.
