# API map: native Java automatic RDM discovery

## Provenance

- **Authored by:** api-cartographer, independent E4.1 research context.
- **Target instance:** none; offline inspection only, no endpoint contacted.
- **Last updated:** 2026-10-15.
- **Update history:**
  - 2026-10-15 — Initial automatic-discovery API/transport map.
- **Evidence basis:** existing repository probes, independent managed-adapter
  source, prior documented SDK/platform observations. No private inventory read.
- **Reproducibility:** managed adapter source is independently versioned and
  retrieved through `knowledge/context/managed_paks.md`; source paths below are
  not factory-owned source. No vendor artifacts were downloaded.

## Transport recommendation and dependency boundary

Use the supported vSphere Web Services **vim25 SOAP contract**, executing inside
the native legacy Java Operations adapter. The immediate transport recommendation
is a small, hardened JDK HTTPS/XML client, not generated JAX-WS bindings.
`content/sdk-adapters/compliance/src/com/vcfcf/adapters/compliance/VSphereClient.java`
documents the build-43 transition: on Operations 9.1 parent-first loading paired
`javax.xml.ws` API with a Jakarta provider, breaking generated `VimService`
initialization. That implementation subsequently removed vim25/JAX-WS/SAAJ JARs.
This is repository evidence of a deployment risk, not proof every supported
binding distribution is broken. [documented in local working source]

Generated Java vim25 classes remain conceptually a supported API binding choice,
but require explicit compatible-runtime/classloader and redistribution proof
before selection; they are not preferred merely because they compile offline.
Raw SOAP remains the supported vim25 protocol rather than an unofficial endpoint.
Do not copy compliance's property-reading algorithm wholesale: it still contains
legacy `RetrieveProperties` requests. Port the RDM probe's bounded, complete,
paged collection contract instead. [local inspection; proposed implementation]

| Candidate | Required-data evidence | E4.1 disposition |
|---|---|---|
| vim25 SOAP `/sdk` | Existing Python probes collect typed RDM backing, host LUNs and complete descriptors. Native Java SOAP implementation already exists elsewhere in factory adapters. | Recommended baseline. [repository evidence] |
| Virtual Infrastructure JSON | Existing lab record cites typed `VirtualDiskRawDiskMappingVer1BackingInfo`; probe supports ordinary/boxed device arrays and explicit backing subtype tags. Lab version/auth/complete parity remains unproven. | Not required; defer transport parity. [repository evidence] |
| vCenter vAPI REST | No inspected repository evidence establishes complete typed RDM backing and durable/alternate SCSI descriptor parity. | Insufficient for this collector; do not assume the generic VM-disk endpoint substitutes for vim25. [offline evidence limitation] |

No Python runtime, container, sidecar, registry, storage-array endpoint or
installation-time dependency fetch belongs in the deployed pack. JDK HTTPS/XML
avoids a new third-party transport dependency; platform SDK remains provided by
Operations, never bundled. XML parser hardening and Java compatibility are still
implementation tests, not established by the transport choice alone.
[mandatory user constraints; proposed design]

## Session and collection operations

The compliance native client supplies exact request examples for
`RetrieveServiceContent`, `Login`, `Logout`, `CreateContainerView`, `DestroyView`,
with typed managed-object references and a `vmware_soap_session` cookie. The
vCenter endpoint is HTTPS `/sdk`; SOAP service namespace is `urn:vim25`.
Views/session objects are ephemeral API query infrastructure, not VMware
configuration mutations. [documented in local working source]

Use `RetrievePropertiesEx`, `ContinueRetrievePropertiesEx`, and
`CancelRetrievePropertiesEx` on
failure/abandonment; existing `scripts/rdm_lab_probe.py::_collect_properties`
uses `RetrieveOptions(maxObjects=64)`, explicit `PropertySpec.pathSet`, and typed
object specs. Reject unexpected/duplicate objects, duplicate property names,
missing objects, required omissions and `ObjectContent.missingSet` faults.
Do not interpret incomplete permission-limited inventory as successful zero RDMs.
Production enumeration must also record its caller-visible scope: absence of an
object outside that scope is not evidence of deletion. [existing probe contract;
production scope policy proposed]

## Exact field map and joins

| Object/source | Requested path or typed field | Use and boundary |
|---|---|---|
| `ServiceContent.about` | `instanceUuid`, `version` | Owning vCenter authority and API compatibility; never infer from hostname. [existing SOAP capture] |
| `VirtualMachine` MOR | type/value (`VirtualMachine`, MOID) | vCenter-scoped VM identity; bare MOID never global. [existing probe] |
| `VirtualMachine` | `config.instanceUuid` | Stable mapping tuple component, not BIOS `config.uuid`. [existing fixture contract] |
| `VirtualMachine` | `config.changeVersion`, `runtime.host` | Pre/post consistency fence and current-host inventory join; retry boundedly or mark unstable if changed. [existing capture] |
| `VirtualMachine` | `config.hardware.device` | Full typed devices; select `VirtualDisk` with `VirtualDiskRawDiskMappingVer1BackingInfo`. Unknown backing representations are not zero RDMs. [existing probe] |
| `VirtualDisk` | `key`, `controllerKey`, `unitNumber`, `deviceInfo.label` | Key is stable mapping component; controller/unit/label only correlation/display evidence. [existing probe] |
| RDM backing | `lunUuid`, `deviceName`, `fileName`, `compatibilityMode` | Opaque UUID joins LUN inventory; other fields describe attachment/backing, not global LU identity. [existing probe] |
| `HostSystem` | `config.storageDevice.scsiLun` | Current host's complete LUN inventory, cached once per host/cycle. [existing probe] |
| `ScsiLun` | `uuid`, `canonicalName` | Require exact backing `lunUuid == uuid` and exactly one current-host result. Other-host UUID equality is independent visibility evidence, not current-host accessibility. [existing probe] |
| `ScsiLun` | `durableName`, `alternateName[]` | Structured namespace/namespaceId/data representations; validate descriptor evidence below. [existing identity capture] |
| `ScsiLun` | `descriptor[].id`, `descriptor[].quality` | Alternate descriptor metadata; a canonical-like text ID alone does not prove LU association. [existing identity validator] |
| `ScsiLun` | `vendor`, `model`, `revision`, `serialNumber`, `displayName`, `lunType`, `deviceType` | Optional reported properties, not unique array-volume names or IDs. [existing capture] |
| `HostScsiDisk` subtype | `capacity.block`, `capacity.blockSize`, `localDisk` | Checked positive signed-64-bit byte product; locality is presentation evidence. Handle missing/unsupported fields explicitly. [existing capture/validator] |

Sources: `scripts/rdm_lab_probe.py::_capture_soap_fixture`,
`_raw_lun_identity`, `_validate_fixture_snapshot`; `scripts/rdm_lun_identity.py`.
The probe's explicit single-VM selection is a lab guard, **not** the production
discovery design. Bulk container-view enumeration followed by bounded batches is
proposed; preserve typed MORs and consistency fences. [offline source inspection]

## Logical-unit descriptor contract

`ScsiLunDurableName` supplies `namespace`, byte-valued `namespaceId`, and byte-array
`data`; `namespaceId` is not the VPD designator type. The qualified lab evidence
contained full four-byte page-83 descriptor headers plus payload in NAA durable
and alternate representations. Java signed bytes preserve unsigned bits with
`b & 0xff`. Binary code set, LU association zero, designator type three, reserved
bits, declared length and supported NAA5/6 payload length must all validate.
Target-port/device designators cannot establish LU identity. Canonical payload
must exactly agree under approved prefix/hex-case handling. An opaque SCSI UUID
is not decoded into NAA. [E3.4.1 qualified evidence; existing validator]

Automatic operation cannot retain the POC's independently supplied
`storage_reference` requirement or synthesize `storage_reference = canonicalName`.
The next design must explicitly approve an automatic evidence policy: exact
current-host backing-UUID join + one unambiguous qualified LU-associated NAA +
complete canonical agreement. This retains the key format, but changes the source
of qualification evidence; distinguish it from independent storage-side
confirmation. Contradictory/malformed claims remain quarantined. [proposed policy
transition requiring independent architecture review]

## Operations VM lookup contract

Existing `scripts/rdm_lab_probe.py::_capture_fixture_resources` uses paged
`GET /api/resources` constrained to adapter `VMWARE` and resource kind
`VirtualMachine`; inspect every page and complete ResourceKey. Resolve exactly
one result with **both** `VMEntityObjectID == VM MOR.value` and
`VMEntityVCID == ServiceContent.about.instanceUuid`, both uniqueness-bearing.
Display names are only search hints. Preserve all identifier names/order/values
and actual boolean uniqueness flags. Existing SDK compatibility supports empty
strings for nonunique identifiers; absent/null values remain unsupported and
must not be silently coerced. [existing exporter and E2.2 compatibility contract]

The deployed lookup should use the collector-injected per-instance Suite API
identity, not an operator-supplied Operations password or another VMware
integration's credentials. See
`knowledge/lessons/cross-mp-stitch-cp-identity-and-edge-mechanics.md` and
`knowledge/context/api-surface/per-instance-suiteapi-credential-contract.md`.
The credential carrier is SDK-public and its use has repository bytecode/runtime
evidence, not blanket support certification. Crypt linkage, endpoint routing,
RBAC and Cloud Proxy behavior remain release-qualified observations; verify them
for the RDM adapter and each targeted collector role. [documented
platform/framework behavior; RDM deployment verification pending]

Do not reuse `ForeignResourceResolver` unchanged: its single-identifier cache can
collapse duplicate keys with last-write-wins behavior, unsuitable for scoped
VM/MOID uniqueness. Do not reuse `SuiteApiStitchClient`'s permissive TLS transport
unchanged either. The RDM resolver needs complete pagination, scoped uniqueness
and ambiguity rejection, plus authenticated transport with explicit trust and
hostname validation. These cautions derive from the corresponding sources under
`src/vcfcf_managementpacks/adapter_framework/src/com/vcfcf/adapter/stitch/`;
they are architectural requirements, not framework changes made this increment.
[local source inspection; proposed stricter RDM contract]

## TLS and unresolved implementation proofs

`content/sdk-adapters/compliance/src/com/vcfcf/adapters/compliance/VCenterCertificates.java`
provides platform trust plus explicit dialed-host certificate-name enforcement,
certificate-review URL support and Cloud-Proxy/provider compatibility handling.
Its build-94 comment records BouncyCastle JSSE sockets lacking peer-host metadata;
therefore a default verifier or chain-only success is insufficient. Reuse the
verified policy, not insecure TLS probe settings. Internal PKI trust/accepted
certificates must follow platform configuration across placement/failover; never
manual node-local trust files. [local working source; RDM runtime proof pending]

Remaining implementation evidence: authenticated read-only privilege scope;
paged SOAP typed XML/base64 descriptor decoding and fault tests; supported
collector/JDK matrix; ambient Suite API RBAC; bulk inventory consistency and
bounded resource usage; accepted-cert propagation/failover; multi-host and
cross-vCenter identity/collision observations. None was executed this increment.
[unverified requirements]

## Related evidence

- [RDM lab validation](../../designs/managementpacks/vsphere-rdm-topology-lab-validation.md).
- [Canonical identity API semantics](vsphere-canonical-lun-identity.md).
- [E3.4.1 qualification](../../designs/managementpacks/vsphere-rdm-topology-e341-integer-compatibility.md).
- [E3.3 architecture](../../designs/managementpacks/vsphere-rdm-topology-e33-canonical-lun.md).
- [Managed adapter registry](../managed_paks.md).
