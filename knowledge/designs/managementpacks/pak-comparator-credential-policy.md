# F0.4 — Java SDK PAK credential comparison policy proposal

Date: 2026-10-14. Status: design for independent review; implementation is
not authorized by this document. This proposal changes neither RULE-005 nor
the recorded F0.1/F0.3 results.

## Root cause and evidence

In `src/vcfcf_managementpacks/pak_compare.py`, `_compare_describe_xml`:

- Lines 579–585 issue BLOCKING code **D1** whenever the two descriptors
  disagree about the presence of `AdapterKind/CredentialKinds`.
- Lines 624–631 issue BLOCKING code **D6** whenever the normalized type-7
  resource kinds disagree about the truthiness of `@credentialKind`.
- Lines 586–597 also issue BLOCKING **D2** for credential-kind count
  differences and WARNING **D3** for credential-field count differences.

F0.1's displayed **B1/B2** are sequential report labels for D1/D6; they are
not stable rule identifiers. The helper `_describe_credential_kinds_info`
extracts only presence and counts. `_describe_resource_kinds_summary` reads
the credential reference but does not read `isCredentialRequired`. No
credential-reference resolution, requiredness evaluation, or adapter-identity
test governs D1/D6. Identical malformed credential metadata in two artifacts
can therefore escape these equality checks.

The normative evidence is the existing clean-room schema digest
`knowledge/context/cleanroom-spec/spec/02a-describe-xsd-canonical.md`, sections
“Top-level” and “ResourceKind attributes”: `CredentialKinds` and
`credentialKind` are optional, and omitted `isCredentialRequired` has
documented effective value true. An explicit false permits creation without a
credential. F0.2's independent review records corroborating schema inspection;
F0.3's independent review verifies the explicit false correction in the POC.
These are schema and static contract findings; target-appliance behavior
remains untested.

`knowledge/lessons/pak-install-reliability.md`, Failure 3, warns specifically
against an empty credential kind for a no-auth pack. Its correction is to omit
the credential block. It does not establish a universal credential requirement.

Synology's authenticated DSM adapter legitimately declares credentials and
binds `synology_credentials` to its type-7 resource. The fixture-only RDM POC
legitimately declares none and explicitly sets `isCredentialRequired="false"`.
The approved reference demonstrates packaging and foreign-parent architecture;
it does not prescribe the POC's authentication design.

## Existing mechanisms and reuse

`compare_paks(factory, reference)` and `compare_pak_directory(factory, dir)`
have no policy mode. “Directory mode” means compare all files and select the
lowest (BLOCKING, WARNING, INFO) score; it is not an upgrade/first-release
distinction. Both the factory CLI and generated buildkit CLI use those
functions. `sdk_builder._run_pak_compare` also uses directory selection.

The build-only `--pak-compare-warn-only` escape is dev-only and cannot satisfy
RULE-005; it must not implement this proposal. There is no reusable complete
schema-aware credential validator in the comparator. Existing XML readers,
`Finding` codes, severity ordering, fail-closed gate, and synthetic PAK test
helpers can be reused. `DescribeBuilder` and Tier 1 no-auth packaging already
support omission, but are generators rather than contract validators.

## Proposed semantics

Introduce a keyword-only policy parameter shared by the Python API, factory
CLI, generated buildkit CLI, and automatic build gate. Proposed public choices
are `legacy`, `upgrade`, and `structural`, with `legacy` as the default.
These names and flags are proposals, not commands available today.

| Policy | Intended reference | Credential difference semantics |
|---|---|---|
| `legacy` (default) | Existing callers | Preserve current findings, severities, ordering and exit behavior. No automatic migration based on adapter name or version. |
| `upgrade` (explicit) | Prior approved artifact of the same adapter | Validate the credential contract independently; retain existing D1/D2/D6 BLOCKING rules and add checks for credential-contract regressions hidden by equal counts. |
| `structural` (explicit) | Independently approved, different native Java SDK adapter for a first release | Validate both credential contracts independently; report valid D1/D2/D6 differences as INFO with stable codes, paths and both sides' contract evidence. Keep all other existing rules, including D3 and the three F0.1 WARNINGs, unchanged. |

All new policies preserve the real gate: any BLOCKING finding or inability to
perform the required evaluation gives nonzero exit. No suppression list,
adapter-specific exception, score override, or warning-only release path is
introduced. INFO in these modes means an explained semantic difference, so
report headings must stop calling every INFO finding purely cosmetic.

### Credential validation before comparison

Implement one bounded credential-contract reader and validator for the two
new modes. This is not a claim to perform complete XSD validation. It must:

1. Parse supported XML namespaces and enumerate resource kinds and credential
   definitions without selecting the first ambiguous adapter. Require exactly
   one native Java adapter and its matching type-7 resource per input for
   this initial policy. Missing/unparseable descriptors, duplicate archive
   members or ambiguous adapter descriptors are BLOCKING; unsupported package
   families cannot use `structural` to obtain a passing result.
2. Read `isCredentialRequired` as an XML Schema boolean: true/1 and false/0,
   with XML whitespace normalization. Omission is effective true; an empty
   or otherwise invalid value is BLOCKING. For a type-7 instance with no
   usable credential binding, require explicit false. This is a conservative
   factory configuration rule grounded in the documented creation default;
   do not claim the XSD itself enforces that cross-field constraint.
3. Resolve every present `credentialKind` comma-separated reference on every
   resource kind against declarations in its own descriptor. Trim token
   whitespace; empty tokens, duplicate tokens or unresolved references are
   BLOCKING even when the resource says credentials are optional. A present
   empty attribute is malformed, not equivalent to an omitted attribute.
   Requiredness-without-binding is checked on type-7 instances, not inferred
   for every data resource that inherits the default.
4. Reject duplicate/empty credential-kind and credential-field keys, duplicate
   credential containers, missing schema-required attributes, invalid field
   boolean/type declarations, and a credential kind with zero fields.
   Check required key, nameKey and field dispOrder attributes. CredentialField
   `type` is optional: validate its enumeration only when present; omission
   must not be reported as a missing required attribute. Apply boolean defaults
   only where documented, retaining omission as distinct when no default is
   established. Legitimate enum field children
   remain supported. Reject an empty `CredentialKinds` container under a
   named factory no-auth policy, explicitly distinguishing that rule from XSD
   grammar (the container itself can contain zero kinds in the XSD).
5. Accept a type-7 instance with valid declared bindings and requiredness
   true, false or omitted. Optional authentication with a valid credential
   definition is supported. Unbound but otherwise valid credential
   declarations merit WARNING rather than a false claim of remote use.
6. Validate each input independently and label findings as candidate or
   reference. A malformed reference cannot qualify a candidate. Invalid
   metadata must remain BLOCKING even when both files have the same defect.

The validator checks declaration integrity, not secrets, authentication
success, or whether application code consumes the declared fields. That last
question remains an SDK review responsibility. The comparator must not print
credential defaults or any supplied credential values.

### Upgrade regression checks

`upgrade` requires manifest/descriptor agreement on adapter identity and
matching identity between the two artifacts; a different adapter is BLOCKING.
Retain historical strictness for D1/D2/D6 even for schema-valid authentication
model changes, since installed configuration may need migration.

Compare credential kind keys, referenced bindings, field keys/types, effective
required flags and masking flags. Removed/renamed bindings or fields, changed
field types, optional-to-required changes (including new required fields),
instance false-to-true changes and loss of password masking are BLOCKING.
An additive optional field remains visible with the existing field-count
WARNING. Intentional incompatible upgrades need a separate migration decision;
this increment introduces no acceptance mechanism for them.

### Structural comparison eligibility and reference handling

`structural` requires different, internally consistent adapter identities,
the same native Java packaging family and a recorded reviewer decision on
target Operations compatibility and structural relevance. Metadata checks do
not automatically prove that relevance or legal availability.

Initially require one explicit reference PAK and SHA-256 in this policy.
Reject structural directory selection; this prevents a lower score from
choosing a reference other than the one reviewed. Automatic first-release
build gates must receive that same explicit policy/reference/digest; they
cannot first fail in legacy mode then be advertised as passing because a
separate manual command used another policy. Existing legacy directory mode
and closest-reference behavior remain unchanged.

Reports record policy/version, candidate/reference SHA-256, adapter identities,
the schema-contract source/version, stable finding codes and structural paths,
counts and gate result. Report the original presence/count difference plus
why its credential contract is valid. Hash mismatch, absent reference,
unknown policy or unsupported descriptor is an error, never a fallback to a
more permissive mode. The approved release process supplies the exact
reference through the buildkit facility, outside the adapter repository.

## Deterministic regression-test matrix

Use synthetic ZIP/descriptor fixtures with no SDK binary, secrets, network or
customer inventory. Test stable codes/severities independently of report B/W/I
numbering. Generate fixtures covering namespaced XML and equivalent boolean
lexical forms; reverse candidate/reference roles where applicable.

| Case | Expected new-policy behavior |
|---|---|
| Valid credentialed candidate/reference | No credential-validity blocker; existing structural differences retained. |
| Explicit false, no block/reference versus valid credentialed adapter | Structural D1/D6 INFO; upgrade rejects differing adapter identities; legacy retains D1/D6 BLOCKING. |
| Two valid explicit credential-free descriptors | No credential-presence finding in structural mode; upgrade accepts unchanged same-adapter contract. |
| No binding and requiredness true or omitted | BLOCKING on type-7 even if reference repeats the defect. |
| Optional instance with a valid binding | Valid; no requirement to use authentication at runtime inferred. |
| Dangling reference, empty binding, trailing/duplicate token | BLOCKING regardless of false requiredness or equal defects in reference. |
| Empty kind or container, duplicate keys/containers, missing field metadata | BLOCKING with schema-versus-factory rule origin identified. |
| Boolean false/0, true/1 and surrounding XML whitespace | Equivalent effective values; invalid/empty values BLOCKING. |
| Valid multiple kinds with different counts across adapters | Structural D2 INFO; legacy D2 BLOCKING; unchanged D3 WARNING if field totals differ. |
| Same-adapter removal/rename with unchanged totals | Upgrade BLOCKING; count equality cannot hide the regression. |
| New required field, field type change, false-to-true or masking loss | Upgrade BLOCKING; structural validates each side without comparing semantic field identity across adapters. |
| Malformed candidate/reference XML or nested ZIP, ambiguous adapters, identity mismatch | Nonzero gate; no reference scoring can turn invalid evaluation into success. |
| Structural selected for same adapter or unsupported MPB/container package | Nonzero policy/eligibility error; no downgrade or automatic policy switch. |
| Reference missing, digest mismatch or structural directory invocation | Nonzero error; legacy closest-reference ordering remains covered separately. |
| Factory API/CLI, generated buildkit CLI and build gate | Same mode propagation, findings and exit status; fail on unknown mode; release still refuses warn-only. |
| RDM-shaped synthetic descriptor versus Synology-shaped synthetic descriptor | Predict D1/D6 INFO under structural policy, W1–W3 and I1–I20 retained; no package-specific name check. |
| No policy supplied | Existing test suite and baseline reports remain unchanged in legacy mode. |

## Implementation scope and acceptance

After explicit implementation authorization, route code through `tooling`:
`pak_compare.py` (contract model, policy rules and report metadata), `cli.py`
(explicit options), `sdk_builder.py` (automatic gate propagation), and
`buildkit.py` (generated CLI and gate packaging). Extend
`tests/managementpacks/test_pak_compare.py` and
`tests/managementpacks/test_pak_compare_gate.py`; add isolated-buildkit coverage
as required. Inventory all direct callers before changing signatures. CLI
documentation and `scripts/verify-tier2-sdk.sh` must carry the selected policy
and exact reference where used; existing calls keep their default. No adapter
change, dependency installation, SDK redistribution or RULE-005 edit is needed.

Acceptance requires the matrix above, unchanged legacy regression results,
factory/buildkit parity, the complete factory suite and content validations,
framework-reviewer approval under RULE-013, and SDK review of emitted findings.
Test malformed inputs on both sides and the build's automatic gate, not just
the interactive CLI. The implementation review must verify required field
metadata against the documented schema before declaring the bounded validator
complete; do not silently skip unsupported constructs.

This policy is reusable for native Java adapters with different authentication
models. It cannot establish topology persistence, instance-creation UI behavior,
upgrade migration safety beyond the inspected credential contract, or complete
platform XSD conformance. Multi-adapter and non-Java package policy is deferred
with an explicit unsupported result for the new structural mode.

The F0.3 POC remains a local development artifact. Its current comparison
remains **2 BLOCKING, 3 WARNING, 20 INFO**; historical reports retain those
severities. A future run under an implemented, reviewed policy produces a new
versioned report rather than rewriting those records. For a valid RDM/Synology
pair the proposed narrow rule change predicts **0 BLOCKING, 3 WARNING, 22 INFO**,
subject to the new independent contract checks. This prediction is not a gate
result. E1.5's approved reference selection, pinned CI tooling, zero-BLOCKING
CI comparison, official artifact, release approvals and later deployment
approval remain prerequisites.

Recommendation: implementation is justified as a general contract-validation
improvement, conditional on independent design approval. Stop at design review
in F0.4; no current comparison or deployment gate is cleared.

## Offline design checks

The existing comparator and gate tests were run unchanged with the repository
virtual environment: `PYTHONPATH=src .venv/bin/python -m pytest
tests/managementpacks/test_pak_compare.py
tests/managementpacks/test_pak_compare_gate.py -q --tb=short` reported
**38 passed, 3 skipped**. The system Python has no pytest; no dependency was
installed. `scripts/validate-changed-content.sh --all` passed, and
`scripts/path_reference_audit.sh` reported no dead references (only existing
documented standing-exception warnings). These are baseline/design checks,
not tests of the proposed modes, which have not been implemented.
