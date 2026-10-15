# F2 — private independent RDM repository bootstrap

Date: 2026-10-15. Scope: offline preparation only. Commands below are an
operator runbook, **not authorization and not an execution record**.
No remote, repository, external setting, commit, push, tag or release was made.

## Decision and checkpoint

The user explicitly settled these values in the F2 brief:

| Field | Approved destination / inspected state |
|---|---|
| Owner | `seancummins`, not `sentania-labs` |
| Repository | `seancummins/vcf-content-factory-sdk-rdm-topology` |
| Initial visibility | Private; public publication needs separate approval |
| Default branch | `main` |
| Local mount | `content/sdk-adapters/rdm-topology-poc` remains unchanged |
| Adapter identity | `vcfcf_rdm_topology_poc`; no resource/relationship changes |
| Factory checkpoint | `feature/rdm-topology-mp`, `ba88ba8f9b8b4742db3384e827d1fbe2a48cf99a`; F1 assessment and review committed, factory clean at F2 start |
| Adapter checkpoint | `main`, `cb2292db90d5d0a8da530e9c187986307daf0d2b`; **F1 changes are NOT committed**, no remote, no tags |

This decision supersedes F1's proposed public Sentania-owned adapter
destination. Historical F1 records are retained, not rewritten. The registry's
Sentania naming convention is explicitly overridden for this adapter by the
user's ownership decision; its independent-repository and registration-timing
rules still apply. Upstream factory/buildkit/Synology URLs remain provenance
and dependency references, not adapter ownership or adapter remotes.

The adapter is still a local-only artifact, not reproducible from a factory
clone alone. Its relevant state and prepared behavior are summarized here and
in the independent audit; no unregistered checkout is claimed to be fetchable.
Its `.git` remains separate. No submodule, copied history or factory-tracked
adapter source is introduced.

**Checkpoint gate: NOT SATISFIED.** Do not push the old adapter HEAD expecting
CI: that commit has no F1 hosted workflow. The owner must explicitly authorize
and review a local preparation commit, then have the exact resulting tip
re-audited before uploading anything, even privately. Nothing is silently
staged or committed in F2. The example below creates one combined F1/F2
preparation checkpoint, not a retrospective assertion that F1 was committed.

## Security audit and prepared CI

See `knowledge/context/reviews/rdm-topology-poc-f2-history-audit.md` for the
complete-history audit: two commits, one branch, no tags, 53 Git objects,
30 text blobs, no unreachable objects; reflogs reach only those same commits.
Paths, blob contents, commit messages, archive signatures, credential patterns,
inventory shapes, Git modes and LFS/submodule/filter configuration were checked.
No proprietary SDK, credentials, raw inventory responses or binary build
artifacts were detected. Synthetic fixture identities and reviewed generated
text/diagram documentation are distinguished from raw lab data and build output.
The prepared tree has 30 nonignored files; its manifest hash is recorded in
the audit. This bounded scan plus manual inspection is not proof that every
possible secret encoding is absent. Any changed tip/tree requires re-audit.

Adapter-local preparation:

- Hosted `check-source.yml` remains PR/main only, `ubuntu-latest`, full-SHA
  checkout/setup-python actions, `contents: read`, no persisted Git credentials.
  It runs stdlib synthetic tests and shell syntax checks, not the SDK build.
  No SDK/release secret, environment, private runner, cache or artifact upload
  is referenced. The normal ephemeral read-only checkout token is not a
  protected SDK/release credential. Do not add repository/organization secrets.
- The disabled protected workflow, helper and policy consistently allowlist
  the new destination. Policy records private/main; these fields describe the
  intended bootstrap and do not prove GitHub's actual settings.
- `.github/CODEOWNERS` names the confirmed owner `@seancummins`; enforcement
  and independent review still require server settings and another reviewer.
- F1 exclusions and test-runner framework override are preserved. Java,
  descriptor, version (`0.1.0`, build 4), fixtures and existing PAK are unchanged.
- `release_enabled` stays false; all unapproved dependency pins stay null.
  No SDK runner or protected release environment is configured.

## Operator checklist — stop gates

- [ ] Approve the local preparation commit and review its exact file set.
- [ ] Re-audit its complete history and tip against the reviewed prepared tree.
- [ ] Separately authorize private repository creation, settings, remote and
  main-only push; approval of this runbook alone is not that authorization.
- [ ] Confirm authenticated account, repository absence, visibility and Actions
  entitlement/budget. Never respond to a permission/plan failure by making it public.
- [ ] Establish no-secret Actions permissions before the first push.
- [ ] Push only reviewed `main`, preserve its history, set default `main`.
- [ ] Explicitly disable the SDK candidate workflow after it exists on GitHub.
- [ ] Observe hosted main CI; configure branch protection; exercise PR CI.
- [ ] Only after the private remote exists, approve and validate registry addition.
- [ ] Record actual run IDs/SHAs/conclusions and server controls before F2 closes.

### 1. Local checkpoint — requires separate commit authorization

Use Bash. Review each section and stop on every unexpected result. Never
execute the whole document as an unattended script.

```bash
cd /home/scummins/Documents/vcf-content-factory/content/sdk-adapters/rdm-topology-poc
git status --short
git rev-parse --show-toplevel
git rev-parse HEAD
git log --oneline --all
git remote
git tag --list
python3 -m unittest discover -s ci/tests -v
bash -n scripts/run-tests.sh
git diff --check
```

Confirm independent root, expected old HEAD, main branch, no remote/tags and
only the reviewed pending files. After explicit commit approval, stage this
allowlist, inspect it and commit in the **adapter**, not in the factory:

```bash
git add -- .gitignore README.md scripts/run-tests.sh \
  .github/CODEOWNERS .github/workflows/check-source.yml \
  .github/workflows/build-pak-on-tag.yml \
  ci/README.md ci/defect_gate.py ci/release.py \
  ci/release-policy.json ci/tests/test_release.py
git diff --cached --name-only
git diff --cached --check
git commit -m "ci(rdm): prepare private bootstrap and disabled SDK release gates"
git merge-base --is-ancestor cb2292db90d5d0a8da530e9c187986307daf0d2b HEAD
test "$(git branch --show-current)" = main
test -z "$(git status --porcelain)"
rdm_bootstrap_sha="$(git rev-parse HEAD)"
```

STOP for independent re-audit/approval of that exact commit and tree. The
commit SHA is intentionally not invented here. Record it locally with the
approval; rerun tests. No amendment, rebase, filter, fresh `git init`, blanket
`git add .` or history replacement is needed. If unrelated files are staged,
stop for operator resolution rather than including or silently unstaging them.

### 2. Create only the private repository — after external authorization

Use the operator's own authenticated GitHub session. Do not paste tokens into
commands/chat or export SDK/lab credentials. Inspect only the login:

```bash
rdm_repo=seancummins/vcf-content-factory-sdk-rdm-topology
gh api user --jq .login
gh repo create "$rdm_repo" --private \
  --description "Fixture-driven RDM topology Java SDK proof of concept"
gh repo view "$rdm_repo" --json nameWithOwner,visibility,url
```

Require the authorized owner account and exactly the approved private name.
The operator's session needs repository creation/administration and Git push
permission for workflow files. An authentication failure is not a reason to
give the hosted workflow a write token or repository secrets.
If the repository already exists, STOP; do not adopt, overwrite or merge it
without inspecting it and obtaining approval. Do not use a template, README,
license or .gitignore initializer, `--source`, `--clone` or `--push`: create
an empty repository without new history or automatic remote/push side effects.
GitHub CLI creation uses the account's configured initial branch preference;
the explicit main-only push and post-push default-branch setting below establish
this repository's default, without changing account-wide defaults.

### 3. Configure hosted-only Actions before upload

These are external settings writes, not commands executed during F2:

```bash
gh api --method PUT "repos/$rdm_repo/actions/permissions" \
  -F enabled=false -f allowed_actions=selected
gh api --method PUT "repos/$rdm_repo/actions/permissions/selected-actions" \
  -F github_owned_allowed=false -F verified_allowed=false \
  -f 'patterns_allowed[]=actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5' \
  -f 'patterns_allowed[]=actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1'
gh api --method PUT "repos/$rdm_repo/actions/permissions/workflow" \
  -f default_workflow_permissions=read -F can_approve_pull_request_reviews=false
gh variable set RDM_RELEASE_ENABLED --body false --repo "$rdm_repo"
gh api --method PUT "repos/$rdm_repo/actions/permissions" \
  -F enabled=true -f allowed_actions=selected
gh api "repos/$rdm_repo/actions/permissions"
gh api "repos/$rdm_repo/actions/permissions/selected-actions"
gh api "repos/$rdm_repo/actions/permissions/workflow"
```

Verify the exact two pinned actions, read-only default and disabled PR approval.
In Settings → Actions → General, confirm those values and no write-token/secret
access for fork PRs. Do not add Actions secrets, SDK/source/runner approval
variables, environments, self-hosted runners, cloud credentials or lab networking.
Keep only `RDM_RELEASE_ENABLED=false`. Do not allow all GitHub-owned/marketplace
actions or add artifact publication permissions to fix a rejected run.

### 4. Add the exact remote and push only main

Immediately recheck clean source and the approved `rdm_bootstrap_sha`. If that
variable is unset in a new shell, restore it from the approval record, not by
blindly approving whatever HEAD now contains.

```bash
test -n "${rdm_bootstrap_sha:-}"
test "$(git rev-parse HEAD)" = "$rdm_bootstrap_sha"
test "$(git branch --show-current)" = main
test -z "$(git status --porcelain)"
test -z "$(git remote)"
git remote add origin https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology.git
git remote get-url origin
git -c push.followTags=false push -u origin refs/heads/main:refs/heads/main
gh repo edit "$rdm_repo" --default-branch main
gh workflow disable build-pak-on-tag.yml --repo "$rdm_repo"
gh repo view "$rdm_repo" --json nameWithOwner,visibility,defaultBranchRef
gh workflow list --all --repo "$rdm_repo"
```

No `--mirror`, `--all`, `--tags`, force push or tag creation. Both old commits
must remain ancestors of remote main. A first main push is a specifically
approved bootstrap exception before required checks exist, not permission for
later direct pushes. The policy/variable gates are already false during this
window; the candidate workflow has no main-push or PR trigger. If disabling it
or verifying private/main fails, stop, do not proceed to additional pushes.

### 5. Verify hosted main and PR checks; protect main

```bash
gh run list --repo "$rdm_repo" --workflow check-source.yml --event push \
  --commit "$rdm_bootstrap_sha" \
  --json databaseId,headSha,event,status,conclusion,url
```

Select the exact run ID from this result (not the first unrelated run), then:

```bash
read -r -p "Verified check-source run ID: " rdm_run_id
gh run watch "$rdm_run_id" --repo "$rdm_repo" --exit-status
gh run view "$rdm_run_id" --repo "$rdm_repo" \
  --json headSha,event,conclusion,jobs,url
gh api "repos/$rdm_repo/actions/runs/$rdm_run_id/jobs" \
  --jq '.jobs[] | {name,conclusion,runner_name,runner_group_name,labels}'
```

Require source SHA match, success (not skipped/neutral), the static test/shell
steps, hosted Ubuntu labels and no SDK/candidate job or PAK artifact. Record
the run URL, action pins, job environment and counts; do not claim an SDK build.

In Settings → Rules → Rulesets (or Branches → branch protection), protect exact
`main`: PRs required, at least one independent approval, dismiss stale reviews,
resolve conversations, require the actual observed static check from GitHub
Actions, block force pushes/deletion, include admins/no routine bypass. Where
supported, require CODEOWNER approval for the prepared ownership file. A sole
owner cannot approve their own PR: approve an additional independent collaborator
before attempting to satisfy review gates. Do not invent or add one in F2.
Verify the plan supports protection for this private repository; if it does not,
record BLOCKED rather than silently make the repository public or claim enforcement.

To exercise the PR event without altering adapter behavior, after separately
authorized local commit/push/PR actions:

```bash
git switch -c bootstrap/hosted-ci-verification
git commit --allow-empty -m "ci: exercise hosted pull-request checks"
git -c push.followTags=false push -u origin \
  refs/heads/bootstrap/hosted-ci-verification:refs/heads/bootstrap/hosted-ci-verification
gh pr create --repo "$rdm_repo" --base main \
  --head bootstrap/hosted-ci-verification \
  --title "Verify hosted no-secret checks" \
  --body "Empty commit only; no adapter behavior, SDK or release change."
gh pr checks bootstrap/hosted-ci-verification --repo "$rdm_repo" --watch
```

Record the PR's actual head/check SHA and check-source success. No merge, close,
branch deletion or release activation is authorized by this runbook. If GitHub
declines an empty-tree PR as having no content difference, STOP and request a
reviewed documentation-only delta; do not change collection logic to trigger CI.

### 6. Registry — only after repository existence and separate local approval

Keep the active `knowledge/context/managed_paks.md` unchanged until then.
Proposed SHA-free, version-free entry:

```markdown
### rdm-topology-poc

- **Remote:** https://github.com/seancummins/vcf-content-factory-sdk-rdm-topology
- **Target:** `content/sdk-adapters/rdm-topology-poc/`
- **adapter_kind:** vcfcf_rdm_topology_poc
- **Owner:** seancummins. Private repository; F2 user-approved ownership override.
- **Notes:** Fixture-only RDM topology POC. Authenticated private-source access
  required; no approved release, bundle publication or deployment.
```

The mount/adapter identity need not equal the GitHub repository suffix; keeping
them unchanged avoids renaming the POC. The parser and bootstrap accept arbitrary
GitHub owners; this is a scoped convention override, not a parser change. Clone
authentication uses the operator's credential helper, never credentials in the
URL/registry. Unauthorized clones must report unavailable, not imply a public
release exists. Do not run global bootstrap or contact other registered remotes
to validate this one entry.

After the owner applies only that registry edit, inspect and validate locally:

```bash
cd /home/scummins/Documents/vcf-content-factory
git diff -- knowledge/context/managed_paks.md
PYTHONPATH=src .venv/bin/python -m pytest tests/test_managed_paks.py -q --tb=short
scripts/validate-changed-content.sh --all
.venv/bin/python scripts/check_skill_parity.py
scripts/path_reference_audit.sh
git diff --check
```

Have an independent reviewer verify one parsed entry with the exact remote,
mount and adapter kind and no owner mismatch; commit only with separate approval.
Do not edit bundle/catalog pointers or publish factory changes. Registration of
a private source repository does not approve public redistribution or releases.

## Acceptance and deferred requirements

| Gate | Offline F2 result / closure evidence |
|---|---|
| Identity decision | PASS: user-approved seancummins/private/main; earlier Sentania/public proposal superseded |
| Complete history audit | PASS for two existing commits and separately hashed prepared tree; new commit must be re-audited |
| Committed adapter CI checkpoint | BLOCKED: F1 and F2 remain uncommitted |
| Independent separation | PASS locally: factory ignores adapter; no submodule, remote or history flattening |
| Hosted no-secret workflow | Offline tests/static checks pass; actual GitHub execution NOT RUN |
| Repository/protections | NOT CREATED/NOT CONFIGURED; explicit external authorization still required |
| Registry | Inactive proposal only; parser validation recorded separately; active edit deferred until remote exists |
| Protected SDK builds/publication | DISABLED/NO-GO; no runner, secrets, environment or approved pins provisioned |

F3 must revisit account type, private-plan capabilities, independent reviewers
and enforceable runner admission. F1's organization runner-group recipe must
not be assumed to work in a personal repository: groups are an organization/
enterprise mechanism. Do not substitute labels or an unrestricted repository
runner. SDK licensing/provisioning/digest, full published F0.5-capable buildkit
and Synology pins, toolchain provenance, approved 1.x+ metadata/tag/source and
CI structural comparison remain future gates. No version bump, SDK build,
release tag, PAK publication or VMware activity is part of F2.

## Evidence and validation record

Independent records:

- `knowledge/context/reviews/rdm-topology-poc-f2-history-audit.md`.
- `knowledge/context/reviews/rdm-topology-poc-f2-bootstrap-review.md`.
- F1 assessment/review and `knowledge/lessons/sdk-paks-independent-repos.md`.

GitHub documentation consulted only for command/settings semantics, not a live
inspection of the target account or repository:

- [CLI repository creation](https://cli.github.com/manual/gh_repo_create).
- [Actions permission endpoints](https://docs.github.com/en/rest/actions/permissions).
- [Disabling a workflow](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows).
- [Private branch-protection availability](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).
- [Runner-group scope](https://docs.github.com/en/actions/how-tos/manage-runners/self-hosted-runners/manage-access).

No account-specific GitHub API, authenticated repository query or external write
was executed. Actual hosted CI results and external enforcement remain unknown.

Offline results: 24 adapter CI tests and 25 factory managed-registry tests
passed. The exact inactive registry snippet independently parses as one entry
with the approved remote/mount/kind, without changing the registry. Full
seven-package content validation, skill parity (5 paired, 7 Codex-only), both
workflow YAML parses, shell syntax and whitespace checks passed. Path-reference
audit is clear, with six existing standing-exception warnings. The root agent
independently reproduced the prepared-tree manifest from the history audit.
No Java/SDK compile or PAK build is necessary for this configuration-only delta;
none was performed in F2. The full factory pytest suite was not rerun and its
previously recorded F0.5 environment failures are not relabeled as passed.

Recommendation: CONDITIONAL GO for the reviewed local preparation; bootstrap
execution remains NO-GO until an explicitly approved preparation commit,
refreshed history/tip audit, separate external-action authorization and the
required server-control verification. Hosted CI and active registry acceptance
remain pending, not assumed. Public publication, protected SDK activation,
release tags/PAKs and deployment remain outside F2.

Independent SDK/bootstrap review: APPROVE, zero BLOCKING implementation
findings. The separate history auditor also approves the bounded audited
history/prepared snapshot, conditional on the refreshed commit audit. Neither
verdict authorizes an external action or claims hosted CI has executed.
