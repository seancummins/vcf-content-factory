# E3.4.1 — pyVmomi integer compatibility correction

**Identity outcome: CONDITIONALLY QUALIFIED for the captured single-host lab
case.** No new live queries, adapter changes, PAK builds or deployment occurred.
This updates the offline BLOCKED status in the
[original E3.4 preparation record](vsphere-rdm-topology-e34-identity-qualification.md),
not its execution history or the scope of E2's topology proof.

## Minimal correction

The [approved investigation](../../context/reviews/framework/rdm-lun-identity-e34-rejection-investigation.md)
identified legitimate pyVmomi `byte` and `long` subclasses rejected by exact
`type(value) is int` checks. `scripts/rdm_lun_identity.py` now uses one helper:

```python
def _is_integer(value):
    return isinstance(value, int) and not isinstance(value, bool)
```

Only three checks use it: namespace ID, each descriptor byte, and capacity
dimensions. Namespace/byte bounds remain `-128..255`; capacity remains positive
with a signed-64-bit product ceiling. No string/float coercion, identifier
normalization, namespace interpretation, descriptor-header/type/association,
NAA format, equivalence or ambiguity policy changed. Timestamp validation is
unchanged; its source is a builtin integer, not an SDK scalar. No capture, adapter
or management-pack implementation was modified by E3.4.1.

## Sanitized offline replay

Read the existing private capture and independently supplied storage reference
directly from ignored owner-only local files, without changing or copying them.
These are local-only evidence, not reproducible repository artifacts; relevant
findings are summarized completely here without raw values.

| Criterion | Result |
|---|---|
| Observed hosts | One; cross-host equivalence not established |
| RDM backing UUID → observed ScsiLun.uuid | Exact equality |
| Distinct eligible LU identities | Exactly one |
| Descriptor proof | Two equivalent full NAA representations; supported LU-associated binary descriptor |
| Canonical name and independent storage reference | Exact complete payload agreement under the already-approved prefix/hex-case rules |
| Capacity dimensions | Valid, positive, within existing bounds |
| Descriptive data | Vendor, model, revision, display name, serial, LUN/device types, locality and capacity available; no values printed |
| Conflicts | No conflicting eligible identities or descriptive fields |
| Cross-vCenter / temporal stability | Not tested |

Saved JSON contains builtin integers because serialization loses SDK subclass
information. Direct replay therefore verifies the captured identity chain, not
by itself the runtime-type fix. New synthetic SOAP-deserialization tests cover
the actual SDK-object → capture helper → validator path **without** JSON
roundtripping. The live execution path was not rerun or claimed verified.

## Regression coverage and review

Added 39 deterministic cases using actual `VmomiSupport.byte`/`long`: positive
SDK/JSON parity, real SOAP decoding, booleans/strings/floats/null rejection,
signed/unsigned bounds, nonpositive/overflow capacity, and unchanged namespace,
association, encoding, designator type, length, ambiguity and equivalence rejection.
No real lab identifiers enter test fixtures or logs.

Results: **114 identity tests passed**; all six probe suites **301 passed / 5
skipped** (existing local SDK/output prerequisites). Full factory suite: **2,450
passed / 19 skipped / 131 deselected / 1 failed**, the previously reproduced,
unchanged `test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo` in
`tests/test_common_setup.py`. No unrelated fix was made. Full content and
changed-document validation, skill parity and diff checks pass. Path audit is
clear with six existing documented standing exceptions.

[Independent implementation review](../../context/reviews/framework/rdm-lun-identity-e341.md)
records the verdict and rerun evidence. Review approval concerns this correction,
not production readiness or live topology behavior.

## Remaining evidence and next implementation boundary

Actual descriptor representation, LU association and independent storage-reference
agreement are now established for this one saved observation. No further live
probe is needed to resolve the integer incompatibility or replay this sample.
The evidence supports proposing the next **minimal, fixture-driven lab**
CanonicalLun POC under separate implementation approval. Preserve the existing
VM → RdmMapping edge and E3.3's global token contract; add no production collector.

Before claiming multi-host/global deduplication, obtain separately authorized:

1. Another ESXi host observing the same already-presented LUN, with independently
   qualified descriptor payload equality; include a distinct-LUN negative control.
2. Repeated timestamped observations showing stable identity. Partial/unreadable
   or contradictory observations must remain unresolved, never silently merged.
3. Cross-vCenter observations where the same storage is already presented, before
   claiming empirical equivalence across the customer's vCenters. No new storage
   presentation/configuration is authorized to obtain that evidence.

Standards-based assignment still cannot rule out every cloned/misconfigured ID.
Keep collision quarantine and single-authority ownership. A future POC must
separately test two mappings converging on one owned key, stable repeated
collection, additive local relationship persistence, UI/API evidence and safe
cleanup. E2's foreign-VM-parent proof does not establish those local-edge outcomes.
