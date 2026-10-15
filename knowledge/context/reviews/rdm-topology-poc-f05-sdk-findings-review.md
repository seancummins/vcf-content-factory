# F0.5 — independent SDK review of emitted comparator findings

Date: 2026-10-14. Reviewer: `sdk-adapter-reviewer`, independent Codex context.
Scope: artifact identity, credential-contract evidence and actual emitted
legacy/structural findings. Framework implementation, full-suite coverage and
entry-point propagation are separately gated by `framework-reviewer`; this
report does not claim to have reviewed or tested those surfaces completely.

## Verdict

**APPROVE — zero new BLOCKING findings in this bounded SDK findings review.**
The executed structural comparison reports **0 BLOCKING / 3 WARNING / 22 INFO**,
exit **0**. The unchanged default comparison reports **2 BLOCKING / 3 WARNING /
20 INFO**, exit **1**. The three comparator WARNINGs remain present and are
not waived by this approval.

If used as-is, the local comparator explains the valid authentication-model
difference while preserving the reference's other structural differences.
It does not demonstrate that an appliance accepts the POC instance or retains
its foreign-parent relationship. **GO for planning release infrastructure**,
subject to the independent framework implementation approval and required
offline validation. **NO-GO for release or deployment** under the remaining
E1.5 prerequisites and RULE-005/RULE-014.

## Independent evidence

I read the approved F0.4 design/review, F0.2 contract findings, F0.3 build-4
re-review, F0.1 reference-selection record, F0.5 comparison record, the canonical
schema digest, Tier 2 SDK skill and reviewer doctrine, and defect registry.
I independently computed both SHA-256s, tested the outer ZIP and nested
`adapters.zip` integrity, parsed both embedded descriptors, inspected their
JAR inventories, and reran both public CLI comparisons using the local
`.venv/bin/python` and `PYTHONPATH=src`.

| Artifact | Independently verified SHA-256 |
|---|---|
| RDM POC `vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak` | `5354acc09b4afa5a2fad5aed9429adebd8fe0f0e751b0b64b909c59854381d61` |
| Synology `vcfcf_sdk_synology_diskstation.1.0.0.30.pak` | `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1` |

The Synology provenance remains the approved official
[v1.0.0.30 release](https://github.com/sentania-labs/vcf-content-factory-sdk-synology/releases/tag/v1.0.0.30)
and F0.1 digest record; I made no new network request. The POC is a local-only
development artifact, not reproducible from a factory checkout alone;
findings are summarized here in full. No SDK binary, fixture or artifact was
copied into the report or changed.

The POC embedded type-7 kind is `vcfcf_rdm_topology_poc`, explicitly
`isCredentialRequired="false"`, with no `CredentialKinds` container and no
`credentialKind` reference. Its only data kind is `RdmMapping`, declaring
required identifiers `vcenter_instance_uuid`, `vm_instance_uuid` and
`virtual_disk_key`. The PAK contains its application JAR and
`vcfcf-adapter-base.jar`; no separately bundled proprietary SDK JAR is present.

Synology's type-7 `synology_diskstation` binds `synology_credentials` and omits
`isCredentialRequired`, which has documented effective value true. The declared
kind contains required username/password fields and three optional Suite API
fields; password fields are masked. It is a coherent credentialed contract,
whereas the POC expresses a coherent credential-free contract.

The schema authority is
`knowledge/context/cleanroom-spec/spec/02a-describe-xsd-canonical.md`,
top-level children and ResourceKind attributes. The credential container and
reference are optional; default-true requiredness is documented semantics.
The approved F0.4 rule requiring explicit false on an unbound type-7 instance
is conservative factory policy, not a claim that the XSD enforces that
cross-field constraint. This review does not claim complete XSD validation.

## Findings preserved and interpreted

The default CLI invocation supplied the candidate and reference paths with no
policy flag. Its B1/B2 presence differences and every remaining finding retain
the historical counts and exit status. The structural invocation added
`--policy structural --reference-sha256` with the full verified Synology digest
above. Its report identifies `structural/1`, both adapter identities and
digests, and the bounded schema-contract source.

D1/D6 remain visible as INFO, with the original differences plus independent
contract evidence: candidate has zero credential kinds/bindings and required
false; reference has one kind/binding and required true. This is exactly the
approved semantic evaluation for this pair, with no dummy credential,
artifact alteration or adapter-specific exemption demonstrated by the output.
All twenty prior INFO findings also remain. This bounded review does not
substitute for the framework review of generic validator failure paths.

| Residual WARNING | Independent interpretation and remaining proof |
|---|---|
| D8: instance identifiers, POC 0 versus Synology 3 | Synology exposes host, port and allowInsecure configuration; the fixture POC has no remote endpoint configuration. The difference remains WARNING. Successful credential-free instance creation on the target appliance is still unproven. |
| D23: TraversalSpecKind count, POC 0 versus Synology 1 | Synology declares a storage traversal; the POC declares none. A relationship emitted in Java does not by itself prove navigation through a particular UI traversal. This WARNING remains visible. |
| D25: empty TraversalSpecKinds versus populated reference | The POC omits the container, normalized as empty by this existing rule. This related structural WARNING also remains. Neither a traversal count nor an API-accepted relationship proves topology UI visibility or persistence. |

The POC source inspection confirms the intended additive `parentForeign`
builder path; no adapter source was changed in F0.5. Runtime VM resolution,
preservation of VMware-owned edges, repeated-collection idempotence, survival
of a VMware adapter collection and UI visibility remain separate authorized
deployment-test outcomes. The cross-MP identity and edge-mechanics lessons
continue to apply; a passing PAK comparison proves none of them.

## Governance disposition

RULE-005 is unchanged. The exact build-4 artifact now has a passing **local
structural comparison** against its independently approved exact reference.
That satisfies this local comparison sub-check, rather than rewriting the
historical legacy failure. The official release process must run the same
explicit policy/reference/digest through pinned reviewed tooling against its
actual CI-built artifact. A manual pass cannot substitute for that automatic
CI gate, release artifact approval, administrator approval or full pre-install
validation. RULE-014 prevents promoting the local `0.x` PAK as a `1.x` release.

Registry check: no open `Affects: rdm-topology-poc` entry exists. The Synology
entries DEF-001, DEF-003, DEF-005 and DEF-006 are closed. No new SDK defect is
proposed from these emitted findings. The three existing cross-adapter
structural warnings are recorded above as unresolved static limitations;
this report neither hides them nor claims an appliance defect without proof.

No build, install, live request, adapter modification, commit, push or
publication was performed by this reviewer. Review writes were confined to
this report.
