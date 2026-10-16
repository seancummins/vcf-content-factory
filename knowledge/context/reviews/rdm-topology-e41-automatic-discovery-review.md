# E4.1 — Independent automatic-discovery architecture review

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT remaining.** Approval is
for the proposed architecture and a separately authorized, offline E4.2
implementation increment. It is not approval to deploy, change the installed
instance, publish topology, or claim production readiness.

## Scope and independent verification

Reviewed the complete [E4.1 architecture](../../designs/managementpacks/vsphere-rdm-topology-e41-automatic-discovery.md)
and [API map](../api-maps/vsphere-rdm-automatic-discovery.md) against the
SDK-adapter reviewer contract, reviewer doctrine, RULE-001/002/005/008/009/012,
the Tier 2 SDK skill, E3.3 ownership/identity policy and E3.4.1 qualification.
Independently inspected existing adapter and framework source, not private
inventory or author-supplied execution claims:

- Compliance `VSphereClient.java`: the documented javax/Jakarta provider
  collision, native vim25 SOAP requests, older per-property reads, and
  namespace-unaware/permissive parser setup. The new design explicitly does
  **not** copy that parser or collection algorithm unchanged.
- Compliance `describe.xml`, `VCenterCertificates.java`, and framework
  `VcfCfAdapter.java`: credential-kind/password declarations, runtime
  `getResourceCredential().getCredenialFields()` access, explicit dialed-host
  certificate matching, and actual certificate-review hook signatures.
- Framework `SuiteApiStitchClient.java`, `AmbientCredential.java`, and
  `ForeignResourceResolver.java`: permissive TLS, localhost routing assumptions,
  credential-file fallbacks, single-identifier last-write-wins indexing and
  failure-to-empty caching. None is accepted unchanged for the proposed client.
- Existing RDM identity and relationship classes, Python PropertyCollector
  paging/cancellation, and the documented injected-credential SDK contract.

Managed adapter source is independently versioned and registry-retrievable;
these inspections do not make its absent license/NOTICE an implied reuse grant.
The architecture identifies code-reuse rights as a pre-copy prerequisite.

## Findings and disposition

An initial draft named a nonexistent `getPasswordCrypt` accessor. The author
corrected it before this verdict to SDK
`AdapterCredentialConfig.getPassword()`, whose internal platform `Crypt`
linkage must be qualified. The final document also explicitly retains the
certificate-review hook, authoritative-coverage requirement before removals,
and limits on detecting reused NAA assignments outside observed scope.

No unresolved architecture finding remains:

- **Native/disconnected:** legacy Java SDK PAK only; JDK HTTPS/XML vim25 SOAP
  is a practical self-contained choice with no Python, containers, services,
  array API, installation-time downloads or borrowed adapter libraries.
  Generated bindings require separate dependency/license/classloader proof.
- **Security:** strict chain and configured-host validation on both network
  hops; explicit Operations-managed trust acceptance; injected-only Operations
  identity distinct from vCenter target credentials. No VMware credential
  harvesting, maintenance-file fallback, silent trust-all or second customer
  Operations password is proposed. Routing, RBAC, FIPS and trust propagation
  remain explicitly unverified on the RDM runtime matrix.
- **Identity:** composite vCenter UUID/MOID VM resolution preserves every
  supported foreign identifier and actual uniqueness flag. Existing mapping
  keys and sole global NAA token are unchanged. Missing, malformed, ambiguous
  or conflicting observations cannot produce a guessed relationship.
- **Qualification:** the intrinsic VPD83/canonical/opaque-UUID join policy is
  explicitly a proposed automatic evidence policy, not fabrication of an
  independent storage reference. This is acceptable architecture for Java
  implementation/tests; single-host laboratory corroboration is not converted
  into a global-assignment or cross-vCenter empirical claim.
- **Lifecycle:** bounded complete paging and typed faults prevent unreadable
  inventory from becoming empty success. An unresolved LUN does not destroy
  an independently valid VM/mapping association. Additive mechanisms are
  preserved; deletions remain disabled pending durable ownership and
  authoritative coverage, not merely two empty snapshots.
- **Multi-vCenter/migration:** overlapping writers remain blocked until
  coalescing/ownership/conflict behavior is proven. Keeping the adapter kind
  preserves full keys but does not prove adoption on a credential-required
  upgrade; quiescing, explicit configuration, rollback and deployed acceptance
  remain necessary. No production fixture-size workaround is introduced.

## Validation and remaining decision

This is a documentation-only architecture review. No Java compilation, PAK
build, SDK validation, comparison or live test was appropriate or performed.
Changed-document validation and whitespace checks were run independently.
The orchestrator records the complete documentation/content and path-audit
results for the increment.

Registry check: `knowledge/context/defects.md` contains no open defect naming
the RDM POC. Historical DEF-005/006 are closed; their transport/authentication
lessons are nevertheless checked against current source and retained as
explicit E4 implementation prerequisites, not assumed solved for this adapter.

**If implemented as designed:** customers can eventually configure a vCenter
credential and trust rather than manual fixture JSON, while unproven TLS,
ownership, multi-writer and cleanup behavior remains gated by technical proof.
**Next recommendation:** approve only the bounded in-memory Java transport,
decoder and composite-resolver increment; authorize publication/deployment
separately after its implementation and runtime evidence are reviewed.
