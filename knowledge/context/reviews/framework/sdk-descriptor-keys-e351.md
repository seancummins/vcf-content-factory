# E3.5.1 — Independent framework descriptor-key review

Verdict: **APPROVE** — zero outstanding BLOCKING, WARNING or NIT findings.
Scope: the descriptor-key guard in `src/vcfcf_managementpacks/sdk_builder.py`,
its deterministic regression tests and SDK-contract digest. Adapter source and
live installation are separate review/authorization surfaces.

## Authority and independently verified semantics

The operator's build-8 analytics error is consistent with the supplied SDK.
Independent `javap -c -p` inspection of
`ResourceAttributeDescribe.isValidAttributeKey(String)` and
`ResourceGroupDescribe.isValidGroupKey(String)` confirms that each rejects
exactly the reserved separators `|` and `:`. Their `load` paths reject an absent
key before this check. No additional character whitelist is justified by these
methods. The proprietary local-only SDK checksum is recorded in
`knowledge/context/sdk-describe-key-contract.md`; no SDK content is redistributed.

The implementation checks individual ResourceAttribute and ResourceGroup key
segments in the canonical SDK namespace and legacy namespace-free form. It
does not reject valid composite runtime MetricKeys, unrelated identifier or
traversal keys, or foreign extension elements. Missing/unreadable/malformed XML
fails closed. This is a bounded semantic guard, not full XSD or platform
descriptor-load certification.

Both `validate_sdk_project` and direct `build_sdk_pak` invoke the guard. The
public CLI and portable buildkit dispatch to these functions; buildkit copies
the guarded builder source. The build guard precedes version stamping,
compilation, documentation generation and packaging. There is no adapter-specific
exception, comparator alteration, key rewrite or finding suppression.

## Independent verification

- New descriptor-key tests: **26 passed**, covering both separators, both
  element types/namespaces, valid nested groups, foreign extensions, unrelated
  keys, missing keys, malformed XML, CLI errors and direct-build fail-closed
  behavior. No unsupported whitelist is imposed.
- Management-pack tests: **312 passed, 8 skipped** after the correction below.
  Existing isolated buildkit tests are included in that suite.
- Full factory tests: **2,489 passed, 20 skipped, 131 deselected; one failure**,
  the previously documented unchanged
  `tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`.
  It expects the no-repository verdict but receives the conservative unknown
  verdict. No setup implementation/test changes are part of E3.5.1.
- Complete content validation: **PASS**, exit 0.
- Skill parity: **PASS**, five paired and seven Codex-only skills.
- Path-reference audit: **PASS**, with six existing documented standing-exception
  warnings. No files were staged for this read-only review.
- `git diff --check`: **PASS**.
- All seven local managed adapter descriptors and the known-good Synology wire
  reference pass the new key guard. SDK-enabled `validate-sdk` for the corrected
  RDM project passes, including compilation; javac emits its existing
  source/target-11 system-module warning.

## Finding resolved during review

The first implementation placed descriptor validation before the existing
release/warn-only prohibition. Independent full-suite testing caught a new
error-precedence regression in
`TestBuildSdkWarnOnlyGuard.test_warn_only_refused_on_release_build`.
Tooling moved the descriptor guard after that established release-policy
rejection, while retaining pre-stamp/pre-build validation. The unchanged test
and subsequent management-pack/full-suite reruns confirm resolution. This is
not an outstanding finding or a waived failure.

## Compatibility and limitations

The change is intentionally inert on standalone dashboard/view rendering and
does not alter runtime keys, localization derivation, resource identities or
relationship output. The named global-default/key-collision escape patterns
were reviewed; no such transformation is introduced. No assembly/template
output change or template-version bump is required. A formerly accepted SDK
descriptor segment containing a reserved separator now fails locally rather
than producing another uninstallable PAK (RULE-005, RULE-013).

If shipped as-is: invalid descriptor key segments fail before build output;
valid grouped descriptors and composite Java MetricKeys retain their meanings.
Offline checks do not prove controller registration or successful installation.
No live access, SDK redistribution, adapter build regeneration, Git staging,
commit, push, release or topology mutation was performed by this reviewer.
