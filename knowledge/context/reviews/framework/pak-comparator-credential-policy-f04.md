# F0.4 — independent comparator credential-policy design review

Date: 2026-10-14. Reviewer: `framework-reviewer`, independent Codex context.
Scope: `knowledge/designs/managementpacks/pak-comparator-credential-policy.md`
and its evidence/caller contracts. This is a design review; no comparator,
adapter, PAK, rule, release or VMware system was changed by the reviewer.

## Verdict

**APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT.** Implementation is justified
through the tooling role, followed by a separate implementation review under
RULE-013. This verdict approves the proposal's design only; it does not
authorize implementation, clear RULE-005, or approve release/deployment.

If implemented as specified, operators can explicitly compare independently
approved native Java adapters with different authentication models while
retaining independent credential-contract checks and all unrelated structural
findings. Existing callers retain their current results by default. The
current RDM/Synology comparison remains **2 BLOCKING, 3 WARNING, 20 INFO**;
the predicted new result is not an executed gate.

## Independently reproduced evidence

| Surface | Verification and conclusion |
|---|---|
| `src/vcfcf_managementpacks/pak_compare.py`, `_compare_describe_xml` | D1 compares only `CredentialKinds` presence; D6 compares truthiness of the normalized type-7 `credentialKind`. Neither inspects `isCredentialRequired`, validates bindings, or checks adapter identity. F0.1's B1/B2 are display numbering for these rules. D2 separately blocks kind-count differences; D3 warns about field-count differences. |
| Comparator XML/archive readers | Namespace removal supports one exact namespace spelling; duplicate ZIP names are collapsed into inventory sets; adapter detection selects one candidate. Missing/unparseable reference descriptors currently produce INFO. The proposed new-mode preflight must execute before these conveniences can hide unsupported or malformed inputs. Legacy behavior remains unchanged. |
| Factory CLI, generated buildkit CLI, automatic SDK build gate | `cli.py`, `buildkit.py`'s generated CLI and `sdk_builder._run_pak_compare` all call the same comparator API. Directory selection sorts by BLOCKING/WARNING/INFO score. There is no existing upgrade/structural mode or credential-contract validator. The proposal covers each consumer and `scripts/verify-tier2-sdk.sh`, rather than fixing only the manual CLI. |
| Schema evidence | The committed canonical digest `knowledge/context/cleanroom-spec/spec/02a-describe-xsd-canonical.md` establishes optional credential container/reference and documentary default true for `isCredentialRequired`. Direct parsing of the locally available 8.3.0 XSD independently corroborated optional container/reference, required field key/order, and optional field type. The default true appears in schema documentation, not an `xs:default` attribute. |
| Prior approvals and no-auth lesson | F0.2 distinguishes schema grammar, instance creation and runtime authentication; F0.3's build-4 addendum approves explicit false plus absent credential declarations/references. `knowledge/lessons/pak-install-reliability.md`, Failure 3, explains why an empty no-auth credential kind is unsafe. The proposal retains this distinction. |
| Existing tests | Read `tests/managementpacks/test_pak_compare.py` and `test_pak_compare_gate.py` independently. Synthetic archive helpers and factory/buildkit/build-gate tests are reusable; existing fixtures do not themselves prove the new validator or policy. No PAK comparison, build, live query or implementation test was executed for this design review. |

The locally inspected XSD is local-only supporting evidence and is not a
reproducible dependency of this review. Its relevant findings are summarized
above; the committed canonical digest is the durable schema-contract source.
No restricted SDK or raw inventory was copied into the report.

## Policy and compatibility assessment

The three explicit policies avoid a global-default regression: `legacy`
preserves finding codes, order, severity and exit behavior; `upgrade` validates
both artifacts and retains historical strictness; `structural` changes only
valid D1/D2/D6 differences to explained INFO. New modes cannot silently infer
their applicability from names, fall back after an error, or treat equal
malformations as valid. INFO headings/report metadata must describe semantic
differences accurately rather than calling every such finding cosmetic.

The credential-free contract is bounded and conservative: an unbound type-7
instance needs explicit false; missing/invalid bindings and malformed declared
credentials block independently on each side. That cross-field requirement
and rejection of an empty credential container are clearly labeled factory
policy, not misrepresented as XSD constraints. Data resource kinds do not
inherit a false universal requirement to bind credentials. Valid optional
authentication and multiple credential choices remain supported.

An implementation must preserve the clarified schema distinction:
`CredentialField@type` is optional, and only a supplied type is checked against
its enum. Key, nameKey and field dispOrder are required. Boolean omission may
only receive a documented effective default; unsupported or unresolved
semantics cannot be guessed. The design explicitly includes this requirement.

Upgrade checks close the equal-count gap by comparing stable kind/field keys,
bindings, types, requiredness and masking. New required fields and removal or
renaming remain BLOCKING even if counts match. Structural mode compares
declaration integrity without requiring unrelated adapters to share those
keys. This is reusable policy rather than an RDM/Synology name exception.

The exact reference path and digest requirement prevents automatic directory
scoring from selecting an unreviewed comparator. The automatic build gate
must use the same explicit policy/reference/digest as the reported comparison.
E1.5's independently approved reference selection and CI-built official
artifact prerequisites remain intact. RULE-005's zero-BLOCKING gate and
RULE-013's implementation review remain unchanged.

## Implementation acceptance obligations

The proposed regression matrix is sufficient at design level: it covers
credentialed, explicit no-auth and optional-auth shapes; requiredness omission
and XML boolean forms; dangling/empty/duplicate references and declarations;
equal defects on both sides; same-adapter migration regressions; malformed,
duplicate and ambiguous archive inputs; family/identity errors; missing or
hash-mismatched references; and API/factory CLI/buildkit/build-gate parity.
Tests must assert stable codes and severities, not merely zero exit or B/W/I
display numbering. The isolated buildkit tests must run without importing the
factory checkout to establish portable behavior.

The future implementation review must independently rerun the full factory
suite and deterministic validation, inspect all callers, and verify no-policy
legacy results and all other current findings remain unchanged. It must
verify actual field metadata requirements against the recorded schema
contract and test automatic release-gate failure paths. This design review
provides none of those implementation proofs in advance.

Scoped offline checks performed for this review: source/caller/schema/test
inspection and deterministic XML assertions against the available local XSD.
Those assertions passed. Full framework tests, render regression and
`pak-compare` are not claimed as reviewer execution in this design-only
increment; no production implementation changed.
`git diff --check` and the report's scoped
`scripts/validate-changed-content.sh` check also passed.
