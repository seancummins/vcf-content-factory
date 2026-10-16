# RDM fixture-export diagnostics — independent review

Verdict: **APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT**.

Scope: the incremental failure-stage diagnostics in `scripts/rdm_lab_probe.py`,
`tests/test_rdm_fixture_diagnostics.py`, and the existing synthetic export tests
in `tests/test_rdm_fixture_export.py`. The earlier, uncommitted E2.2 exporter
implementation remains separate background; this review does not authorize live
execution or establish the cause of the operator's prior failure.

## Findings and evidence

- The original CLI deliberately redirected third-party output and caught every
  export exception with one fixed message. That prevented disclosure but erased
  the distinction between local Java setup, service access, correlation, parsing,
  and output failures. The presence of six service variables could not establish
  which operation failed.
- New diagnostics expose only allowlisted stage/code constants. Exception text,
  types, response bodies, subprocess diagnostics, and chained causes are not
  rendered. Unknown exceptions remain `FAILED` rather than implying rejected
  credentials. This follows `knowledge/rules/no-secrets-on-disk.md` and the
  residual-status discipline in
  `knowledge/lessons/unenumerated-exit-status-is-not-a-verdict.md`.
- Stage labels identify the failed operation, not a guessed root cause.
  Authentication rejection requires typed SOAP authentication faults or an
  observed HTTP 401; HTTP 403 has a separate authorization category. The existing
  shared client can retry authentication internally during inventory requests;
  an otherwise unclassified failure there remains `OPS_READ/FAILED`, not a
  claim about credentials. No exception-message matching is used.
- Exceptions retain causes internally where wrapping is necessary. The private
  output context and fixed CLI failure line remain in place. Nested stage
  contexts preserve a more specific inner classification.
- Identity comparison, exact identifier values/uniqueness flags, complete
  inventory requirements, one-RDM cardinality, Java acceptance before writing,
  fixed ignored destination, exclusive mode-0600 creation, and cleanup of newly
  created failed output are preserved. Token release remains best effort and
  does not replace the primary result. No adapter, comparator, shared client,
  release workflow, vendor material, or existing reporting mode was modified by
  this diagnostics increment.

## Independent offline checks

- `PYTHONPATH=src VCFCF_SDK_JAR=<local authorized SDK> .venv/bin/python -m pytest tests/test_rdm_fixture_export.py tests/test_rdm_fixture_diagnostics.py tests/test_rdm_lab_probe.py -q --tb=short`:
  **99 passed**, including the actual Java fixture parser against synthetic
  data, scoped identity/cardinality checks, secure-output cleanup, category
  propagation, internal causes, and allowlist/redaction tests covering stdout,
  stderr, logging, warnings, and captured compiler/parser output.
- Full content validation via `scripts/validate-changed-content.sh --all`:
  **passed**, exit 0.
- `git diff --check`: **passed**.

No credentials, profile values, local raw inventory, or existing real fixture
were read. No live API, installation, commit, or push was performed. Full-suite
execution and additional repository audits remain the orchestrator's checks;
render/package comparisons are inapplicable to this script-only diagnostics
change.

If shipped as-is: the operator receives a sanitized, verified failed-operation
category and bounded reason code instead of the former undifferentiated
message. The exact previous live failure remains unknown until an explicitly
authorized operator retry; success and lab correlation are not claimed here.
