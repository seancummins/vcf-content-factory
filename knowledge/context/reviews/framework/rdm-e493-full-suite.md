# E4.9.3 — Independent full factory-suite follow-up

Verdict: **APPROVE for the unchanged E4.9.2 framework guards reused by E4.9.3**, with the broader suite's existing failure and safety limits explicitly recorded below. No E4.9.3 framework implementation regression was identified. This is not a green full-suite claim or live-collection qualification.

This follow-up supersedes the earlier scoped review's statement that the broader factory suite was not rerun. It does not change adapter/security review scope or authorize installation.

## Actual results

| Invocation | Result |
|---|---|
| First guarded full factory run | 2,638 passed, 15 skipped, one deselected, 333 warnings; 12 failed and two setup errors; 168.16 seconds |
| Full factory rerun after correcting only the /tmp audit harness | **2,649 passed, 15 skipped, one deselected, 333 warnings; three failed, zero errors; 167.49 seconds** |
| Two repository-writing tests, unchanged, in a byte-identical /tmp snapshot | **Two passed**, 0.03 seconds |
| Final git diff --check | PASS |
| Framework sdk_builder source | Unchanged from the reviewed E4.9.2 hash |

Both full runs cleared the default `not slow` filter, ran serially across `tests`, and used the single explicit safety exclusion below. The previous 339-passed management-pack run is a separate, narrower invocation; it is not represented as the full factory suite.

### Failure classification

1. **Preexisting, unrelated baseline failure:** `tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`, line 1263. The assertion expects `its directory is not a git repo, so nothing there could commit it`, while the actual result is `could not determine whether anything git-ignores it`. This exact failure is already recorded in `knowledge/context/reviews/framework/sdk-entry-constructor-e492.md`. Neither this test nor `src/vcfcf_common/setup_credentials.py` has a working-tree diff. It remains unresolved; no claim is made that E4.9.3 fixes it.

2. **Read-only execution-environment failures, independently resolved in an isolated snapshot:**
   - `tests/test_rdm_lab_probe.py::test_report_creation_is_exclusive_and_restrictive`
   - `tests/test_rdm_lab_probe.py::test_ops_handoff_is_restricted_and_contains_only_local_operator_input`

   These two tests derive the actual repository root from the imported probe module and attempt exclusive writes beneath the real `tmp/rdm-lab-probes`. The full run correctly received `[Errno 30] Read-only file system` before writing. They were then run unchanged against byte-identical copies of `tests/test_rdm_lab_probe.py` and `scripts/rdm_lab_probe.py` in `/tmp/rdm-e493-full-work/snapshot`; both passed with the same inherited kernel restrictions. No repository scratch exception or write escalation was used.

3. **Initial audit-harness false positives, corrected without changing product/tests:** eleven initial failures came from the Python audit hook interpreting relative `os.open(..., dir_fd=...)` paths against cwd because the open audit event omits dir_fd. Two initial setup errors came from resolving a temporary interpreter symlink's final target when checking unlink. The /tmp guard now defers relative dir_fd writes to the unchanged kernel Landlock policy and checks unlink's parent without following the final symlink. A smoke check proved both legitimate scratch operations succeed while outside-scratch reads and native child socket creation remain denied. The refined full run has none of these thirteen harness errors.

No source/test change was made to obtain these results. The final three raw failures must not be hidden by reporting only the passing count; the two supplementary snapshot passes are a separate invocation.

## Safety exclusion and ordinary skips

Exactly one test was explicitly deselected:

`tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path`

Its session fixture runs `pip wheel <actual repo> --no-deps` without disabling build isolation, followed by pip install into a scratch site. Build isolation may download build-system dependencies and wheel creation may write build metadata/residue into the actual repository. The handoff forbids downloads and repository writes by this reviewer. This test was excluded, not changed or represented as passed.

A final guarded prerequisite check evaluated whether an unchanged snapshot variant was feasible. The active test interpreter has pip, pytest and PyYAML, but **does not have setuptools, setuptools_scm or wheel**. The project's build-system explicitly requires `setuptools>=64` and `setuptools-scm>=8`, with `setuptools.build_meta` as backend. PIP_NO_INDEX plus the inherited network ban cannot supply those missing dependencies; disabling build isolation would still leave the backend absent. Consequently no wheel-test invocation was attempted, no backend was installed, and no source/test change or weakened guard was used. This is the precise remaining offline test blocker. Evidence is `/tmp/rdm-e493-full-wheel-prereq.log`, generated by `.venv/bin/python -B /tmp/rdm-e493-full-wheel-prereq-launch.py` under the same OS restrictions.

The 15 ordinary skips reported by pytest were: four pending MPB buildNumber behavior cases; three absent reference-PAK integrations; one scaffold test whose expected local SDK location is absent; one missing-setuptools contract check; one shim case with no delegated names; four missing-PowerShell tests; and one RDM fixture-export test that detects an existing operator fixture and explicitly refuses to touch it. No dependency was installed to remove a skip.

## Audited execution boundary

Before execution, the full test tree (114 Python files), its sole conftest, pytest configuration, subprocess call sites, credential paths, fixture setup, network-facing fakes and invoked shell/JVM entry points were inspected. Slow publish/bootstrap/release tests use temporary local Git repositories and synthetic/mocked clients; real project content is used as a read source. The two unparameterized scratch writers above were discovered by the read-only run and moved only through the separate snapshot invocation.

The test launch environment is recreated from an explicit nonsecret allowlist. HOME, XDG directories and TMPDIR point beneath the dedicated /tmp work root. Real inherited credentials are not passed to pytest or its children. Bytecode writes are disabled; the pytest cache provider is disabled.

Linux Landlock ABI 10 grants read/execute access to approved project/runtime paths, excludes actual `.env`/credential/home paths, and grants filesystem write/create/remove access only beneath `/tmp/rdm-e493-full-work`. Repository code, tests, content, references and Git state remain read-only. Inherited seccomp rules deny socket/socketpair creation, connect and network-send syscalls for all children, including shell and JVM processes. The launcher fails closed if these restrictions cannot be installed.

A Python startup audit hook additionally refuses actual credential-file reads and Python network operations and injects its startup directory into child Python environments before exec. It adds no eager factory imports. A narrow import wrapper preserves the actual dotenv loader for fixture roots under the dedicated scratch tree and returns without credential discovery outside it. This is an offline guarded suite, not an unmodified ambient-credential run.

Kernel smoke evidence includes an artificial outside-scratch sentinel read being denied and a child Python launched with `-S` (therefore bypassing the Python startup guard) being unable to create a socket. The refined smoke also confirms secure relative dir_fd writing and removal of a scratch symlink to a read-only interpreter target. No real credential file was opened for these checks. Bubblewrap network namespaces were unavailable on this host; the working run used Landlock and seccomp instead.

The stock content validate helper unconditionally invokes dotenv discovery before checking whether `--profile` was supplied. That establishes an attempted credential-loading path; it does **not** establish that an existing real .env would be found. Real .env existence/content was not inspected. The earlier scoped report's wording about reading an existing file should be read with this correction.

## Exact retained invocations

Working directory for all commands:

```text
/home/scummins/Documents/vcf-content-factory
```

Initial full run:

```sh
.venv/bin/python -B /tmp/rdm-e493-full-launch.py > /tmp/rdm-e493-full-pytest.log 2>&1
```

Refined full run:

```sh
.venv/bin/python -B /tmp/rdm-e493-full-launch.py > /tmp/rdm-e493-full-pytest-refined.log 2>&1
```

The refined launcher's exact pytest argv, also recorded at the top of its log:

```text
/home/scummins/Documents/vcf-content-factory/.venv/bin/python -B -m pytest tests --override-ini=addopts= -m '' -p no:cacheprovider --basetemp=/tmp/rdm-e493-full-work/tests --deselect=tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path -q -ra
```

Snapshot rerun:

```sh
.venv/bin/python -B /tmp/rdm-e493-full-snapshot-launch.py > /tmp/rdm-e493-full-snapshot-pytest.log 2>&1
```

Snapshot pytest argv:

```text
/home/scummins/Documents/vcf-content-factory/.venv/bin/python -B -m pytest /tmp/rdm-e493-full-work/snapshot/tests/test_rdm_lab_probe.py::test_report_creation_is_exclusive_and_restrictive /tmp/rdm-e493-full-work/snapshot/tests/test_rdm_lab_probe.py::test_ops_handoff_is_restricted_and_contains_only_local_operator_input --override-ini=addopts= -m '' -p no:cacheprovider --basetemp=/tmp/rdm-e493-full-work/snapshot-tests -q -ra
```

## Integrity evidence

```text
402261053abc0e964e8713d0faf398e530f78f7efef7bba537671c3fe58011ba  /tmp/rdm-e493-full-launch.py
f410b70563cff008b42d9501694072afcd224bd82b997f9bafebe65eb01729f5  /tmp/rdm-e493-full-guard/sitecustomize.py
10c7f9eff6464bba8667adf84bedb8b37b0f78d41602cddde3dcf851d1a3b5ce  src/vcfcf_managementpacks/sdk_builder.py
3835807bb751434c429de82f9b809e7a3271c9358c4806f5dabf84bd512dc69f  tests/test_common_setup.py
103da0ac8c293a235e87a187eabee661ed7547d3f91c3a5cd211db159e9e0aad  src/vcfcf_common/setup_credentials.py
e1a5909052bcc38086966cd47a26aa112b26890d27b211715dddcc4a1421a32d  scripts/rdm_lab_probe.py (also the snapshot copy)
892964622de69685364f38591fb38c54c9a239fc293bb05a998571a8242ca8fa  tests/test_rdm_lab_probe.py (also the snapshot copy)
```

Temporary /tmp scripts and logs are supporting execution records, not reproducible repository authorities. The parent may copy this report into the authorized review location; this reviewer has written only /tmp outputs. No actual-repository commit/push/tag, live infrastructure call, installation, credential/trust change, publication or dependency download occurred.

If shipped as-is: the existing framework descriptor/constructor checks retain their reviewed behavior. The broader suite supplies no new framework regression finding; the known setup-test mismatch and excluded wheel gate remain explicit limits. Live initialization and collection still require the operator-controlled validation described by the separate E4.9.3 adapter handoff.
