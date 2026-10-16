# F2.2 — live GitHub bootstrap configuration audit

Date: 2026-10-15. Observation checkpoint recorded at 14:56:57 UTC.
Scope: authorized read-only GitHub API inspection and local evidence/reporting.
No GitHub setting, ref, workflow, source, remote, runner or release was changed.
No VMware access, SDK build, installation or deployment occurred.

## Result

**Audit completed; F2 is PARTIALLY VERIFIED, NOT COMPLETE.** Repository upload
and hosted main CI are proved. Several approved configuration/checklist gates
remain unmet. **NO-GO for protected release activation, tags/releases or
deployment.** Independent reviewer verdict: **CHANGES REQUESTED for full F2
closure**, not a claim that SDK execution is currently enabled.

The current user brief identifies the repository as public. That matches the
live API, but differs from the earlier approved private-bootstrap baseline and
the committed `bootstrap_visibility: private` declaration. Record/reconcile
the visibility decision before claiming checklist conformance. This audit
does not infer an unauthorized disclosure, retrospectively approve an earlier
visibility change, or authorize changing it back.

## Identity, history and source checkpoint

| Item | Observed value |
|---|---|
| Repository | [seancummins/vcf-content-factory-sdk-rdm-topology](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology) |
| Owner / type | `seancummins` / `User`; account plan not inspected |
| Visibility / default branch | `public` / `main`; not archived or disabled |
| Live main | `160f6461541ca312708ee880f3b5837b7ccfd312` |
| Commit parent / tree | `cb2292db90d5d0a8da530e9c187986307daf0d2b` / `7934a5d021534cd516dc822d5904d04c95b59753` |
| Local adapter | Same HEAD; clean; `main` tracks `origin/main`, local tracking SHA equals live main; origin matches approved owner/repository |
| Local factory | `96215d6154c85d1e159ce79bfd11ce5d6adcf163`; clean at audit start |
| Live recursive tree | Not truncated; same audited commit/tree, 30 source/document blobs; no new SDK/PAK payload introduced relative to approved checkpoint |
| Tags / releases | Both empty, including releases visible to the authenticated observer |

Source provenance remains the approved checkpoint described in
`knowledge/context/reviews/rdm-topology-poc-f2-checkpoint-audit.md`; this is not a
new generic secret scan. GitHub commit/tree identity matches that exact approved
source. No fetch, clone, push, tag or local Git configuration write was used.

## Branch ruleset 25167815 — Protect main

[Observed branch ruleset](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/rules/25167815):
`enforcement: active`, branch target `~DEFAULT_BRANCH`, no exclusions or bypass
actors; current-user bypass is `never`. With default branch `main`, the effective
`/rules/branches/main` response independently confirms these four rules:

- `pull_request`: changes must be associated with a PR.
- `required_status_checks`: context `static`, integration ID `15368`.
- `deletion`: deletion blocked.
- `non_fast_forward`: force pushes blocked.

**These requested basic controls PASS.** The check's issuer is bound to GitHub
Actions, not an arbitrary status provider. Targeting the default branch is
dynamic; changing that default later changes which branch this ruleset covers.

However, the additional approved F2 review controls do not pass:

| PR/check parameter | Live value | Interpretation |
|---|---|---|
| `required_approving_review_count` | `0` | PR does not imply independent approval; F2 requested at least one |
| `dismiss_stale_reviews_on_push` | `false` | F2 stale-review dismissal not enforced |
| `require_code_owner_review` | `false` | CODEOWNERS file exists but approval is not required |
| `require_last_push_approval` | `false` | No last-push independent approval guard; informational additional defense |
| `required_review_thread_resolution` | `false` | F2 conversation-resolution requirement missing |
| `strict_required_status_checks_policy` | `false` | Loose check policy; latest-main testing not required; not by itself an additional F2 blocker |
| `do_not_enforce_on_create` | `false` | Required check is not explicitly waived on branch creation |

No mutation was attempted to prove rejection. This verifies API-declared active
and effective rules, not a destructive force-push/delete/merge experiment.

## Tag ruleset 25168035 — Protect release tags

[Observed tag ruleset](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/rules/25168035):
`enforcement: active`, exact include `refs/tags/v[1-9]*`, no exclusions, no bypass
actors. Rules are `deletion`, `non_fast_forward` and `update`.

**Update/retargeting and deletion protection PASS for matching tags. Creation
is NOT restricted by this ruleset.** There is no `creation` rule and no other
applicable creation ruleset in the repository/inherited-ruleset listing.
Otherwise-authorized write actors can create matching tags; anonymous/public
read access does not grant that ability. No creation test was executed.

This is tag immutability, not release authorization. It does **not** fulfill
F1's carried-forward requirement to restrict release-tag creation to named
release maintainers. The F2 checklist's no-tag state is satisfied today, but
the full protected-release control is not. The limited source bootstrap can
remain release-disabled while a creation policy is designed; treating that
as a phase-boundary exception requires explicit approval, not this audit.
This is a definite F3 activation blocker, alongside the F2 gaps below.

The pattern matches a prefix, not full semantic-version syntax; `v0*` and other
tags are outside this ruleset. The helper independently enforces strict 1.x+
version/build/tag agreement. No development-version tag was found.

Future creation authorization must not accidentally waive existing immutable
update/deletion rules by granting a broad bypass to this same ruleset. Design
those permissions and actor/account support separately before activation.

## Hosted CI and workflow permissions

Verified [check-source run 38751025464](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/actions/runs/38751025464):

- Event `push`, branch `main`, attempt 1, exact SHA `160f6461541ca312708ee880f3b5837b7ccfd312`.
- Completed **success**; created `2026-10-15T14:23:56Z`, updated `14:24:08Z`.
- [Job static, ID 116477144822](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/actions/runs/38751025464/job/116477144822)
  completed success; runner group `GitHub Actions`, labels `[ubuntu-latest]`.
- Both pinned actions, deterministic no-SDK check step and shell syntax step
  completed success. No artifacts were emitted (`total_count: 0`).
- Commit check-run name `static`, app slug `github-actions`, app ID `15368`:
  exact match for the ruleset's required context and integration.
- One source workflow run exists, on push. No PR-event workflow result or PR
  exists in the independently inspected all-state PR list. PR-event acceptance
  is **not demonstrated**. The successful run predates ruleset creation, so it
  is not proof that a protected PR merge has been exercised.

The [pinned hosted workflow](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/blob/160f6461541ca312708ee880f3b5837b7ccfd312/.github/workflows/check-source.yml)
has PR/main triggers, hosted Ubuntu only, `contents: read`, no persisted checkout
credentials and full-commit action pins. It references no SDK/release secret,
protected environment, private runner, cache or upload step. Synthetic tests
mock external commands; a fixture ZIP is not an SDK build or published PAK.

Repository workflow defaults: `default_workflow_permissions: read`,
`can_approve_pull_request_reviews: false` — **PASS**. This controls the workflow
token; it does not require a human to approve a PR.

Repository Actions policy: `enabled: true`, `allowed_actions: all`,
`sha_pinning_required: false`. The existing workflows are pinned, but the
repository does not enforce the F2 exact two-action allowlist. **Checklist gap**:
allowing every action is broader than the approved selected-action setup.

## Release denial: observed state, not authorization

| Layer | Live observation | Consequence |
|---|---|---|
| Release workflow service state | `active`, workflow ID `385639726` | F2 explicitly required server-side disablement; not satisfied |
| Workflow trigger | Tag pushes matching `v[1-9]*` only; no PR/main/manual trigger | Ordinary hosted main/PR checks do not run the SDK builder |
| Repository variables | `total_count: 0` | `RDM_RELEASE_ENABLED` is absent, **not explicitly false**; comparison to `'true'` denies the candidate job |
| Protected environment / runners | Both `total_count: 0` | No release environment/reviewer protection or self-hosted SDK runner established |
| Repository secrets | Metadata count `0`; no values retrieved | No repository release/SDK secret configured |
| Committed policy | `release_enabled: false`; SDK/buildkit/toolchain approval pins null | Helper rejects context before dependency use or compilation |
| Helper prerequisites | Exact approved source SHA, protected tag, main ancestry, clean checkout, runner approval, SDK digest/scope and strict 1.x+ version required | Additional independent gates remain unmet |
| Release run history | `total_count: 0` | No observed protected candidate execution |
| Published output | Zero tags/releases; hosted artifacts zero | No development PAK or approved release published through these paths |

The [exact committed policy](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/blob/160f6461541ca312708ee880f3b5837b7ccfd312/ci/release-policy.json)
and [release workflow](https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology/blob/160f6461541ca312708ee880f3b5837b7ccfd312/.github/workflows/build-pak-on-tag.yml)
therefore prevent current protected release execution. **An active workflow is
not equivalent to an enabled SDK build**, and an absent enable variable is not
evidence it was explicitly set false. No tag or helper execution was attempted.
The named runner group is only source configuration, not a provisioned resource.
These conclusions apply to the observed configuration and SHA; future writers
can change source/settings, especially without an enforced approval minimum.

## Approved F2 checklist disposition

| Checklist control | Result |
|---|---|
| Reviewed local preparation commit and exact-tip audit | PASS, retained checkpoint and prior independent audit |
| Independent repository / owner / main / remote tracking | PASS |
| Initial private visibility baseline | DEVIATION: public matches F2.2 brief; historical decision/baseline reconciliation still needed |
| Main-push hosted no-secret CI | PASS with exact run/job/check evidence |
| PR + static + no deletion/force push | PASS |
| Independent approval, stale-review dismissal, thread resolution, CODEOWNER enforcement | NOT SATISFIED as above |
| Selective action permissions | NOT SATISFIED; all actions allowed |
| Explicit false enable variable / server-disabled candidate workflow | NOT SATISFIED; missing variable / workflow active, though execution denied |
| Hosted PR-event exercise | PENDING; no observed PR/run |
| Factory registration and independent active-entry validation | PENDING; active `knowledge/context/managed_paks.md` has no RDM entry |
| No release runner / no tags or releases | PASS for the release-disabled F2 phase |
| Named release-tag creation authority | NOT SATISFIED; carried-forward release/F3 prerequisite, not waived |

**F2 completion: INCOMPLETE.** Do not equate a successful main-push test and
two active rulesets with complete adherence to the approved checklist.

## F3 prerequisites — no implementation authorized here

1. Reconcile/approve F2 checklist deviations or obtain narrowly documented,
   independently reviewed phase-boundary decisions; do not silently waive them.
   The independent review identifies four closure findings: enforced review
   controls; Actions/release-disable checklist drift; PR-event evidence; registry.
   Before accepting a future artifact build, register any surviving gate/security
   defect under the appropriate CI/repository scope per RULE-012; this read-only
   increment does not authorize registry changes.
2. Establish creation authority for approved release tags while preserving
   update/deletion immutability. Review existing bypass scope and the exact
   protection pattern, and retain no 0.x publication.
3. Design account-compatible, technically enforced SDK runner admission.
   The owner is now verified as `User`; F1 organization runner groups must not
   be assumed available. No runner may execute untrusted PR code or have VMware
   routes/credentials. Labels alone are not admission control.
4. Approve independent release reviewers/environment controls and exact source
   approval, subject to account/plan capabilities; no unsupported enforcement claims.
5. Approve licensed SDK provisioning outside Git/build/upload roots and its
   SHA-256; approve full F0.5-capable buildkit/Synology/toolchain digests and
   acquisition/image provenance. No SDK upload or redistribution.
6. Separately approve 1.x+ metadata/source/tag, perform a protected CI candidate
   build and structural comparison, inspect all findings and SDK exclusion,
   verify PAK/sidecar/provenance; publication and deployment need their own approvals.

## Evidence collection, review and limitations

All target API calls used authenticated `gh api --method GET`; no token values
or credential profiles were displayed/read. Repository/commit/tree, rulesets
including parents and effective main rules, Actions permissions/workflows/runs/
jobs/checks/artifacts, variable/secret counts, runners, environments, tags and
releases were inspected. Source was read at the exact SHA, not a moving branch.
Lists contained fewer than 100 records (or were empty); no pagination tail or
truncated tree was treated as complete. Only nonsecret selected metadata was
retained here. Missing enablement was confirmed by the successful empty variable
list, not inferred from a permission-ambiguous 404.

Governance: F1 protected-CI assessment, F2 operator plan, approved checkpoint
audit, RULE-008/014/015 and the independent-repository lesson. GitHub documents
that PR requirements and approving reviews are separate, and creation/update/
deletion are separate rules:
[available rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets),
[rules REST schema](https://docs.github.com/en/rest/repos/rules).

Independent review:
`knowledge/context/reviews/rdm-topology-poc-f22-github-review.md`.
Its live reruns confirm the same findings and re-ran 24 offline CI tests; that
is not an additional live SDK or relationship-persistence experiment. No open
RDM-affecting implementation defect was found in the existing defect registry;
the reported gaps are external acceptance/control gaps. No registry was modified.

Report validation: full seven-package content chain and skill parity passed;
path-reference audit is clear with six existing standing-exception warnings;
whitespace checks passed. Adapter remains clean at the same SHA. Only these
two factory audit/review documents are new and uncommitted; no full factory
pytest or Java/SDK build was required or represented as newly passed.

This is a point-in-time read-only audit, not a permission-bypass test or a
license/publication approval. Only local audit/review documents were written;
no prior records, adapter files, Git refs/remotes or GitHub configuration changed.
