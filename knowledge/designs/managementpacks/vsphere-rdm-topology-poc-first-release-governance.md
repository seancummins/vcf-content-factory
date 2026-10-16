# RDM topology POC — first-release governance and CI readiness

## Decision

**Current recommendation: NO-GO for release or deployment.** This document is
a setup plan only; it authorizes no GitHub, tag, release, package upload, or
lab action.

The POC must become an independently versioned adapter repository before a
release is considered. Its expected repository identity is:

```text
GitHub repository: sentania-labs/vcf-content-factory-sdk-rdm-topology-poc
Factory mount:      content/sdk-adapters/rdm-topology-poc/
Adapter kind:       vcfcf_rdm_topology_poc
```

The factory registry gains its one managed-pak entry only after that remote
repository exists and has been approved. The factory must continue to ignore
the clone; no submodule, nested factory history, or repository flattening is
allowed.

## First-release reference-PAK policy disposition

No documented first-release exemption permits a release or installation to
skip `pak-compare`:

- RULE-005 requires comparison against the closest reference PAK before an
  install.
- The SDK builder deliberately skips a missing reference only for a local
  development build; a release build fails closed if no reference PAK exists.
- RULE-014 makes the local `0.0.0.2` PAK a development preview, never a
  release artifact.

Therefore `pak-compare` is **blocked, not waived and not passed**. A POC PAK
cannot compare to itself, and an unrelated management pack cannot be presented
as a baseline simply to make a gate green.

### Proposed narrow first-release procedure

The narrowest acceptable first-release accommodation is a **reference
selection exception, not a comparison exception**. It allows the release
owner to nominate one existing, known-good Java SDK PAK as a structural
reference only when all of the following are recorded and independently
approved before it is used:

1. It is provenance-traceable (vendor or prior approved factory release),
   legally available to the release runner, and SHA-256 recorded.
2. It uses the same native Java SDK PAK family and target Operations line; its
   manifest, `adapters.zip`, adapter directory, `describe.xml`, and runtime
   dependency layout are relevant to this POC's C2-style structure.
3. A reviewer documents why it is structurally comparable and which expected
   semantic differences are not judged by `pak-compare`.
4. The exact reference is added through the buildkit/reference mechanism, not
   copied into the adapter repository or fabricated from the candidate.
5. The CI `pak-compare` run against that reference has zero BLOCKING findings.

This procedure does not waive RULE-005, authorize installation, certify
topology semantics, or make a local artifact official. If no candidate meets
these criteria, the result remains NO-GO and the policy owner must supply or
approve a genuine reference; no self-baseline is allowed.

## CI-compatible SDK dependency strategy

The existing canonical `build-pak-on-tag.yml` pattern fetches an SDK JAR from
a private runtime repository. That pattern cannot be used for this POC under
the explicit constraint that the Broadcom SDK JAR must not be committed,
published, redistributed, or bundled.

Use this replacement strategy, subject to security and licensing-owner
approval:

1. Run only the protected tag-release job on a dedicated, non-public
   self-hosted runner. It must not execute pull-request code and must not have
   network reachability to a VMware lab.
2. A runner administrator pre-provisions the licensed JAR outside every Git
   checkout and outside artifact/upload directories. The release job receives
   its readable path as `VCFCF_SDK_JAR`; it never copies that JAR into the
   workspace, PAK, cache, artifact, or log.
3. The administrator records the JAR's approved SHA-256 in protected runner
   configuration. The tag job verifies that checksum before compiling, without
   printing the local path or JAR contents.
4. The job obtains a published, pinned `sdk-buildkit` release, invokes its
   `build-sdk --release --sdk-jar "$VCFCF_SDK_JAR"`, and uses the kit's
   approved reference-PAK directory for a real `pak-compare` gate.
5. General push/PR CI runs only no-secret static checks and tests that do not
   require the proprietary JAR. Until the POC tests are separated from the
   SDK types, compilation tests stay exclusively in the protected tag job.
6. The release job deletes its temporary build directory on completion and
   uploads only the generated PAK, its SHA-256 sidecar, and a sanitized
   comparison report. It must never upload the SDK, classpath listing, raw
   lab evidence, credentials, or tokens.

This is a proposed adaptation, not a claim that the existing public-hosted
workflow already implements it. The security owner must approve the runner
isolation and JAR provisioning before implementation.

## Operator-executable repository and CI setup plan

Perform these steps only after separate authorization for external GitHub
actions.

1. Create the repository from the sanctioned Java SDK adapter template with
   the required name above. Do not create a submodule.
2. Add the POC source as the repository's reviewed initial history. Preserve
   `dist/`, `*.pak`, `build/`, `.test-build/`, `__pycache__/`, `.env`, and
   local scratch/report paths in `.gitignore`. Verify with `git status` that
   no SDK JAR, PAK, credential, token, lab report, or generated build output
   is staged.
3. Add the template's vendored `ci/defect_gate.py`, a no-secret PR workflow,
   and a tag-only release workflow. Keep actions commit-pinned and retain the
   tag/version/build-number consistency gate.
4. Configure repository protection so only reviewed, protected tags invoke the
   release workflow. Scope `contents: write` to that workflow alone. Configure
   the dedicated runner and its pre-provisioned SDK strategy described above;
   do not add `SDK_RUNTIME_SSH_KEY` or an SDK blob to GitHub secrets/artifacts.
5. Pin a published `sdk-buildkit` version, not a mutable branch. Before the
   first tag, place the independently approved structural reference PAK in the
   buildkit/reference mechanism and record its provenance and SHA-256 in the
   release review.
6. Add `rdm-topology-poc` to `knowledge/context/managed_paks.md` only after
   the remote exists. The entry must name the remote, mount target, adapter
   kind, owner, and POC scope; it carries no SHA, release version, or binary.
7. Run the no-secret workflow on a reviewed source commit. Resolve all static
   failures before considering a tag.
8. Before any tag, obtain approval for a **`1.x+`** first-release version,
   update `adapter.yaml` and `CHANGELOG.md` in the independent repository,
   and use the next approved monotonic build number. Require the protected tag
   to equal `v<approved-1.x+-version>.<approved-build_number>`. The current
   `0.1.0` metadata and its `v0.1.0.2` derivation are prototype-only and must
   never be tagged or released. Do not run `--release` by hand.
9. On the protected tag runner, verify the SDK checksum, run the defect gate,
   build the candidate, and run `pak-compare`. The workflow fails if the
   reference is absent or any BLOCKING finding exists.
10. Attach only the CI-built PAK and `<pak>.sha256` to the matching GitHub
    Release. An operator independently downloads both and verifies with
    `sha256sum -c <pak>.sha256`; record tag, commit, buildkit version,
    reference PAK provenance/checksum, candidate checksum, and gate outputs
    in the release review.

## Baseline artifact decision

The local `vcfcf_sdk_rdm_topology_poc.0.0.0.2.pak` cannot be promoted to the
first approved baseline. It is a hand-built `0.x` preview, lacks a successful
comparison, and is not an official CI artifact.

The first approved baseline, if the process above succeeds, is the fresh
CI-built PAK attached to the protected tag. It becomes an audit reference only
after the release review records its SHA-256, source commit, buildkit version,
selected structural reference, and zero-BLOCKING comparison result. It does
not itself prove runtime topology persistence; that remains the separately
authorized E2 experiment.

## Updated readiness matrix

| Gate | Current state | Required evidence to advance |
|---|---|---|
| Fixture POC mechanics | PASS | Existing build-2 review and six focused tests. |
| Local artifact audit | PASS | E1 audit and independent readiness review. |
| Reference-PAK comparison | BLOCKED | Approved relevant reference + zero-BLOCKING CI comparison. |
| Independent remote repository | BLOCKED | Approved GitHub repository and managed-pak registry entry. |
| CI release workflow | BLOCKED | Protected runner/JAR provisioning approval; pinned buildkit; green no-secret and tag workflow. |
| First-release version line | BLOCKED | Approved `1.x+` metadata, changelog, and matching protected tag. |
| Official first-release artifact | BLOCKED | Protected tag CI PAK + SHA-256 sidecar + release review. |
| Development-lab authorization | BLOCKED | Named change, window, fixture, administrator, and rollback approval. |
| E2 persistence experiment | NO-GO | Every preceding gate plus explicit user authorization. |

## Remaining approvals

The following decisions belong to the user/release and security owners, not
to this planning increment: repository creation and visibility; runner trust
boundary; licensed SDK provisioning method; reference PAK relevance; buildkit
pin; source commit and tag; GitHub Release publication; and the later lab
installation/rollback window.
