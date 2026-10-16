# RDM installation documentation — scoped SDK review, 2026-10-16

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT.**

Scope is the three corrected statements in the independent adapter repository's
`docs/installing.md`, not a renewed implementation, release or deployment gate.
Reviewed file SHA-256:
`08ccbae97dc403df54a7d34e5fd0181d2c0d864e8b29fe3b30799e7ea3ef037f`.

## Independent checks

- The endpoint/credential-free claim is now explicitly fixture-only. The
  diagnostic paragraph correctly requires two configured endpoints, an
  associated read-only vCenter credential and a separate SDK-injected
  per-instance Operations identity. The combined descriptor retains optional
  instance fields and `isCredentialRequired="false"`; conditional Java
  validation supplies diagnostic requirements. No invented authentication
  property or reuse of another integration's credential is suggested.
- Actual dispatcher `test(TestParam)` invokes identity/selection validation,
  including strict fixture parsing or diagnostic configuration validation. It
  does not configure the active route, decrypt, arm or execute discovery.
  `DiagnosticRuntime.validateSameKindConfiguration` constructs only the
  configuration boundary. The revised Test Connection wording correctly
  distinguishes accepted configuration from live API/collection proof.
- The qualification paragraph agrees with the October 16 final E4.9.3 SDK and
  security records: eight genuine external platform libraries, actual SDK
  descriptor loading and fixture lifecycles through original/dispatcher and
  both public constructors, without constructor bypass or logging/platform
  replacements on those qualified paths. Historical bypass tests remain
  supplementary. Genuine SDK root-appender ERROR messages are explicitly an
  offline logging limitation, not a logging qualification pass.
- The document retains separate authorization for installation and preserves
  E2's live topology evidence without presenting it as proof of build-13
  recovery, current collector startup, UI serialization, credential/trust
  delivery, networking or failover. The linked diagnostic procedure and
  `configuration-compatibility-e493.md` agree on these limits.
- Scoped `git diff --check -- docs/installing.md` passes. No Java test, build,
  full suite, PAK generation or live API was run for this documentation-only
  review. Existing October 16 qualification results were checked against
  actual source and frozen review hashes, not represented as newly rerun tests.

## Preservation and authority

Independent read-only checks still match the final E4.9.3 source/artifact record:

| Input | SHA-256 |
|---|---|
| Dispatcher Java source | `8abe662cbc06423c359b19cffffaa29fdc072e010f9e1bbe2642074ba5596260` |
| Combined descriptor | `e2208997811428a5368fed66b5726986126092008d68f46a1a0275667e0251df` |
| Local development build-13 PAK | `96d6293f3858bb13e625f52188b515d72e73c9f87ae46debd2ba7e50b30c68ae` |

These proprietary-input/local-build checks are not reproducible from factory
Git alone. No platform library or PAK is redistributed by this review.

Evidence: the independent adapter's `RdmTopologyDispatcher.java`,
`diagnostic/DiagnosticRuntime.java`, `runtime/RuntimeDiscoveryBinding.java`,
`ops/OperationsBinding.java`, `describe.xml` and the two linked operator docs;
[final SDK review](rdm-topology-e493-startup-sdk-review.md) and
[final security review](rdm-topology-e493-startup-security-review.md).

Authorities: SDK reviewer contract, SDK-adapter playbook's gap honesty and
docs-parity requirements, and RULE-001/005/008/012/015. The defect registry
has no open defect naming this adapter; DEF-019 remains an open tracked
factory-extractor defect and is neither closed nor waived here.

**If committed as-is:** operators receive correct mode-specific configuration
and offline qualification guidance; no new runtime, deployment or publication
claim is introduced. This approval addresses the installation-documentation
commit-readiness blocker only. No adapter source, descriptor, generated docs,
SDK libraries, PAKs, index, commit or live system was modified by this reviewer.
