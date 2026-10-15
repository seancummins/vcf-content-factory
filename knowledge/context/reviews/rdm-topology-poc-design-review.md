# RDM topology SDK POC — independent design review

**Reviewer:** `sdk-adapter-reviewer` (independent, design-only pass)  
**Scope reviewed:** Increment C decision record and the amended lab-validation
plan; no adapter repository, source, package, or deployment exists.  
**Initial verdict:** **CHANGES REQUESTED — BLOCKING: 1**  
**Re-review verdict (2026-10-14):** **APPROVE — design-only; implementation,
build, package, and deployment remain blocked by the absent Integration SDK
artifact.**

This is not a review approval for an SDK adapter or a deployment. The POC is
correctly stopped before either exists, because the required Integration SDK
artifact is absent. Re-review confirmed the documentation correction below;
there are now zero remaining blocking findings in the design-only scope.

## Independent evidence

### C1 evidence and design boundaries

- The decision record correctly limits the POC topology to
  `VMWARE::VirtualMachine -> RdmMapping` and explicitly excludes
  `CanonicalLun`, collection scheduling, metrics, and removal behavior
  ([decision record](../../designs/managementpacks/vsphere-rdm-topology-sdk-poc.md)
  lines 5–14).
- The lab plan distinguishes the verified identity chain from relationship
  persistence, and correctly refuses to treat a Virtual Disk metric instance
  as a `ResourceKey` or topology endpoint (lab plan lines 23–43 and 168–178).
- The documented foreign identity is vCenter-scoped.  It requires the actual
  `VMEntityObjectID` and `VMEntityVCID` values and their real
  uniqueness-bearing flags, rather than a bare MOID (decision record lines
  44–48; lab plan lines 187–192).  This satisfies the identity direction in
  `knowledge/lessons/stitch-moid-not-unique-across-vcenters.md` and the
  uniqueness-flag requirement in
  `knowledge/lessons/cross-mp-foreign-key-uniqueness-flags.md`.
- The proposed call sequence is supported by local framework *source*, not by
  a compiled artifact: `RelationshipBuilder.parentForeign(...)` marks a
  foreign parent and its `build()` path calls additive
  `Relationships.addRelationships(...)`
  ([RelationshipBuilder.java](../../../src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/stitch/RelationshipBuilder.java)
  lines 180–199 and 278–314).  `VcfCfAdapter` attaches nonempty relationships
  to the active collection result (lines 804–809 and 945–970).  The proposed
  direction therefore does not use `setRelationships` against the VMware
  parent.
- The direction, persistence, duplicate-add behavior, first-collection
  timing, and removal semantics remain explicitly unproven until a separately
  approved deployment experiment (decision record lines 54–80).  That is the
  right gap classification under `vcfops-sdk-adapter` (“Gaps — name them,
  never hide them”) and RULE-002
  [`knowledge/rules/no-fabricated-metrics.md`](../../rules/no-fabricated-metrics.md).

### Artifact and repository gate — independently verified

Local inspection found:

- `javac 25.0.4.1` is available.
- `src/vcfcf_managementpacks/adapter_runtime/` is absent and a repository-wide
  search found **zero** `vrops-adapters-sdk*.jar` and
  `vcfcf-adapter-base*.jar` files.
- `content/sdk-adapters/rdm-topology-poc/` is absent.  The factory ignores
  that location by design (`.gitignore` lines 38–42); an adapter there would
  be an independent managed repository, not factory source.
- The managed-pak registry has no `rdm-topology-poc` entry.  This is correct
  for the present no-artifact stage: `knowledge/context/managed_paks.md`
  “Hard rules” says agents do not add registry entries themselves and the
  orchestrator adds one only after the repository exists (lines 31–45).
- No build, `validate-sdk`, or `pak-compare` could be run: there is no POC
  project and the decisive SDK JAR is absent.  No live endpoint, vCenter, or
  VCF Operations system was contacted.

The builder independently confirms that the decisive prerequisite is
`vrops-adapters-sdk-*.jar`: it rejects a build if it is absent from
`adapter_runtime/` and `VCFCF_SDK_JAR` is unset
([sdk_builder.py](../../../src/vcfcf_managementpacks/sdk_builder.py) lines
179–198 and 424–455).  It also confirms that `vcfcf-adapter-base.jar` is
generated from the in-repository framework source when absent, once the SDK
JAR is supplied (lines 114–140 and 171–214).

## Findings and re-review disposition

### B1 — RESOLVED: the build blocker now distinguishes the external SDK JAR from the generated framework JAR

**Initial severity:** BLOCKING (implementation-readiness documentation)  
**Authority:** `vcfops-sdk-adapter` (“Tier 2 Java SDK adapter” build loop);
`knowledge/rules/source-of-truth.md` (RULE-001); and
`src/vcfcf_managementpacks/sdk_builder.py` lines 114–214.

**Initial finding:** The prior wording grouped the absent
`vrops-adapters-sdk` and `vcfcf-adapter-base.jar` as though both were external
artifacts. The builder compiles the latter from the committed framework source
once the former is legitimately supplied.

**Re-review evidence:** The revised decision record now says that the
compatible `vrops-adapters-sdk-*.jar` is the **sole external build
prerequisite**, that the factory builds `vcfcf-adapter-base.jar` from
`adapter_framework/src/`, and that the Broadcom JAR must not be downloaded or
redistributed through this repository (decision record lines 82–90). This
exactly agrees with `sdk_builder.py` lines 114–214 and 424–455.

**Disposition:** RESOLVED. The independent local check still finds no
`adapter_runtime/` directory and zero matching SDK/framework JARs, so this is
an honest no-artifact gate rather than an implicit authorization to create or
build an adapter.

## Registry check

`knowledge/context/defects.md` was read in full for this review.  It contains
no open defect with `Affects: rdm-topology-poc`, `rdm`, or this unregistered
POC.  Existing open defects affect named established adapters or factory
subsystems, not this absent adapter candidate.  No closure is proposed and no
registry change was made, satisfying RULE-012
[`knowledge/rules/release-gate-defects.md`](../../rules/release-gate-defects.md).

## Remaining implementation prerequisites

1. Make a legitimately supplied compatible Broadcom Integration SDK JAR
   available locally, without downloading or redistributing it through this
   repository.
2. Create and register the independent RDM POC repository through the
   orchestrator's managed-pak process.
3. Provide the minimal compilable adapter, deterministic fixtures, and the
   focused cases named in the decision record.
4. Independently run `validate-sdk`, `build-sdk`, and `pak-compare`; return
   their paths and outputs for a code-level SDK reviewer pass.
5. Request a separate, explicit authorization before any install or
   relationship-persistence observation.  Compilation and packaging alone do
   not prove cross-management-pack relationship persistence.

