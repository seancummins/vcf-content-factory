# E3.5 — independent SDK review, build 8

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT implementation findings.**
Independent implementation, test, compilation, build, artifact and documentation
checks complete. This approves the offline development candidate, not deployment.

## Scope and authority

Independent `sdk-adapter-reviewer` context; source was reviewed read-only against
[E3.3](../../designs/managementpacks/vsphere-rdm-topology-e33-canonical-lun.md),
[E3.4.1](../../designs/managementpacks/vsphere-rdm-topology-e341-integer-compatibility.md),
the SDK skill's stitching/build/gap contracts, the reviewer doctrine, RULE-005,
RULE-008, RULE-012 and RULE-014. Factory fixture-preparation tooling receives a
separate framework review. No private lab evidence or credentials were read.

- Factory HEAD: `f53bb603e0b112e4febe9acc09cb4d2c6b1f7315`, plus uncommitted E3.5 work.
- Independent adapter HEAD: `dc7e83afc7aee75536faaf6dd7b86628f74588c1`, plus build-8
  changes. The independent Git boundary is intact; no commits were created.
- Candidate: `vcfcf_sdk_rdm_topology_poc.0.0.0.8.pak`, SHA-256
  `de78efc3715244a1f2b101c721ff9ab70cdfd22a728cf84a9e4fca167e04d849`.
- Superseded intermediate build 7 is not the candidate. Build 8 includes the
  reverse scoped-VM-instance consistency check and corresponding regression.

Development PAKs and the SDK dependency are local-only, not reproducible repository
citations; their relevant findings and exact hashes are summarized here. Reference
selection remains the previously approved Synology `v1.0.0.30` release artifact,
SHA-256 `beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`.
Local proprietary SDK SHA-256 independently verified:
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
It was used on the compile classpath only.

## Implementation findings

No Java correctness blockers found:

- `CanonicalLunIdentity.parse` requires exact backing/SCSI UUID equality and
  independently provided canonical/reference agreement. It validates full binary
  VPD83 headers, supported namespace, namespace-byte bounds, reserved bits,
  association, declared length and complete NAA5/6 payload. Exactly one distinct
  eligible LU payload is required. Port/target descriptors cannot substitute for
  LU identity; contradictory eligible payloads fail. Approved prefix/hexadecimal
  case handling is the only identity representation conversion.
- The `CanonicalLun` key has exactly one unique identifier,
  `identity_token=scsi-vpd83:naa:<payload>`. It contains no VM, host, disk,
  vCenter or adapter-instance scope. Two synthetic scoped VM attachments converge
  on one owned key; distinct payloads stay distinct.
- Bounded schema-v2 attachments validate completely before emission. Duplicate
  mappings, conflicting LU observations, conflicting opaque UUID-to-token
  assignments and inconsistent scoped VM ownership fail closed. Version-1
  build-6 fixtures remain mapping-only. Existing mapping identity and exact
  foreign-key values/uniqueness flags are preserved, including supported explicit
  nonunique empty strings. Bare-MOID identity remains rejected.
- Enumeration emits only the two owned kinds, deduplicating keys. Foreign
  VM→mapping still uses `parentForeign(...).build()`. Owned mapping→LUN uses
  `parent(...).buildDelta(false)`. Actual SDK relationship items are additive,
  not clear-first, and have no VMware-owned children/removal/full-set operations.
- Descriptions are allowlisted optional fixture properties, not independently
  reacquired facts. Provenance/assessment explicitly identify the single-authority
  fixture POC. Capacity uses positive decimal dimensions and checked signed-long
  multiplication; simultaneous same-key descriptions require exact consensus.
- Adapter source introduces no network, file or environment access. No credentials,
  array client, production collector, stale-edge cleanup or LUN garbage collection
  is introduced. All configuration remains the Operations-managed nonidentity
  `fixture_json` setting with `isCredentialRequired="false"`.

## Independent verification

| Check | Actual result |
|---|---|
| Focused Java script, actual SDK | PASS: seven original topology tests; 42 invalid runtime/lifecycle cases; 34 invalid-LUN cases plus shared-LUN, distinct-key, consistency, representation, property, direction and repeated-output matrices |
| SDK identifier behavior | PASS: values/order/uniqueness matching and six-identifier empty-string roundtrip preserved |
| Descriptor loader | SKIP: missing local `log4j-api`; DOM credential-free descriptor contract checked, not claimed full runtime descriptor loading |
| `validate-sdk` with explicit SDK | PASS, six source files compile; standard existing source/target-11 compiler warning |
| Independent scratch-source `build-sdk`, pinned structural gate | PASS, development version `0.0.0.8`; exit 0 |
| Exact candidate structural comparison | **0 BLOCKING / 3 WARNING / 23 INFO**, exit 0 |
| Archive integrity / nested content | PASS; candidate and independent rebuild have all 73 recursively expanded non-directory payload leaves byte-identical |
| Packaging / restricted SDK exclusion | PASS; only adapter JAR and framework JAR bundled; no proprietary SDK classes/JAR, test classes, fixture files or environment file entries |
| Credential-free metadata | PASS; exact source descriptor embedded, no CredentialKinds or credentialKind references |
| Sensitive-literal/package audit | No known lab-name/credential literals detected; adapter classes contain no hardcoded fixture |
| Adapter diff whitespace | PASS |
| Documentation parity | PASS after restoring explicit owned-runtime-edge supplements in generated landing/inventory documents; root README, overview and fixture contract agree |

The scratch rebuild SHA-256 was
`1a7295f9aaf0da4007ee3e47dee95c7a5103dc299631fe2cbbefe5422bf10435`.
Archive timestamp metadata differs; all recursively expanded contents, including
the ZIP-formatted `overview.packed`, match the candidate. This is reproducible
compilation/payload evidence, **not a claim of deterministic archive bytes**.
Final rebuild used a scratch source copy to avoid regenerating adapter documents.

### Unchanged structural comparator findings

All actual findings are retained, without waiver, suppression or reclassification:

- WARNING W1 / D8: adapter-instance identifier count 1 versus 3.
- WARNING W2 / D23: TraversalSpecKind count 0 versus 1.
- WARNING W3 / D25: candidate has no populated TraversalSpecKinds.
- INFO I1 / D1 and I2 / D6: independently valid optional credential-contract
  differences (credential-free candidate versus credentialed reference).
- INFO I3–I5 / M7: description, display name and name differences.
- INFO I6–I10 / A1: candidate adapter icon, two data-kind icons, adapter-instance
  icon and adapter JAR differ.
- INFO I11–I22 / A2: reference adapter icon, nine reference data-kind icons,
  adapter-instance icon and adapter JAR differ.
- INFO I23 / D17: two versus nine data kinds.

These remain comparator output, separate from code-review findings. Missing
TraversalSpecs do not establish missing runtime relationships: the SDK emits
relationships explicitly; actual topology acceptance/UI rendering remain lab tests.

The existing documentation generator does not model owned runtime-only edges.
Final landing/inventory supplements explicitly correct its generic Suite API
wording and empty parent columns for this adapter, describe both additive SDK
paths, and explain the diagram limitation. They must be restored after future
generation; preserved hand-maintained overview/fixture documents are authoritative.
No false cross-MP metadata or framework change was introduced. Supplement-only
changes do not alter the candidate PAK; its checksum was rechecked unchanged.

## Registry and deployment boundary

`knowledge/context/defects.md` was checked: **no open entries affect this adapter**;
no closure or registry modification is proposed. No comparator or framework policy
was changed. Existing release/CI settings and external configuration were untouched.

No live calls, installation, configuration changes, resource/relationship mutations,
commits, pushes or publication occurred. Local compilation and fixtures do not prove
Operations acceptance, multiple-parent convergence, local-edge persistence, UI
visibility, failover or cleanup. E2 proves the old VM→mapping edge only. Additional
host/vCenter/stability observations and collision controls remain necessary before
any global-deduplication claim. A separately authorized controlled development-lab
experiment must preserve VMware topology and verify exact owned resources/edges.

**If shipped as-is:** version-1 fixtures retain the proven mapping-only behavior;
strict version-2 fixtures can emit shared CanonicalLun endpoints and additive
local edges. An operator must still obtain separate lab authorization and prove
new edge acceptance/persistence and safe cleanup before relying on live topology.
