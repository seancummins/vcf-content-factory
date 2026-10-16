# F2 — independent committed-checkpoint security audit

Date: 2026-10-15. Reviewer: independent `sdk-adapter-reviewer`, repository
security/checkpoint scope. This report supersedes only the uncommitted-status
statements in `knowledge/context/reviews/rdm-topology-poc-f2-history-audit.md`;
its methods, synthetic-fixture classification and bounded-scan limitations still
apply. F2 implementation and bootstrap review remain separate authorities.

## Verdict

**APPROVE — zero BLOCKING checkpoint/security findings.** The orchestrator
created the explicitly authorized **local-only** adapter commit after an
independent staged audit. The exact committed contents match the previously
reviewed F1/F2 source fingerprint. No history rewrite occurred.

**CONDITIONAL GO for a separately authorized private repository bootstrap** to
`seancummins/vcf-content-factory-sdk-rdm-topology`, default branch `main`.
**NO-GO for any external action without that authorization**, public publication,
protected-runner activation, release tags/PAKs, or deployment.

If used as-is, the checkpoint contains the no-secret hosted source workflow and
disabled protected candidate preparation. It has no remote; no hosted run or
external protection has been verified by this audit.

## Exact checkpoints

| Item | Verified value |
|---|---|
| Factory HEAD | `ba88ba8f9b8b4742db3384e827d1fbe2a48cf99a` — unchanged |
| Adapter branch | `main` |
| Adapter before | `cb2292db90d5d0a8da530e9c187986307daf0d2b` |
| Adapter after | `160f6461541ca312708ee880f3b5837b7ccfd312` |
| After parent | `cb2292db90d5d0a8da530e9c187986307daf0d2b` |
| After tree | `7934a5d021534cd516dc822d5904d04c95b59753` |
| Commit subject | `ci(rdm): prepare protected CI and private repository bootstrap` |
| Original root retained | `4493ee2584f180be65a4472b0996f5207d8ee456` |
| Adapter status / refs | Clean; one `refs/heads/main`; no tags or configured remote |

The reviewer performed no Git writes. The orchestrator alone staged and
committed the user-approved adapter scope. Existing untracked factory F2
documentation was not incorporated into the adapter or committed by this audit.

## Independent staged approval, before commit

The reviewer read **index blobs**, not just worktree files. Exactly these eleven
changed paths were staged:

```text
.github/CODEOWNERS
.github/workflows/build-pak-on-tag.yml
.github/workflows/check-source.yml
.gitignore
README.md
ci/README.md
ci/defect_gate.py
ci/release-policy.json
ci/release.py
ci/tests/test_release.py
scripts/run-tests.sh
```

All 30 indexed files totaled 101,892 content bytes. The manifest SHA-256 was
`c84facd4954f81a47d8a13cecde62869e93e4530a28a6a0462c0fd59373e1eb9`, exactly
matching the approved prepared-tree fingerprint. The algorithm is specified in
the prior history audit: sorted UTF-8 path, NUL separator, raw file SHA-256,
then SHA-256 of the concatenated stream. No unexpected paths, nonregular modes,
unmerged stages or unstaged tracked changes were present. The reviewer sent an
explicit staged APPROVE to the orchestrator before its commit.

## Independent exact-tip and full-history re-audit

After the commit notification, the reviewer independently reran Git/object
inspection and recomputed the manifest from `HEAD` tree blobs:

| Check | Result |
|---|---|
| Committed tree | 30 regular text files, 101,892 bytes |
| Committed manifest SHA-256 | `c84facd4954f81a47d8a13cecde62869e93e4530a28a6a0462c0fd59373e1eb9` — exact approved match |
| Complete local object database | 71 objects: 3 commits, 27 trees, 41 blobs; 116,238 blob-content bytes |
| Complete reachable history | Exactly the three commits listed above |
| Integrity/unreachable check | `git fsck --full --no-reflogs --unreachable`: exit 0, no diagnostics/unreachable objects |
| Blob and commit inspection | No binary/archive/class, recognized token/private-key, credential-assignment, URL-userinfo or raw-inventory-envelope finding |
| Every historical tree | No prohibited SDK/PAK/class/key/environment/scratch/build-output path; no nonregular-file mode |
| Adapter Java/tests | No change from parent |
| `describe.xml`, `adapter.yaml`, CHANGELOG | No change from parent; prototype version/build remain `0.1.0` / 4 |
| Protected policy | `release_enabled: false`; no approved SDK/toolchain pins introduced |
| Owner/visibility | Consistent approved owner destination and private bootstrap instructions; no remote configured; account type/plan unverified |

All commit objects, including commit messages, were rescanned without printing
author emails or possible secret payloads. Known fixture identifiers retain the
previously reviewed synthetic classification; this scan does not convert
unknown-format secret detection into proof of absence. Ignored local development
PAKs and bytecode remain outside the committed tree and push reachability.

Independent offline rerun: `python3 -m unittest discover -s ci/tests -v` —
**24 passed**. Tests use deterministic mocked dependencies and temporary
synthetic ZIPs, not proprietary SDK files, live queries or a real PAK build.
The committed source is identical to the indexed/tested snapshot.

## Governance and outstanding evidence

Authority: RULE-008 (`knowledge/rules/no-secrets-on-disk.md`), RULE-014
(`knowledge/rules/pak-version-lines.md`), RULE-015
(`knowledge/rules/cited-artifacts-reproducible.md`), the SDK skill's build-hygiene
and gap-honesty requirements, and
`knowledge/lessons/sdk-paks-independent-repos.md`. Registry check:
`knowledge/context/defects.md` contains no open defect affecting
`rdm-topology-poc`. No new surviving implementation defect is proposed.

No SDK binary or credential profile was opened. No dependencies were installed,
no network/GitHub/VMware action was taken, and no Git ref was changed by the
reviewer. No PAK was created, modified, published or deployed. Write scope was
limited to this factory review artifact. The report itself remains uncommitted
factory documentation, not part of the adapter checkpoint.

The exact commit is ready for the next **separately authorized** bootstrap step;
GitHub ownership/private visibility confirmation, branch/workflow settings and
the actual hosted no-secret run still require external verification. Protected
SDK runner provisioning and release enablement remain out of scope and disabled.
