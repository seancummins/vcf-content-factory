# RDM topology SDK POC — architecture decision record

## Decision

Implement a deliberately minimal Tier 2 proof only after the local Integration
SDK artifact is available. Its topology is:

```text
VMWARE::VirtualMachine --(additive foreign-parent edge)--> RdmMapping
```

`CanonicalLun`, live vCenter collection, metric emission, collection schedule,
and production deletion/lifecycle handling are out of scope. The eventual
production topology remains `Existing VM → RdmMapping → CanonicalLun`.

## Verified lab evidence

The read-only lab findings are recorded in
`knowledge/designs/managementpacks/vsphere-rdm-topology-lab-validation.md`:

- RDM `lunUuid` equals host `ScsiLun.uuid`; the resolved LUN supplies NAA
  canonical/durable-name evidence.
- `VMEntityObjectID` plus `VMEntityVCID` uniquely resolves the existing
  Operations VM, with both real uniqueness flags true.
- Controller/unit, disk label, and backing filename jointly correlate the RDM
  with one Operations metric instance.

The metric instance is diagnostic/UI evidence only. It is not a ResourceKey
and cannot be a topology endpoint.

## SDK implementation design

The local cleanroom specification documents
`com.integrien.alive.common.adapter3.ResourceKey`,
`ResourceIdentifierConfig`, and `Relationships`; the factory helper is
`com.vcfcf.adapter.stitch.RelationshipBuilder`.

1. Define pack-owned `RdmMapping` with stable composite identifiers:
   `vcenter_instance_uuid`, `vm_instance_uuid`, and `virtual_disk_key`.
   The POC fixture supplies these deterministic values; it does not query
   vCenter.
2. Construct the local `RdmMapping` `ResourceKey` with its exact declared
   identifier flags.
3. Construct the foreign `VMWARE::VirtualMachine` ResourceKey from the real
   Suite API `resourceKey.resourceIdentifiers[]` result. Preserve every
   identifier name, value, and `isPartOfUniqueness` flag returned by the API;
   never synthesize or mark identifiers unique locally. The validated minimum
   identity is `VMEntityObjectID` + `VMEntityVCID`.
4. Call `RelationshipBuilder.parentForeign(foreignVmKey, rdmMappingKey)`,
   then `adapter.addRelationshipsToCurrentCycle(builder.build())`. The helper
   emits additive `Relationships.addRelationships`, not replacing
   `setRelationships`, so it does not modify VMWARE-owned relationships.

Direction is chosen as existing VM parent → local mapping child because it
matches the desired UI navigation. The cleanroom evidence says either
direction can persist, but exact topology UI presentation and persistence are
deployment-proof questions.

## Lifecycle contract

- Repeated collection reasserts the same additive edge; expected idempotence
  is SDK/platform behavior requiring deployed proof.
- An unresolved/ambiguous foreign VM skips the edge and surfaces an explicit
  collection diagnostic; it must never fall back to a bare MOID or name.
- The POC does not remove obsolete mappings. Production design must choose
  supported removal semantics after a proof establishes whether additive
  foreign edges are adapter-scoped and removable without affecting VMWARE.

## Supported evidence vs deployment proof

Supported locally: `RelationshipBuilder.parentForeign` and
`VcfCfAdapter.addRelationshipsToCurrentCycle` use the SDK relationship
collection objects; `parentForeign` uses additive relationship calls. Sources:
`src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/stitch/RelationshipBuilder.java`,
`src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/VcfCfAdapter.java`,
and `knowledge/context/cleanroom-spec/spec/07-relationships-cross-mp.md`.

Unproven until deployment: actual persistence and UI direction, duplicate-add
behavior, foreign-key resolution with this exact VM kind, first-collection
timing, and safe removal of obsolete RDM mappings.

## Build blocker

This checkout has a JDK but no compatible `vrops-adapters-sdk-*.jar` under
the factory runtime. That Broadcom Integration SDK JAR is the sole external
build prerequisite; the factory builds `vcfcf-adapter-base.jar` locally from
the committed `adapter_framework/src/` source after the SDK JAR is supplied.
Do not download or redistribute the Broadcom JAR through this repository.
Until it is legitimately available locally, no adapter repository or
non-compilable placeholder is created. Once it is available, create the independent
`content/sdk-adapters/rdm-topology-poc/` repository and require:

- focused fixture tests for composite foreign identity, same MOID in two
  vCenters, repeated collection identity, unresolved foreign VM, local RDM
  key, and no VMWARE-owned mutation;
- `validate-sdk`, `build-sdk`, and `pak-compare`; and
- an independent `sdk-adapter-reviewer` approval before any deployment
  request.

No compilation or package can prove foreign relationship persistence; a
separately authorized devel installation and topology observation is required.
