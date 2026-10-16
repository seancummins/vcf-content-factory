# E4.9.3 — Independent framework review

Verdict: **APPROVE**, scoped to the existing framework guards reused by E4.9.3. Zero new BLOCKING, WARNING or NIT findings. No E4.9.3 framework source change is present; Java adapter behavior and the eventual PAK require the separate SDK/security reviews.

## Scope and authorities

Read-only review of the dirty `src/vcfcf_managementpacks/sdk_builder.py` diff and its constructor/descriptor regression modules, following `.claude/agents/framework-reviewer.md`, `knowledge/context/authoring/guide_reviewer_doctrine.md`, `.agents/skills/vcfops-validation/SKILL.md`, `.agents/skills/vcfops-sdk-adapter/SKILL.md`, RULE-005/008/013/014/016, the lessons index, architecture and ownership documentation. The two named historical renderer escapes (00d3382, 6c59f6b) were checked for applicability.

The present sdk_builder source and constructor-test hashes exactly match `knowledge/context/reviews/framework/sdk-entry-constructor-e492.md`:

```text
10c7f9eff6464bba8667adf84bedb8b37b0f78d41602cddde3dcf851d1a3b5ce  src/vcfcf_managementpacks/sdk_builder.py
7999ccd4940c8134cf49fe9117e1741b0a988fda8ed6384af7e12253011ffec8  tests/managementpacks/test_sdk_entry_constructor_contract.py
e71c4ef54103dee51acdfe167435290cf5dd5877cfae8419b157a1d705b50f09  tests/managementpacks/test_sdk_describe_key_contract.py
```

The constructor guard inspects actual class metadata using javap and does not load or execute adapter code. It requires a public concrete entry class, a declared public no-argument constructor and exact public `(String, Integer)` constructor. Primitive int, private, varargs, missing, inherited-only, abstract and nonpublic cases fail. Controller and collector guards run on validate-sdk and direct/buildkit builds before packaging. The bounded descriptor guard distinguishes SDK ResourceGroup/ResourceAttribute key segments from composite runtime MetricKeys, checks the documented separators, and preserves the release/warn-only rejection precedence.

No renderer, key derivation, global content defaults, assembly template, identity or relationship emitter is changed. The named standalone rendering escape patterns are not reopened. A template-version bump/content ZIP rebuild is not required by these validation-only guards.

## Independently reproduced checks

| Check | Actual result |
|---|---|
| Entire `tests/managementpacks` directory, all markers enabled | 339 passed, 8 skipped, 115 warnings; 14.32 seconds |
| Seven stock content cmd_validate implementations, guarded offline equivalent | PASS: all return 0 |
| Tier 2 projects encountered by full content validation | Seven valid; actual SDK compilation and exact constructor ABI checks passed for all |
| Codex skill parity | PASS: five paired, seven Codex-only |
| Path-reference audit | PASS: no dead paths; six documented standing-exception warnings |
| git diff --check | PASS |
| Broader factory suite | Not rerun in this scoped E4.9.3 review |
| Render regression / PAK comparison | No changed renderer/output; separate SDK/artifact review covers candidate PAK |

Tests used the existing repository `.venv/bin/python`, `PYTHONDONTWRITEBYTECODE=1`, `pytest -p no:cacheprovider --basetemp=/tmp/rdm-e493-framework-test/managementpacks`, and the explicitly supplied local SDK JAR. No dependencies were downloaded and proprietary SDK bytes were not copied or redistributed. The test startup audit hook refused real credential-file reads and Python network connections; only fixture credential files beneath the unique /tmp test root were permitted. The tests' isolated buildkit subprocess paths were inspected before running.

There were two corrected reviewer invocation issues before the successful test run: the system python has no pytest, and the first .venv test attempt had a nonexistent basetemp parent. These are harness/setup failures, not product test failures. The recorded successful count comes from the completed rerun after selecting the existing .venv interpreter and creating only the /tmp parent.

## Credential-loading boundary and limits

Inspection found that `src/vcfcf_common/_profile_cli.py:validate_profile_arg` calls load_dotenv unconditionally before testing whether a profile was supplied. All seven stock content validate functions call this helper. Therefore the unmodified `scripts/validate-changed-content.sh --all` would read real .env content in this checkout; it was **not run** under this handoff's explicit no-credential-read restriction.

Instead, a temporary in-process harness replaced only `vcfcf_common._env.load_dotenv` with a no-op before importing each stock CLI and invoked `main(['validate'])` for supermetrics, dashboards, customgroups, symptoms, alerts, reports and managementpacks. An audit hook refused credential-file opens, Python networking and repository writes. The content validation implementations, default corpus paths, cross-reference/slug checks, SDK compilation, descriptor guards and constructor checks all remained in place. This is explicitly an offline guarded equivalent, not an unmodified shell-script PASS.

The previously reported unchanged full-suite failure `tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo` is recorded in the E4.9.2 review. It was not rerun here and is not represented as resolved or waived. No full green factory-suite claim is made.

If shipped as-is: framework validation continues to reject invalid descriptor segments and missing platform constructors before packaging; this review supplies no proof that a live account initializes or collects. Existing framework gates are approved for reuse by E4.9.3, conditional on no later framework edits.

No repository file was edited by this reviewer. No preflight/doctor command, live access, installation, artifact build, staging, actual-repository commit, push, publish, credential access or trust change occurred. Temporary review scripts/logs live only in /tmp and are supporting execution records, not reproducible corpus authorities.
