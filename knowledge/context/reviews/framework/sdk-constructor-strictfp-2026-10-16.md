# Framework review — Java 11 strictfp constructor recognition

Date: 2026-10-16. Independent role: `framework-reviewer`.

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT findings.**

## Bounded scope and authority

This review covers only the commit-readiness correction in
`src/vcfcf_managementpacks/sdk_builder.py` and
`tests/managementpacks/test_sdk_entry_constructor_contract.py`.
The existing descriptor guard and collector/controller constructor contract are
preserved; their prior review is
`knowledge/context/reviews/framework/sdk-entry-constructor-e492.md`.
The controller authority is also recorded in
`knowledge/lessons/controller-describe-bare-instantiation.md`.
RULE-013 and the shared reviewer doctrine govern this independent review.

The one production change permits the optional `strictfp` modifier in a public
constructor declaration emitted by `javap`. Java 11 strictfp classes place
`ACC_STRICT` on constructors. This modifier does not change their JVM descriptor
or public visibility. Matching remains anchored to the configured binary class
name, with optional generic constructor parameters, and still requires both
exact descriptors: `()V` and `(Ljava/lang/String;Ljava/lang/Integer;)V`.
The class must still be public and concrete.

No ABI broadening, adapter-specific exception, fallback or code execution was
introduced. Inspection remains `javap -public -s`, not class loading or
constructor invocation. Primitive `int`, Object, varargs, inherited, nonpublic
and missing constructors remain invalid. Absent/malformed/failed inspection
remains fail-closed. Existing no-JDK validation explicitly remains unverified,
not a positive ABI result.

## Independent verification

Executed only the four focused modules, as explicitly requested; no full suite,
content-validation chain, PAK build, SDK lifecycle or live test was rerun:

```sh
PYTHONPATH=src .venv/bin/python -m pytest \
  tests/managementpacks/test_sdk_entry_constructor_contract.py \
  tests/managementpacks/test_sdk_describe_key_contract.py \
  tests/managementpacks/test_buildkit_isolated_build.py \
  tests/managementpacks/test_buildkit_release_flag.py -q --tb=short
```

Result: **63 passed, 8 existing unknown-timeout-marker warnings, exit 0**,
5.16 seconds. Local `javac` is 25.0.4.1; the synthetic inputs are genuinely
compiled with `--release 11 -proc:none`, not simulated javap strings.

Both ordinary and generic strictfp classes produce actual `public strictfp`
constructor metadata. The tests assert that the former regex rejects that real
metadata and the corrected guard accepts it. Strictfp classes with primitive-int,
private collector or missing bare constructors are rejected. Existing tests
also retain ordinary/generic positives, all prior invalid forms, failed
inspection, and a class whose initializer/constructors throw if executed.
Validate/build integration still rejects invalid ABI before packaging.

The October 16 complete regression evidence is reused, **not rerun or claimed
as a fresh result**:
`knowledge/context/reviews/framework/def019-view-reverse-fidelity-2026-10-16.md`
records 2,932 passed, 15 skipped, one deselected. This small text-recognition
correction touches no renderers, localization, content, templates, resource keys,
relationship semantics, adapter source or artifacts; it does not reopen the
global-default or key-collision escape paths.

Reviewed SHA-256:

```text
4bd809445f51e695a9c0a3a87d5d20ac210b8899af0d66f2ad2d273f03b52837  src/vcfcf_managementpacks/sdk_builder.py
39e7802039e8637ef5c070bc90b997388668a626887d20c15ca9706d0e1a43cf  tests/managementpacks/test_sdk_entry_constructor_contract.py
```

If shipped as-is: legitimate Java 11 strictfp entry classes with the exact
collector/controller ABI no longer fail SDK validation merely because javap
prints `strictfp`; incompatible classes still fail. This is tooling approval,
not live collector or deployment qualification.

The reviewer edited only this report. No source changes, staging, commits,
downloads, installation, publication or live calls were performed.
