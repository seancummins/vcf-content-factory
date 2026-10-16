# F2 — independent adapter Git-history security audit

Date: 2026-10-15. Role: independent `sdk-adapter-reviewer`, narrowly scoped to
repository-history and pending-source publication hygiene. No network access,
SDK binary reading, Git mutation, compilation or deployment was performed.

## Checkpoint and verdict

Factory checkpoint: `ba88ba8f9b8b4742db3384e827d1fbe2a48cf99a`.
The F1 factory documentation is committed. Independent adapter `main` remains
`cb2292db90d5d0a8da530e9c187986307daf0d2b`; its F1 workflow/helper changes are
**not committed**. The adapter has no remote or tags. No commit was created
during this review.

**APPROVE the audited existing history for the proposed private bootstrap;
zero BLOCKING security findings.** This is not authorization to create a
repository, add a remote or push. Bootstrap remains conditional on separately
reviewed and explicitly committed pending adapter changes, a refreshed tip audit,
and explicit operator authorization for external actions. No history rewrite is
recommended. Initial destination is the user-approved private repository
`seancummins/vcf-content-factory-sdk-rdm-topology`, default branch `main`.
Publication or transfer to another owner is not approved.

If pushed as-is, the current adapter tip contains the fixture POC and reviewed
text documentation, **but not the F1/F2 hosted validation workflow**. Therefore
pushing `cb2292d` alone cannot satisfy the hosted-CI acceptance criterion.

## Complete history scope and methods

Read-only Git inspection covered every local ref, commit, tree and blob:

| Evidence | Result |
|---|---|
| All refs | One: `refs/heads/main`; no tags, remote-tracking or replacement refs |
| Commits | Root `4493ee2584f180be65a4472b0996f5207d8ee456`, then `cb2292db90d5d0a8da530e9c187986307daf0d2b` |
| Historical entries | 44 regular-file entries across both trees; 22 distinct paths |
| Entire object database | 53 objects: 2 commits, 21 trees, 30 blobs; 43,919 blob-content bytes |
| Integrity | `git fsck --full --no-reflogs --unreachable`: exit 0, no diagnostics or unreachable objects |
| Reflogs | Only the same two commits; no extra reflog-only history |
| History completeness | Not shallow; no object alternates or grafts |
| Repository isolation | Separate adapter `.git`; factory ignores adapter files; no gitlinks/submodule |
| Other indirection | No tracked `.gitmodules`/`.gitattributes`, Git LFS pointer blobs, local info attributes or custom filters |

Commands included `git log --all`, `for-each-ref`, `rev-list --objects --all`,
`ls-tree -r` for every commit, `ls-files --stage`, `cat-file
--batch-all-objects --batch-check`, full blob reads, `reflog show --all`,
`count-objects -v`, local configuration key-name inspection, and `fsck`.
Local config contains only ordinary repository core keys; no configured remote
or credential/filter configuration was present. Author emails were not copied
into this report. Commit messages were inspected for credential-like payloads.

Every object blob was checked in memory for binary/archive/class signatures,
private-key delimiters, recognized GitHub/AWS token forms, JWT-shaped strings,
URL user/password information, credential assignment forms, inventory envelopes
and sensitive inventory/scratch path patterns. Historical paths were checked
for SDK/build archives, classes, keys, environment files and scratch/build output.
These are bounded pattern checks plus source/document inspection, not a claim
that a general-purpose secret detector proves arbitrary text safe.

## Findings and classification

- **No proprietary SDK, other binary/archive, compiled class, credential file,
  private key, recognized token or raw inventory response was found in any
  historical blob or commit message.** There are no historical `.jar`, `.pak`,
  `.class`, `.env` or build-output paths.
- The fixture source and both historical Java-test versions contain a short
  MOID also used in the stated lab context. Manual review shows deliberately
  synthetic repeated-digit UUIDs and fixture-only names, alongside explicit
  no-network behavior and deterministic multi-vCenter tests. This is **synthetic
  fixture identity**, not a committed Suite API or SOAP response. No raw lab
  UUID, canonical LUN/WWN identity, backing filename or inventory report was
  identified. A generic MOID alone is not a credential or proof of raw inventory.
- Tracked `*.generated.md`, SVG and Excalidraw inventory documentation are
  reviewed human-readable project documentation. They are not generated PAKs,
  proprietary SDK redistributions or sensitive lab-report artifacts. Their
  presence is intentional, consistent with the factory's SDK documentation
  convention.
- Current ignored metadata lists four local development PAKs under `dist/`
  and two Python bytecode-cache files. None occurs in any historical tree or
  the prospective nonignored source set. Ignored paths were inventoried by name
  only; the SDK and other secret-bearing local files were not opened. Do not use
  `git add -f`, blanket filesystem uploads, `git push --mirror`, or `--tags` in
  bootstrap commands. Push the reviewed `main` ref only.

## Pending-source snapshot

The completed F1/F2 prepared tree contains **30 nonignored tracked/untracked
files, 101,892 bytes**. A final in-memory scan found no binary/archive payload,
recognized credential pattern or inventory envelope. The inventory-like
constants remain only the reviewed fixture/test identities described above.

The complete prospective-source manifest SHA-256 is
`c84facd4954f81a47d8a13cecde62869e93e4530a28a6a0462c0fd59373e1eb9`.
Definition: lexicographically sort the unique UTF-8 paths from `git ls-files
--cached --others --exclude-standard -z`; for every path concatenate its UTF-8
bytes, one NUL byte and the raw 32-byte SHA-256 of its file contents; hash that
stream using SHA-256. Ignored PAKs/bytecode and `.git` metadata are excluded.
This fingerprint is **not** a commit, staged-file assertion, approved push
revision or substitute for auditing the eventual new commit.

| Security-relevant prepared file | SHA-256 |
|---|---|
| `.github/CODEOWNERS` | `ec61441e8b240869ec41dc54d91da7550d7d1f5ef78b6ae371aeb75e2d86ea72` |
| `.github/workflows/check-source.yml` | `9207416250ec33e9fbfaa0644eecfd730d8e26ee082957c7dbd88e18d10b51ba` |
| `.github/workflows/build-pak-on-tag.yml` | `b49284d2e3ca5b4bfb2b8cfd555b132640b98b31ca6e7a4c04318e84660fdad0` |
| `ci/release.py` | `d767d37e113286b2695e0abd4b093fb45676bcd9320e6a8a77e0118320e87caf` |
| `ci/release-policy.json` | `8ccc6079ffbcce51ba3f25ce6a59f3a5ca0ef57b5c63f8e087971996324db5a3` |

Destination allowlists in the helper, policy and protected workflow agree with
`seancummins/vcf-content-factory-sdk-rdm-topology`; CODEOWNERS names the confirmed
owner. Remaining `sentania-labs` references designate upstream buildkit/registry
sources, not adapter ownership or a configured Git remote. Release policy stays
false with unapproved dependency pins unset. The hosted workflow has only
GitHub-hosted runners, read-only contents permission, nonpersisted checkout
credentials, no protected SDK configuration, no secrets expression, no network
collection commands, and no candidate/artifact upload step. It invokes offline
synthetic helper tests and shell syntax validation, not the protected builder.
Hosted execution itself remains unperformed and cannot be inferred from YAML.

## Governance and limitations

Authorities: RULE-008 (`knowledge/rules/no-secrets-on-disk.md`), RULE-014
(`knowledge/rules/pak-version-lines.md`), RULE-015
(`knowledge/rules/cited-artifacts-reproducible.md`), the SDK skill's
classloader/build-hygiene and gap-honesty contract, and
`knowledge/lessons/sdk-paks-independent-repos.md`. The F1 independent review at
`knowledge/context/reviews/rdm-topology-poc-f1-ci-readiness-review.md` approves
only local preparation, not publication or release enablement.

Registry check: `knowledge/context/defects.md` has no open defect affecting
`rdm-topology-poc`. No new surviving implementation defect is proposed by this
security audit. No credentials were read from local profiles; no external secret
scanner or software was installed. Pattern matching cannot rule out every
possible unknown-format secret, encrypted value, steganographic payload or
licensing/provenance issue. Review the exact staged diff and future commit tip
again before any authorized push; this report does not cover later changes.

A normal reviewed-ref push sends reachable Git objects, not ignored worktree
files or unrelated reflog entries. This checkout presently has no unreachable
objects anyway. Do not delete `.git`, flatten the adapter into the factory,
rewrite the two existing commits or silently commit pending F1/F2 work.

**GO, conditional, for a separately authorized private repository bootstrap
after pending-source commitment and re-audit. NO-GO for public publication,
protected runner activation, release tags/PAKs, or deployment.** Hosted GitHub
execution and external protections are outside this offline history audit.
