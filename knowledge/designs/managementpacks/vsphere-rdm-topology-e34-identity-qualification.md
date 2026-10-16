# E3.4 — Canonical LUN identity qualification

**Follow-up:** [E3.4.1](vsphere-rdm-topology-e341-integer-compatibility.md)
corrected SDK integer compatibility and independently replayed the captured
single-host evidence as **CONDITIONALLY QUALIFIED**. The original offline
preparation status below is retained for history, not the latest qualification.

**Evidence verdict: BLOCKED pending operator execution.** Offline inspection and
synthetic tests cannot establish that the lab exposes a qualifying descriptor.
The operator supplied a TrueNAS logical-unit NAA reference; its value is not
recorded here. It is a storage-side reference, not proof of equality with any
vSphere UUID/canonical name. No live calls or adapter changes in this increment.

## Evidence chain and current findings

Basis: [E3.3 architecture](vsphere-rdm-topology-e33-canonical-lun.md),
[API evidence map](../../context/api-maps/vsphere-canonical-lun-identity.md),
[independent architecture review](../../context/reviews/rdm-topology-poc-e33-canonical-lun-review.md),
and [lab record](vsphere-rdm-topology-lab-validation.md).

| Link / property | Evidence and qualification |
|---|---|
| TrueNAS logical unit → storage-side NAA | Operator-supplied UI observation. Reference has a full NAA6-length hex representation; assignment/association is not inferred from syntax. No storage-array API or credentials are needed. |
| RDM backing → current-host SCSI LUN | Prior lab exact `backing.lunUuid == ScsiLun.uuid`; must be freshly rechecked on precisely one RDM and one current-host device. No UUID→NAA conversion. |
| Host LUN → candidate global identity | Candidate fields are `durableName` and `alternateName[]` on `HostScsiDisk`/`ScsiLun` in `HostSystem.config.storageDevice.scsiLun`. VPD83 descriptor header and payload must establish binary, LU-associated NAA5/6 identity. Not yet observed in retained evidence. |
| Canonical name → storage-side NAA | Compare full independently decoded bytes with a strictly parsed whole-device `naa.` canonical name and the operator's `0x`-prefixed reference. Only hex presentation case/prefix syntax changes; no shortening, guessed padding, UUID slicing, path/partition stripping or substring matching. Pending. |
| Multiple hosts → same logical unit | Requires separate readable host inventories and equivalent qualified payloads. Prior single-host evidence does not establish it. Pending. |
| Across vCenters / repeated observations | No cross-vCenter or timestamped stability proof established. Global assignment presumes conformant storage and cannot exclude every clone/collision. Pending. |

Structural inspection of existing local SOAP reports confirmed namespace,
data-presence, canonical-class and descriptor fingerprints, but no retained
namespaceId/descriptor data sufficient for header decoding. The E3.2 discovery
report describes Operations candidates, not VPD representation. Raw values were
not printed, copied into this document or reconstructed from fingerprints.

The existing E2 VM → RdmMapping topology proof remains unchanged. The E3.2
16-candidate/zero-scoped-match observation does not establish categorical native
LUN absence and is not used as global-storage identity evidence.

## Probe scope and qualification contract

New explicit `scripts/rdm_lab_probe.py --mode lun-identity` uses existing
environment-only vCenter access and double execution guards. It reads SOAP
PropertyCollector data only; there are no Operations or TrueNAS API calls.
The selected VM remains `vm-71` in its configured owning vCenter, with exactly
one RDM, stable VM instance UUID/configuration version/runtime host before and
after capture. Missing objects/properties, faults or changing snapshots fail closed.

The current ESXi host is always included. Optional additional host MORs are
explicitly supplied by the operator through `RDM_PROBE_LUN_HOST_MOIDS` (comma
separated); this is not an unrestricted host inventory scan. Read permission
is required on the selected VM, about data and selected hosts' storage inventory.
Other-host evidence never establishes current-host accessibility.
At most 15 explicit host entries are accepted, without duplicates; the current
host is added automatically, for at most 16 observed hosts. Unreadable or
unmatched selected hosts prevent claiming equivalence for the requested set.

The decoder keeps `ScsiLun.uuid`, canonical device name, VPD designator payload
and host/path-specific names distinct. NamespaceId is ESXi's namespace byte,
not a substitute for the SCSI association/type header. Unknown encodings,
page80/payload-only representations, locally assigned NAA3, unsupported NAA/EUI
forms and ambiguous or contradictory eligible identities cannot qualify. The
narrow support policy is NAA5/6 only; a valid unsupported standard is not silently
converted to a supported one. A path/target-port WWN is not a volume identifier.

For a proven chain the proposed ResourceKey remains:

```text
adapter kind: vcfcf_rdm_topology_poc
resource kind: CanonicalLun
sole unique identifier: identity_token = scsi-vpd83:naa:<full-payload-hex>
```

The token uses validated complete payload bytes, not the full descriptor header.
Host, VM, disk key, path and vCenter are provenance, not components of this key.
No resource is created by the probe. VMware VM/RdmMapping identities are unchanged.

Descriptive evidence includes optional vendor/model/revision, display name,
serial, `lunType`, inherited `deviceType`, locality and capacity where supplied.
Capacity requires positive LBA block count × block size with checked arithmetic;
missing capacity is unknown, not zero. Display names/device paths are presentation
evidence and do not affect identity. Disagreement is reported, never resolved by
silently selecting a host. vSphere does not guarantee an array's internal volume,
pool or array serial-number naming.

## Operator procedure — not executed here

Use the existing Python environment with pyVmomi and the three configured
`RDM_PROBE_VCENTER_*` credential variables. No SDK JAR, management-pack build,
Operations credentials or VIM JSON session is required. Do not print credentials.
Run from the factory root. The existing ignored `tmp/rdm-lab-probes/` directory
must be owned by the operator and mode `0700`. All files below must be untracked,
ignored and exclusively created with `0600`; existing files are not overwritten.

First create the reference file through a hidden local prompt. Enter the exact
storage-side reference already supplied, including its `0x` prefix; never put it
on the command line or paste it into a tracked document:

```sh
.venv/bin/python - <<'PY'
import getpass
import runpy
import warnings
from pathlib import Path

probe = runpy.run_path("scripts/rdm_lab_probe.py")
path = probe["_lun_local_path"](Path("tmp/rdm-lab-probes/storage-reference.json"))
with warnings.catch_warnings():
    warnings.simplefilter("error", getpass.GetPassWarning)
    reference = getpass.getpass("Storage-side NAA (hidden): ")
probe["_write_report"](path, {"naa": reference})
print("Private reference file created; contents not displayed.")
PY
```

Then run the operator-initiated SOAP-only capture:

```sh
PYTHONPATH=src RDM_PROBE_VCENTER_VERIFY_SSL=false \
  .venv/bin/python scripts/rdm_lab_probe.py \
  --execute --allow-read-only-lab --mode lun-identity --profile devel \
  --storage-reference-file tmp/rdm-lab-probes/storage-reference.json \
  --output tmp/rdm-lab-probes/lun-identity-vm-71.json \
  --lun-evidence-output tmp/rdm-lab-probes/lun-identity-private-vm-71.json
```

Disabled TLS verification uses the established development-lab setting only.
To test other hosts, set `RDM_PROBE_LUN_HOST_MOIDS` locally to the approved host
MORs, then rerun with **fresh output filenames**. Do not substitute host display
names or guess MORs. No existing storage presentation or VMware configuration
is changed. Repeat later with fresh filenames for timestamped stability evidence.
Cross-vCenter observation requires a later explicitly scoped procedure; this
single-vCenter probe does not claim that proof.

Only the sanitized report may be shared: qualification/reason codes, observed
host counts, descriptor format/association, match booleans and fingerprints.
Opaque UUID and descriptor-ID text comparisons are reported separately from
decoded NAA equality; matching one does not imply interchangeability. A complete
well-formed port/target-associated alternate is excluded from LU identity, not
mistaken for a contradiction merely because it accompanies a valid LU designator.
The optional private evidence preserves matched-device identities/descriptors
for local inspection, not full unrelated inventory. Never commit or paste it.
Missing/malformed reference configuration must fail before network access.
Authentication/session cleanup does not modify VMware configuration.
Exit 0 means CONDITIONALLY QUALIFIED; BLOCKED and collection/output failures
exit 2. A blocked analysis can still preserve useful optional private descriptor
evidence. An exception cleans up outputs newly created by that execution.

## Decision and next increment

- **BLOCKED:** current offline evidence; or any incomplete, ambiguous,
  unsupported or conflicting required identity chain during capture.
- **CONDITIONALLY QUALIFIED:** a future run demonstrates exact current-host
  UUID join, LU-associated supported descriptor, canonical-payload equality and
  complete storage-reference equality. Report actual cross-host observations;
  one host alone does not prove cross-host equivalence. This supports proposing
  a bounded lab POC, not production/global collision guarantees.
- **QUALIFIED:** not claimed by this offline increment or by a single capture.
  Broader equivalence/stability still needs separately assessed evidence.

Next implementation recommendation remains conditional: after a reviewed
successful capture, propose the minimal owned CanonicalLun fixture POC with
two mappings converging on one stable key and additive local relationships.
Do not modify the installed POC or add a production collector in this increment.

## Offline verification

Implementation: `scripts/rdm_lab_probe.py`, `scripts/rdm_lun_identity.py` and
`tests/test_rdm_lun_identity.py`. The added 75 tests use synthetic identities only.
Six RDM suites: **262 passed / 5 skipped** (existing explicit SDK/local-output
prerequisites); no dependencies were installed. Full factory suite: **2,411
passed / 19 skipped / 131 deselected / 1 failed**. The unchanged
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`
failure was independently reproduced in isolation; no unrelated fix was made.
Full content/changed-document validation, skill parity and diff checks pass.
Path audit passes with six existing documented standing exceptions.

[Independent technical review](../../context/reviews/framework/rdm-lun-identity-e34.md):
**APPROVE, zero blocking findings**, covering offline implementation, not live
identity qualification. No real reference file was created, raw identifiers
committed, adapter modified, PAK built or VMware endpoint contacted.
