# E3.4.1 SDK integer compatibility — independent review

**Verdict: APPROVE — zero blocking findings.** Review limited to the numeric
compatibility correction in `scripts/rdm_lun_identity.py` and its deterministic
tests. No adapter, SDK PAK, live inventory, or relationship changes reviewed.

## Verified implementation

The shared `_is_integer` predicate accepts `int` subclasses and explicitly
rejects `bool`. Only namespace-ID, descriptor-byte, and capacity-dimension checks
use it. This addresses the independently reproduced pyVmomi SOAP `byte`/`long`
incompatibility without coercing strings, floats, or missing values.

Existing byte bounds, positive capacity and signed-64-bit product ceiling,
descriptor length/header/code-set/type validation, namespace interpretation,
logical-unit association, complete NAA payload equality, backing UUID join,
ambiguity handling, and cross-host consistency checks remain intact. The locally
generated observation timestamp retains its original builtin-integer contract.
There is no canonical-only identity fallback or vendor-specific exemption.

New tests cover SDK integer subclasses, JSON representation parity, actual
SOAP deserialization through `_raw_lun_identity` without JSON roundtripping,
wrong types including booleans, out-of-range bytes, and nonpositive/overflowing
capacity. Seven additional SDK-wrapped negative cases verify namespace,
association, encoding, designator type, declared length, ambiguous alternate
identities, and canonical/payload mismatch remain rejected. Existing port/target
association and malformed-descriptor rejection tests remain passing.

## Independent validation

- Relevant identity, discovery, and base probe suites: **175 passed** (including
  **114** identity tests).
- Fixture schema, diagnostics, and export suites: **126 passed, 5 skipped**;
  these environment-dependent skips are not claimed as executed coverage.
- Final combined rerun of all six relevant suites: **301 passed, 5 skipped**.
- Full changed-content validation chain: **PASS**.
- Codex skill parity: **PASS** (5 paired, 7 Codex-only).
- Path-reference audit: **PASS**, six existing standing-exception warnings.
- `git diff --check`: **PASS**.

The existing private evidence and independently supplied private storage
reference were replayed locally with owner/mode/path checks; no raw identifiers
or descriptor bytes were printed or copied. One host yielded exact
backing-UUID and canonical/reference matches, one distinct validated LU
designator, and valid capacity/descriptive values. Result:
**CONDITIONALLY QUALIFIED** for the captured single-host lab observation.

This does not establish cross-host equivalence, cross-vCenter equivalence,
temporal stability, global collision freedom, or any deployed CanonicalLun
behavior. No new live query is required to diagnose or replay the saved
single-host evidence. Further host/time observations remain separately
authorized evidence-gathering work, not prerequisites invented by this fix.

Authority: the [independent rejection diagnosis](rdm-lun-identity-e34-rejection-investigation.md)
and [identity evidence map](../../api-maps/vsphere-canonical-lun-identity.md).
No live queries, credential access, builds, application fixes by the reviewer,
commits, or pushes were performed.
