# E3.4 LUN identity rejection — independent diagnosis

**Disposition: APPROVE diagnosis and narrowly scoped correction proposal; no
implementation reviewed or authorized here.** Offline inspection only. No live
requests, adapter changes, or raw inventory copied into this report.

## Independently verified causes

The rejection is a Python runtime-type incompatibility, not evidence that the
captured namespace identifier is absent:

- `scripts/rdm_lun_identity.py:45` requires `type(namespace_id) is int`.
- Its descriptor-byte check at line 50 has the same exact-type restriction.
- Its capacity check at line 135 repeats it for `block` and `blockSize`.
- `scripts/rdm_lab_probe.py:1015` preserves SDK scalar objects; converting an
  SDK data array with `list(data)` does not convert its elements.

The locally installed pyVmomi schema declares
`vim.host.ScsiLun.DurableName.namespaceId` as `byte`, `data` as `byte[]`, and
`vim.host.DiskDimensions.Lba.block` as `long` (`blockSize` is `int`).
`VmomiSupport` defines `byte` and Python-3 `long` as subclasses of `int`;
`SoapAdapter` constructs the declared scalar type while deserializing SOAP.
These are valid integers but fail `type(value) is int`.

An independent synthetic `SoapAdapter.Deserialize` reproduction with a valid
LU-associated binary NAA descriptor confirmed all three incompatible scalar
locations. The unchanged analyzer rejected the namespace, produced zero LU
designators, and rejected positive capacity dimensions. JSON serialization and
reload converted SDK integer subclasses to builtin integers; the same descriptor
then decoded as `valid_lu_naa` and capacity passed. This is diagnostic evidence,
not a recommendation to use JSON roundtripping as validation.

Private evidence was inspected locally by field types and validation outcomes
only. It contains one host observation; its validated vendor/model/type fields
are nonempty strings. The `descriptive_values_valid=false` result is caused by
the invalid-capacity branch setting the shared descriptive-invalid flag—not by
missing vendor or model data. Saved JSON no longer retains the original SDK
scalar subclasses. Offline replay decoded one distinct LU identity, with two
valid LU-associated NAA representations; capacity and descriptions passed.
Independent operator-reference comparison was separately verified by the
orchestrator against the existing private reference file.

## Smallest justified correction

Permit integer subclasses, explicitly excluding booleans, in the three numeric
checks; retain all existing bounds, complete descriptor-header checks, binary
code set, namespace recognition, LU association, NAA format, full-payload equality,
scope and ambiguity checks. Alternatively normalize only verified SDK integer
scalars at capture boundaries. Do not coerce arbitrary strings/floats, infer an
NAA from an opaque UUID, or accept canonical-name equality without descriptor
proof. Fixing only `namespaceId` is insufficient: descriptor byte elements and
capacity also require coverage.

Add deterministic tests using actual SOAP-deserialized SDK objects, retaining
negative tests for booleans, strings/floats, out-of-range bytes, invalid capacity,
and non-LU associations. Existing E3.4 tests independently run: **75 passed**;
their builtin-integer fixtures did not exercise this incompatibility.

## Evidence and next step

No new live query is necessary to diagnose this rejection or qualify the
**captured single-host** descriptor against the already saved independent
reference. The saved evidence supports a **CONDITIONALLY QUALIFIED** single-host
lab conclusion after the documented offline replay; it does not validate the
unchanged live parser. Cross-host equivalence remains **not established**;
cross-vCenter equivalence and temporal stability remain untested. Those require
separately authorized observations, not inference from one host.

Schema/semantics authority:
[ScsiLunDurableName](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.ScsiLun.DurableName.html),
[HostDiskDimensionsLba](https://developer.broadcom.com/xapis/vsphere-web-services-api/latest/vim.host.DiskDimensions.Lba.html),
and the [identity evidence map](../../api-maps/vsphere-canonical-lun-identity.md).
The actual installed pyVmomi SOAP decoder and schema supplied the runtime-type
proof. No proprietary SDK material or raw descriptor payload is reproduced.
