# F2.2 — independent live GitHub configuration review

Date: 2026-10-15. Role: independent `sdk-adapter-reviewer`, applying
`knowledge/context/authoring/guide_reviewer_doctrine.md`. Scope: authorized
read-only GitHub GET inspection and deterministic local CI tests; no repository,
workflow, ruleset, runner, Git ref or VMware mutation.

## Verdict

**CHANGES REQUESTED for full F2 completion.** Repository bootstrap and hosted
main source validation are independently confirmed, but the approved F2
operator checklist is not fully implemented. **F2 is partially complete;
NO-GO for protected SDK activation, release tags, publication or deployment.**
This is not a finding that SDK execution is currently enabled: independent
deny layers remain in force. The changes requested below require separate
authorization; this review neither implements nor authorizes them.

If treated as fully complete today, operators would inherit PRs mergeable
without an independent approval, broad Actions permission, an active candidate
workflow rather than the mandated server-side disablement, no PR-event proof
and no active factory registry entry. Source checks passing do not satisfy those
external acceptance gates.

## Independently reproduced live evidence

All GETs below succeeded unless explicitly noted. Inspection used the named
repository `seancummins/vcf-content-factory-sdk-rdm-topology`; no credentials or
secret values were requested or printed. The live main SHA is
`160f6461541ca312708ee880f3b5837b7ccfd312`, exactly the approved checkpoint.
Repository owner type is `User`, visibility `public`, default branch `main`,
not archived or disabled. There are no tags or releases. Public visibility is
acknowledged in the current user brief; the older F2 plan and live policy's
`bootstrap_visibility: private` describe a different baseline. Historical
publication approval was not inspected, so no unauthorized-disclosure claim or
permission to revert visibility follows from this discrepancy.

| Surface / GET endpoint relative to repository API | Independent observation |
|---|---|
| `rulesets/25167815`, `rules/branches/main` | Active default-branch ruleset, no bypass actors; PR required, `static` required from integration 15368, deletion and non-fast-forward prohibited. Required approvals **0**; stale-review dismissal, CODEOWNER review, last-push approval and thread resolution all false. Strict up-to-date status policy false. |
| `rulesets/25168035` | Active tag rule matching `refs/tags/v[1-9]*`, no bypass actors. Update, deletion and non-fast-forward rules present; **no creation restriction**. |
| `actions/permissions` | Actions enabled, `allowed_actions: all`, `sha_pinning_required: false`. |
| `actions/permissions/workflow` | Default token permissions `read`; workflow PR-review approval false. |
| `actions/workflows` | Both `check-source` and `protected-release-candidate` are **active**. |
| `actions/variables` | Zero repository variables. Direct `actions/variables/RDM_RELEASE_ENABLED` GET returns 404, consistent with absent variable, **not an explicitly false value**. No inaccessible response is reported as a passing configuration. |
| `actions/runners`, `environments` | Zero repository runners and zero environments; no protected SDK environment/runner is configured. |
| `actions/runs`, `pulls?state=all` | Exactly one workflow run, main `push`; zero PRs. PR-event execution has not been demonstrated. |
| `actions/runs/38751025464/jobs` | Successful `static`, GitHub Actions runner group, `ubuntu-latest`; deterministic no-SDK and shell-syntax steps succeeded. |
| `commits/<exact SHA>/check-runs` | One completed successful `static` check, app `github-actions`, app ID **15368**, matching required-check issuer. |
| `actions/runs/38751025464/artifacts` | Zero artifacts. This run did not build or upload a PAK. |

Hosted evidence: [successful main run 38751025464](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/actions/runs/38751025464),
job 116477144822, started 2026-10-15T14:23:59Z and completed
2026-10-15T14:24:07Z, exact checkpoint SHA above. Both checkout and Python setup
step pins match the reviewed workflow. This is a source-validation result,
not an SDK/package/persistence result.

The exact live commit's three configuration files were independently fetched
through `contents/<path>?ref=<exact SHA>`:

- `.github/workflows/check-source.yml`: PR/main push only, hosted Ubuntu,
  explicit read-only contents, full-SHA action pins, no persisted checkout
  credentials, protected environment, SDK variables, secret references,
  self-hosted runner, cache or upload. The normal ephemeral checkout token is
  not a protected SDK/release secret.
- `.github/workflows/build-pak-on-tag.yml`: only matching tag pushes; exact
  repository, tag/protected-ref and `vars.RDM_RELEASE_ENABLED == 'true'` job
  checks; named protected environment and runner group. No publication step
  and only `contents: read`.
- `ci/release-policy.json`: `release_enabled: false`; SDK/buildkit/toolchain
  approval pins unset. The source helper's first context check rejects this
  policy before compilation/dependency access; approved source and runner
  checks remain additional gates. Missing repository variable cannot satisfy
  the job's exact `'true'` test. No release run was observed.

The current workflow source therefore remains credential-free for hosted
checks and fail-closed for the intended SDK candidate. A disabled policy is
not equivalent to the F2 checklist's explicit server-side workflow disablement.
No workflow or API mutation was performed to test these gates.

## Acceptance gaps and authority

1. **BLOCKING — independent main review is not enforced.** The F2 operator
   plan section 5 requires at least one independent approval, stale-review
   dismissal and conversation resolution; observed approval count is zero and
   those protections are false. CODEOWNER review is also false. PR requirement
   alone is not independent review. Smallest remedy: separately approve and
   configure the specified main controls and eligible independent reviewer,
   then re-audit. Do not self-approve or silently reduce the approved baseline.
2. **BLOCKING — hosted-only server configuration differs from the checklist.**
   F2 sections 3–4 require the exact two selected action pins, explicit
   `RDM_RELEASE_ENABLED=false` and server-side disablement of the candidate
   workflow. Observed all-actions permission, absent variable and active
   candidate workflow do not meet that baseline. These are acceptance gaps,
   not proof of a present SDK leak. Remedy requires authorized settings changes
   or an explicitly reviewed policy revision; no waiver is inferred here.
3. **BLOCKING — PR-event verification is missing.** The F2 checklist and
   acceptance section require successful main **and PR** source-check evidence.
   Only the main push has run. An authorized harmless PR exercise is still
   needed; this audit did not create one.
4. **BLOCKING — registry acceptance is pending.** Read-only inspection of
   `knowledge/context/managed_paks.md` finds no RDM entry. F2 requires the
   post-creation registry addition with independent parser/content validation.
   Repository existence alone does not register it. Add nothing without
   separate authorization, and reconcile the now-public source description.

These are external bootstrap acceptance findings, not Java/PAK implementation
defects. RULE-012 (`knowledge/rules/release-gate-defects.md`) registry check:
there is no open defect affecting `rdm-topology-poc` and no downstream local
registry is present. Surviving security/gate findings should be registered by
the orchestrator under an appropriate CI/repository scope before any future
artifact build is accepted; the reviewer does not edit the registry.

**Release-tag creation remains unrestricted by the ruleset.** This means
otherwise authorized tag-writing actors can create matching tags; it does not
mean anonymous visitors can write tags. Update/deletion protection establishes
immutability after creation, not release authority. The glob is also broader
than a semantic version parser; runtime checks provide the stricter format.
F1's named-maintainer creation restriction is not satisfied. This is an
explicit F3 activation blocker; absent SDK enablement does not waive the
future creation-authorization gate. Current tag protection is useful but
insufficient evidence of approved protected-release governance.

Visibility-baseline documentation needs reconciliation to the current public
brief before a completion claim; no visibility mutation is requested by this
review. Existing private-bootstrap regression tests passing do not validate
the public live setting.

## Independent offline rerun and limitations

`python3 -m unittest discover -s ci/tests -v`: **24 passed**. The printed
candidate filename/checksum is generated by a temporary synthetic ZIP fixture,
not a new proprietary-SDK build or releasable PAK. No Java behavior or source
changed, so SDK compilation/build/comparison was not repeated for this live
settings audit. Prior F0.5/F1 package results remain historical evidence only.

No hosted workflow was triggered, Git ref changed, repository configuration
written, SDK binary opened, dependency installed, credential obtained or VMware
endpoint contacted. This report is the reviewer's sole write target.

Cross-review: read the completed orchestrator record at
`knowledge/context/reviews/rdm-topology-poc-f22-github-audit.md`. Its observed
branch/tag/workflow/checkpoint findings and incomplete-F2 disposition agree
with the independent GETs above. No material reporting discrepancy found.
The added commit-tree/local-factory/secrets-metadata observations are the
orchestrator's evidence, not separately repeated claims of this reviewer.

Before F3: close F2 discrepancies with explicit approvals; restrict release-tag
creation; approve independent environment reviewers and enforceable personal-
account runner isolation (do not assume organization runner groups work for a
`User` owner); provision/licence the SDK outside Git; pin SDK/buildkit/toolchain
digests; approve 1.x+ metadata/source; separately authorize candidate execution,
verify structural comparison and provenance, then separately consider publication
and the deployment-persistence experiment. None is authorized by this review.
