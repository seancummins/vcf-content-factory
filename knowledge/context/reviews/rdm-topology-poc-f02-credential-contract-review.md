# RDM topology POC F0.2 — credential and adapter-instance contract review

**Reviewer:** `sdk-adapter-reviewer` (independent Codex context)  
**Date:** 2026-10-14  
**Scope:** Offline review only. I did not change the adapter, factory,
comparator, PAKs, or any VMware/VCF Operations system, and did not run
`pak-compare`.

## Verdict

**CONDITIONAL APPROVE — implement one credential-free intent attribute; do
not add a dummy credential kind or credential reference.**

The F0.1 B1/B2 differences are real structural differences from the approved
Synology comparator, but the available schema and factory evidence does **not**
support treating them as an Operations or legacy-Java-SDK requirement. The
comparator currently makes those semantic differences BLOCKING solely because
it compares presence asymmetrically; it does not inspect whether an adapter
performs authenticated collection. They must remain reported by the current
comparison rather than suppressed, but they are not evidence that the POC must
declare credentials it neither requests nor consumes.

There is a separate, smaller POC metadata issue: its type-7 adapter instance
omits `isCredentialRequired`, which the shipped schema documents as defaulting
to `true`. The POC documentation promises a credential-free instance. The
minimal truthful representation is therefore an explicit
`isCredentialRequired="false"` on that type-7 `ResourceKind`, while retaining
both the absence of `<CredentialKinds>` and the absence of `credentialKind`.
That change clarifies adapter-instance creation intent; it will **not** make
the existing Synology comparison's B1/B2 disappear.

**GO / NO-GO:** **CONDITIONAL GO** for that one metadata correction plus its
focused offline regression coverage, after author authorization. **NO-GO** to
claim the F0.1 comparison gate is cleared, or to deploy: actual appliance
installation and credential-free adapter-instance creation remain unproven and
require the separately authorized persistence experiment.

If shipped as-is, an operator could encounter a credential requirement at
adapter-instance creation that contradicts the POC's no-credential contract,
even though the PAK's missing CredentialKinds/reference itself is schema-valid.

## Evidence inspected

| Evidence | What it establishes | Limit |
|---|---|---|
| `knowledge/context/reviews/rdm-topology-poc-f01-reference-comparison.md` | B1 is absence/presence of `<CredentialKinds>` and B2 is absence/presence of the type-7 `credentialKind`; the Synology reference has real DSM/Suite API credential fields and endpoint identifiers. | A structurally relevant authenticated adapter is not a semantic requirement source for a fixture-only adapter. |
| `tmp/reference_paks/vcfcf_sdk_synology_diskstation.1.0.0.30.pak`, as summarized reproducibly in the F0.1 records | Synology uses `synology_credentials` and binds it on its type-7 instance because it calls external DSM; F0.1 verified the artifact/release digest. | The local scratch path is not a durable citation; the F0.1 release URL and SHA-256 are the provenance record required by RULE-015. |
| `content/sdk-adapters/rdm-topology-poc/describe.xml` and `src/.../RdmTopologyPocAdapter.java` | The POC declares no endpoint/configuration identifiers or credential kind; `configureAdapter` does not retrieve a credential and the collector deliberately opens no connection. | Static code cannot prove Operations accepts and retains an instance at runtime. |
| `content/sdk-adapters/rdm-topology-poc/docs/installing.md` | The published POC contract says it requests no credentials and opens no network connection. | It is a claim requiring metadata consistency and later appliance proof. |
| `content/sdk-adapters/cluster-perf-risk/conf/describeSchema.xsd` lines 18-23, 264-268, 309-314 | The vendor-shipped schema declares `<CredentialKinds minOccurs="0">`; `credentialKind` is optional; `isCredentialRequired` defaults to true when omitted and false permits creation without a credential. | This is an 8.3.0 local schema, not an installation test on the target Operations build. |
| `knowledge/context/cleanroom-spec/spec/02a-describe-xsd-canonical.md` sections *Top-level* and *ResourceKind attributes* | The factory's canonical 6.3.0 schema analysis independently records `CredentialKinds` and `credentialKind` as optional and the same `isCredentialRequired` default/meaning. | Clean-room schema analysis establishes grammar/declared semantics, not UI behavior. |
| `src/vcfcf_managementpacks/builder.py` `_append_credential_kinds` and `_append_bare_adapter_instance_kind` | The factory deliberately emits neither `<CredentialKinds>` nor `credentialKind` for `auth.preset: none`, citing its no-auth MPB reference behavior. `loader.py::_validate_auth_none` also rejects credentials/flows for that preset. | This is factory convention and validation, not a legacy-SDK appliance acceptance proof. |
| `src/vcfcf_managementpacks/pak_compare.py` lines 575-630 | D1/D6 unconditionally mark a mismatch in CredentialKinds/`credentialKind` presence as BLOCKING. They do not inspect fields, source authentication, or `isCredentialRequired`. | The tool correctly reports a structural divergence under its present rule; its severity is not an SDK contract proof. |
| `PYTHONPATH=src python -m vcfcf_managementpacks validate-sdk content/sdk-adapters/rdm-topology-poc` | Passed the project validation. Compile was skipped because no SDK-JAR path was supplied in this reviewer session. | It neither validates appliance import nor tests instance creation. |

An attempted local `xmllint --schema` check could not compile the vendor XSD
because this environment's libxml2 lacks support for an XSD assertion used by
that schema. That is a tool limitation, not an XML failure, and is not counted
as platform validation.

## Contract assessment by lifecycle phase

| Phase | Credential-kind/reference requirement | Evidence-based conclusion |
|---|---|---|
| PAK installation / describe parsing | No: both `<CredentialKinds>` and `ResourceKind@credentialKind` are optional in the vendor schema. | B1/B2 are **not demonstrated install-metadata defects**. A real install remains required to prove appliance behavior. |
| Adapter-instance creation | A credential is not intrinsically required when `isCredentialRequired="false"`; the current omission defaults to true. | The current POC leaves creation semantics ambiguous/inconsistent with its docs. This is the only evidence-backed metadata correction. No credential kind is needed to express it. |
| Runtime authentication | No POC runtime credential is needed when no network/API session is opened. | The POC does not retrieve credentials or create a remote client. Adding a credential kind would be unused configuration and would falsely imply an authentication contract. |

The Python `cluster-perf-risk` investigation
(`knowledge/context/investigations/2026-10-13-cluster-perf-risk-credential-reuse.md`)
is corroborating evidence that Operations supports a no-credential adapter
shape, but it is a Python Integration SDK adapter and is **not** used as proof
of legacy Java runtime behavior.

## Required corrective action (not performed)

The smallest legitimate change is limited to the existing fixture-only
adapter-instance element:

```xml
<ResourceKind key="vcfcf_rdm_topology_poc" nameKey="2" type="7"
              isCredentialRequired="false" monitoringInterval="5"/>
```

Keep all of the following unchanged:

- no `<CredentialKinds>` block;
- no `credentialKind` attribute;
- no dummy fields, secrets, endpoints, or remote collection;
- no attempt to make `pak-compare` pass by altering its severities.

The author should add a focused deterministic test that parses the POC
`describe.xml` and asserts the type-7 kind has no `credentialKind`, there are
no `CredentialKind` elements, and `isCredentialRequired == "false"`.
Re-run `validate-sdk`, the project tests, build, and the approved comparison.
The re-run must preserve B1/B2 unless a separately reviewed comparator-policy
or credential-free reference selection changes the comparison basis. It must
not call those findings resolved merely because this one attribute exists.

## Comparator and gate disposition

The correct remediation path for B1/B2 is **not** to fabricate credential
metadata. The current Synology comparator remains approved for packaging-family
relevance, but its credential-presence rule cannot distinguish its authenticated
DSM use case from this credential-free fixture POC. After the metadata fix,
the release owner must choose, with independent approval, one of these
auditable routes:

1. select an approved, provenance-qualified credential-free native Java PAK as
   the comparator; or
2. change the comparator policy with explicit tests and an independent
   framework-reviewer review so it reports this declared, credential-free
   semantic difference without pretending it is a platform import failure.

Neither route is authorized by this review, and RULE-005 remains in force:
the eventual applicable comparison must have zero BLOCKING findings before
installation. This record neither waives nor reclassifies B1/B2.

## Governance and registry check

- **RULE-005** (`knowledge/rules/validate-before-install.md`): still blocks
  installation until applicable validation, including an approved clean
  comparison, completes.
- **RULE-008** (`knowledge/rules/no-secrets-on-disk.md`): rules out a fake
  credential as a means to satisfy structural similarity; there is no
  authenticated POC collection to justify one.
- **RULE-014** (`knowledge/rules/pak-version-lines.md`): the `0.x` POC stays a
  hand-built preview and cannot be promoted by this review.
- **RULE-015** (`knowledge/rules/cited-artifacts-reproducible.md`): Synology
  artifact facts are cited through the F0.1 public release/checksum record,
  not the scratch artifact path.
- **Defect registry:** no open defect has `Affects: rdm-topology-poc`; none is
  re-asserted as blocking this review. The B1/B2 policy mismatch is not
  registered as a product defect because it is being resolved before an
  acceptance build; if it survives the next approved build, RULE-012 requires
  the orchestrator to register it.

