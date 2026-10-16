# E3.2 — Read-only Operations LUN discovery

Status: **offline implementation; INSUFFICIENT EVIDENCE for native reuse until operator execution**.
No live requests were made during this increment. This does not justify creating
CanonicalLun objects. Preserve the proven existing VM → RdmMapping implementation.

## Evidence and approach

Continue the [E3.1 assessment](../../context/reviews/rdm-topology-poc-e31-lun-identity-assessment.md)
and [lab-validation record](vsphere-rdm-topology-lab-validation.md).
`scripts/rdm_lab_probe.py --mode lun-discovery` reacquires exactly one RDM for
`vm-71` using SOAP PropertyCollector. It requires stable VM instance UUID,
configuration version and current host before/after capture, an exact backing
lunUuid → current-host ScsiLun.uuid match, and a nonempty canonicalName.
A UUID visible only on another host is not evidence of local accessibility.

Suite API requests (verified against `reference/docs/operations-api.json`):

- Paginated GET `/api/resources?page=N&pageSize=1000`: census of resource kinds
  actually present in the caller-visible inventory, not assumed native kinds.
- For likely storage candidates, GET `/api/resources/{id}` and
  GET `/api/resources/{id}/properties`: complete key and direct
  `{resourceId, property:[{name,value}]}` response. Resource IDs must agree.
- Normal Suite API token acquisition and POST `/api/auth/token/release` cleanup;
  releasing authentication does not modify monitored inventory. Cleanup failure
  is recorded without hiding the primary result.

No statistics, relationships or configuration mutation endpoints are called.
The minimum generic first pass is one paginated inventory census plus two reads
per candidate; there is no justified native LUN kind/property name to filter on
yet. Kind-name hints (`lun`, `scsi`, `storage`, `volume`, `disk`, `datastore`)
select candidates only, never establish physical-LUN granularity. An explicitly
bound observed kind is searched even if its name lacks these hints. Unknown
opaque kinds remain an evidence limitation, not proof that native LUNs are absent.
Bounds: 100,000 resources / 1,000 pages / 2,000 candidates; exceeding them fails
closed. Permission-filtered inventory can never establish global absence.

## Operator execution — not executed by this increment

Prerequisites: existing Python environment including pyVmomi and factory client;
existing development profile/credential environment, without secrets in command
arguments. vCenter read permission for VM config/runtime, host storage inventory
and about.instanceUuid; Operations login and read visibility for the relevant
resources, full keys and properties. No write privileges are needed. Missing
properties/faults, pagination inconsistencies and unreadable responses fail closed.

From the factory root, prepare the existing ignored scratch directory as owned
by the invoking operator with mode `0700`. Do not change ownership or overwrite
existing outputs. The command creates output files exclusively with `0600`.

```sh
PYTHONPATH=src RDM_PROBE_VCENTER_VERIFY_SSL=false VCFOPS_DEVEL_VERIFY_SSL=false \
  .venv/bin/python scripts/rdm_lab_probe.py \
  --execute --allow-read-only-lab --mode lun-discovery --profile devel \
  --output tmp/rdm-lab-probes/lun-discovery-vm-71.json \
  --lun-evidence-output tmp/rdm-lab-probes/lun-candidates-private-vm-71.json
```

TLS verification disabled here reflects the separately accepted development-lab
settings, not a production recommendation. Both credential sets must already be
available through the existing environment/profile conventions. Do not print them.
No SDK JAR, Java parser, fixture reconfiguration or management-pack build is needed.

Terminal/report output contains only adapter/resource kind metadata, counts,
resource UUID fingerprints, static match methods/statuses/confidence and cleanup
status. Candidate key names/values, display names, property values, host IDs and
source storage identifiers are not printed. The optional private evidence file
preserves every candidate's complete ResourceKey, identifier values/flags and
ordering, plus property **names** and exact-value field-name hints. It contains
sensitive inventory: inspect only locally; never paste or commit it. It is
explicitly unqualified evidence, not a relationship target. Property values
unrelated to correlation are not exported.

## Qualification and decision criteria

First-pass exact UUID/canonical value matches are **unverified semantics**.
Do not infer field meaning from a display name or a coincidental substring.
The operator must establish physical-LUN granularity and actual identifier or
property semantics from observed metadata and authoritative adapter documentation.
If this cannot be established, stop with INSUFFICIENT EVIDENCE.

To evaluate a documented interpretation, create an ignored owner-only (`0600`)
bindings JSON directly in scratch, using **actual observed** field names. This
synthetic example is a schema illustration, not an asserted VMware kind or key:

```json
{
  "adapter_kind": "EXAMPLE", "resource_kind": "ExamplePhysicalLun",
  "granularity": "physical_lun",
  "uuid": {"source": "identifier", "name": "ExampleLunUuid"},
  "canonical_name": {"source": "property", "name": "ExampleCanonicalName"},
  "vcenter_instance_uuid": {"source": "identifier", "name": "ExampleVcenterUuid"}
}
```

At least one of `uuid` and `canonical_name` is required. vCenter scope is always
required; array-only/global storage scope is not yet supported. Never synthesize
a missing scope or normalize/truncate identities. Repeat the first command with
fresh output filenames plus `--lun-bindings tmp/rdm-lab-probes/lun-bindings.json`
and, optionally, `--lun-handoff-output tmp/rdm-lab-probes/lun-resource-handoff.json`.
All configured storage identifiers and vCenter scope must match exact full values.
Conflicting UUID/canonical values, missing bound roles, incomplete SDK keys or
competing unqualified exact-value candidates prevent reuse. Same UUID with a
proven different vCenter scope does not establish a match in the source scope.

REUSE requires exactly one scoped match with an SDK-representable complete key:
nonempty kind/name metadata, nonempty identifier list, explicit boolean uniqueness
flags, no case-insensitive duplicate names and at least one uniqueness-bearing
identifier. Explicit empty strings are retained only for nonunique identifiers;
omitted/null values cannot be faithfully passed through the SDK and block reuse.
ASCII identifier-name comparison is verified; other names remain unqualified.
The handoff is written only for a qualified unique match and preserves the exact
ResourceKey rather than rebuilding it from matched fields. Operator bindings are
an explicit semantic assertion, not automatic vendor/schema verification.

Statuses distinguish no candidate kinds observed, no unique match, missing scope,
conflicting identity/scope, ambiguity and incomplete evidence. Only `unique_match`
returns REUSE with `high_with_operator_bindings` confidence. All other results are
INSUFFICIENT EVIDENCE, never an automatic CANONICALLUN decision. A successful read
with insufficient evidence exits 0; acquisition/output failures exit 2 with static
sanitized reasons. Read report status/recommendation, not exit code alone.

If reuse is proven, a later approved increment can use additive
`childForeign(mapping, lun).buildDelta(false)` to preserve
existing VM → RdmMapping and add RdmMapping → existing LUN. No foreign relationship
is emitted by this probe; API matching does not prove deployed edge persistence.
If evidence is insufficient, request only missing kind semantics, storage identity
or scope; do not create duplicate LUN resources based on absence of proof.

## Offline validation and review

Synthetic analysis/API/guard/file/redaction tests live in
`tests/test_rdm_lun_discovery.py`; no lab fixture is used.
Independent review: `knowledge/context/reviews/framework/rdm-lun-discovery-e32.md`.
Live counts, candidate kinds, correlation confidence and reuse disposition remain
pending the operator's separately initiated run.

Final checks: 42 new discovery tests pass; five combined probe suites yield
187 passed / 5 skipped without an explicitly supplied SDK, and independent
SDK-enabled verification yields 191 passed / 1 protective skip. Full factory
suite: 2,336 passed / 19 skipped / 131 deselected / 1 failed. The unrelated,
unchanged `test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo` in
`tests/test_common_setup.py` also fails in isolation (unknown ignore status
instead of the expected not-a-repository wording); no unrelated fix was made.
Full content validation, changed-document checks, skill parity and diff checks
pass. Path audit is clear with six existing documented standing exceptions.
Independent verdict: APPROVE, zero blocking findings. Adapter source, vendor
references and `.claude/` remain unchanged. No live evidence was collected.
