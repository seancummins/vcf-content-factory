# RDM fixture schema diagnostics — independent review

Verdict: **APPROVE** — zero BLOCKING findings.

Scope: offline review of the fixture-export diagnostic changes in
`scripts/rdm_lab_probe.py` and deterministic tests in
`tests/test_rdm_fixture_schema.py`. Existing exporter and diagnostic tests were
also independently rerun. No live queries, credential reads, adapter edits,
commits, or fixture exports were performed by this reviewer.

## Findings and evidence

- `FIXTURE_SCHEMA_VALIDATION / FAILED` previously conflated ResourceKey shape,
  identifier value/flag failures, RDM device/identity failures, JSON decoding,
  and serialization errors. The new codes distinguish verified conditions;
  field paths are a closed set of structural strings, never API-returned names,
  values, indices, fingerprints, or exception messages. The CLI rechecks both
  code and field allowlists at the rendering boundary.
- The Suite API contract in `reference/docs/operations-api.json`, schemas
  `resource-identifier` and `resource-identifier-type`, permits omitted values
  and omitted uniqueness flags (with platform default-true semantics). The
  unchanged E2.1 `RuntimeFixture` parser is stricter: every identifier must
  contain a nonblank string value and an explicit Boolean flag. Accordingly,
  an API-valid response may be unrepresentable under the current fixture
  contract. The diagnostic helper correctly describes a fixture-contract
  rejection, not necessarily a malformed Suite API response.
- Synthetic API-shaped responses with six identifier entries preserve every
  name, value and flag. Nonidentity API metadata is projected away as before.
  Tests reproduce missing, null and empty nonunique values without dropping,
  coercing or repairing them. Actual Java-parser tests independently confirm
  rejection of these variants, including blank values.
- No identity-matching rule changes were found: exact vCenter UUID plus VM
  MOID correlation, uniqueness-bearing scope, one VM and one RDM, and complete
  foreign-key preservation remain fail-closed. Existing Java UUID, conflict,
  string and parser-bound checks remain authoritative. The output writer and
  its exclusive `0600` creation/cleanup logic are unchanged.
- Secret-bearing exception messages and causes do not reach the CLI. New
  tests exercise every allowed structural field plus an injected untrusted
  field. Existing stage redaction, output/no-overwrite, failure cleanup and
  parser-rejection/no-write tests still pass.

## Independent verification

- Explicitly supplied the existing local SDK path and ran all four probe test
  modules: **148 passed**, including compilation/execution of the actual E2.1
  Java parser against synthetic payloads. The final rerun also verified missing,
  null and empty required mapping fields are rejected by Java, and serialization
  failure preserves token cleanup without writing a fixture.
- `bash scripts/validate-changed-content.sh --all`: **passed**, exit 0.
- Reviewed the unchanged Java parser and the vendor API schema directly;
  no SDK artifact was copied or bundled.

## Limits and disposition

The historical sanitized reports' absent-or-empty nonunique values, reported
by the orchestrator, establish a plausible and reproducible incompatibility,
not the exact condition in the failed current export. No new live retry was
authorized or executed in this review. A retry may now identify the specific
Python-side field/rule; UUID, conflicting-instance and other Java-only failures
still correctly report `JAVA_PARSER_VALIDATION / PARSER_REJECTED` without
invented detail or a second, drifting implementation of the Java validator.

If shipped as-is, operators receive actionable, sanitized diagnostics and the
same fail-closed acceptance behavior. An absent/empty identifier will still
block export: deleting it, assigning a value/default flag, or changing the
adapter is not authorized by this diagnostic-only correction. Resolving that
fixture-contract incompatibility requires a separate evidence-based decision,
not weakening this export gate. No live persistence or readiness is established.
