# F2 — independent private repository bootstrap review

Date: 2026-10-15. Role: independent `sdk-adapter-reviewer`, applying the shared
reviewer doctrine. Scope: local repository/hosted-CI preparation and the operator
runbook; not approval to execute any external action.

## Verdict

**APPROVE — zero BLOCKING implementation findings.** The prepared destination
and no-secret workflow respect the explicit F2 ownership decision and preserve
the independent adapter history. **CONDITIONAL GO for the reviewed local
preparation; NO-GO for external execution until separately authorized and the
pending adapter checkpoint is explicitly committed and re-audited.**

If uploaded as prepared after those approvals, the private repository can run
hosted source checks without the SDK. The existing committed adapter tip alone
cannot: the F1/F2 workflow files are not yet committed. Nothing here establishes
an actual hosted-CI success, enforced branch protection or release readiness.

## Inspected checkpoints and scope

- Factory: `feature/rdm-topology-mp`,
  `ba88ba8f9b8b4742db3384e827d1fbe2a48cf99a`; F1 documentation is committed.
- Adapter: independent `main`,
  `cb2292db90d5d0a8da530e9c187986307daf0d2b`; pending F1/F2 preparation remains
  uncommitted. No remote or tag exists. The factory tracks no adapter files.
- Explicit destination: `seancummins/vcf-content-factory-sdk-rdm-topology`,
  **private**, default `main`. This supersedes F1's proposed Sentania/public
  destination without rewriting the historical approval record.
- Read the F1 assessment/review, SDK author/reviewer contracts, relevant skills,
  rules/lessons, prepared workflows/helper/policy/tests/operator documentation,
  and `knowledge/designs/managementpacks/vsphere-rdm-topology-f2-repository-bootstrap.md`.
  Read the separate complete-history security audit at
  `knowledge/context/reviews/rdm-topology-poc-f2-history-audit.md`.

The adapter is still local-only and unregistered, not independently fetchable
from a factory clone. Its relevant controls are summarized below rather than
presented as an already published implementation. Java, Java tests, descriptor,
adapter metadata and changelog have no diff from the reviewed adapter HEAD.
Version remains `0.1.0`, build 4; no real PAK was rebuilt.

## Independent control assessment

| Control | Result |
|---|---|
| Ownership | Workflow, helper constant and policy consistently select the confirmed owner destination. Account type and plan were not queried. The former adapter destination is rejected by regression coverage. Upstream factory/buildkit/reference URLs remain dependency provenance, not the adapter remote. |
| Hosted isolation | `check-source` triggers PR/main only on `ubuntu-latest`, with read-only contents and no persisted checkout credentials. Full-SHA actions execute stdlib synthetic tests and shell checks. No SDK variable, protected environment, self-hosted runner, cache, artifact upload or release secret is referenced. Pipeline tests mock all external command execution. |
| Release remains disabled | Policy false; unapproved dependency pins null; repository enablement false in the runbook. Candidate workflow remains tag-only with repository/protected-ref/environment/source gates and no publication/write permission. The runbook explicitly disables it server-side after upload, configures no release environment/runner and selects only the two hosted action pins. |
| Bootstrap integrity | Empty private repository creation has no template/source/push initializer. Existing main history is retained; exact approved tip/clean state is checked before an explicit main-only push with automatic tag following disabled. First push is an auditable bootstrap exception, not permission for later unreviewed main pushes. |
| Checkpoint honesty | Uncommitted F1/F2 state is prominently blocking. Exact allowlist staging, separate commit approval and fresh complete-history/tip audit precede any upload; no retrospective commit SHA or hosted result is invented. |
| Server controls | Actions default is read-only, PR approval disabled, release variable false; owner must verify private/main and workflow state. Run selection is tied to exact approved SHA. Independent main approval, required actual check, force/deletion restrictions and private-plan availability are explicit verification gates. |
| Private-account/plan limits | Plan does not assume organization runner groups are available for this owner/account or labels enforce isolation. Account type, plan capabilities, runner provisioning and protected release activation remain deferred verification gates; unsupported branch protection is BLOCKED, not a reason to make source public or claim enforcement. |
| Registry | Proposed entry is inactive, SHA/version-free and preserves local mount/adapter kind. The user's explicit ownership override is documented without changing general policy or adding a nonexistent remote to the active registry. Private authentication is not embedded in its URL. |
| PR verification | Separately authorized empty-commit branch/PR can test the event without behavior changes; rejection stops for a reviewed documentation-only alternative. No merge, cleanup, collaborator addition or release activation is silently authorized. |

The complete-history auditor inspected all refs, reachable/reflog history and
the object database, with no binary/recognized-secret/raw-inventory finding.
I independently confirmed the two-commit history, tracked-file surface, absent
remote/tags and repository separation; the specialized blob-pattern scan is the
separate audit's evidence, not a claim that arbitrary secrets can be proven absent.
Generated text and diagrams are intentional reviewed documentation, not PAKs or
raw lab output. Its recorded prepared-tree fingerprint must be refreshed after
any subsequent edit or commitment.

## Independent verification

- **24 adapter CI stdlib tests passed.** The synthetic success-path ZIP is a
  temporary test fixture, not a compiled or published PAK. Failure cases leave
  no candidate output. F2 coverage checks exact owner/private/main, disabled
  policy/null pins and rejection of the old destination.
- **25 managed-registry tests passed**, using the existing factory test file.
- **Proposed entry parsed successfully in memory:** exactly one
  `rdm-topology-poc` entry, exact `seancummins` remote, unchanged local target
  and `vcfcf_rdm_topology_poc` kind; derived GitHub API URL also exact. Mocked
  file reads only; no active registry edit or remote access.
- **Full content validation passed**, independently rerun with
  `scripts/validate-changed-content.sh --all`.
- **Skill parity passed:** 5 paired / 7 Codex-only. Path audit clear, with the
  same six existing TVS/downstream-local-registry standing-exception warnings.
- Adapter shell syntax and both repositories' whitespace checks passed.
  Diff check confirms no Java, descriptor, metadata or changelog change.
- **Hosted GitHub execution NOT RUN.** No repository/account/settings query,
  SDK compile/build/comparison, installation, dependency download or Git write
  was performed by this reviewer. F1's existing SDK/build/comparison evidence
  is historical, not a newly repeated F2 build claim. Full factory pytest was
  not rerun for this independent-adapter CI/documentation-only increment.

Reviewed control-file SHA-256 values:

| File | SHA-256 |
|---|---|
| hosted workflow | `9207416250ec33e9fbfaa0644eecfd730d8e26ee082957c7dbd88e18d10b51ba` |
| disabled candidate workflow | `b49284d2e3ca5b4bfb2b8cfd555b132640b98b31ca6e7a4c04318e84660fdad0` |
| release helper | `d767d37e113286b2695e0abd4b093fb45676bcd9320e6a8a77e0118320e87caf` |
| disabled policy | `8ccc6079ffbcce51ba3f25ce6a59f3a5ca0ef57b5c63f8e087971996324db5a3` |

## Governance, remaining gates and registry check

Authorities: RULE-008 (no secrets), RULE-014 (no prototype release), RULE-015
(honest reproducibility/provenance), RULE-012 (defect gate), the SDK skill's
build-hygiene/gap-honesty requirements and independent-repository lesson. The
user's F2 brief is the explicit scoped ownership-convention override; it does
not waive registry timing or independent release/deployment controls.

Registry check: `knowledge/context/defects.md` has no open defect affecting
`rdm-topology-poc`; no downstream local registry is present. No new surviving
WARNING-or-higher implementation defect is proposed. Missing approvals,
uncommitted checkpoint, unexecuted hosted checks and unconfigured external
controls are explicit acceptance gaps, not silently passed implementation tests.

Required before F2 execution/closure: operator approval of the preparation
commit; refreshed exact-tip audit; separate approval for repository creation,
settings, remote and reviewed-ref upload; actual successful main/PR check
evidence; verified private-plan protections and independent reviewer access;
and separately approved, independently validated post-creation registry entry.

Protected SDK CI activation, runner admission/provisioning, approved dependency
pins, 1.x+ metadata/source/tag approval, actual CI comparison, release
publication and VMware deployment remain **NO-GO** and outside F2. Compilation,
future packaging or source CI does not prove runtime relationship persistence.

Reviewer writes were confined to this report; no implementation was fixed by
the reviewer. No external action is authorized by this APPROVE verdict.
