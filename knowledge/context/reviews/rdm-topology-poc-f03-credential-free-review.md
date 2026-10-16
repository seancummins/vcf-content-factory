# RDM topology POC F0.3 — credential-free metadata review

**Reviewer:** `sdk-adapter-reviewer` (independent Codex context)  
**Date:** 2026-10-14  
**Scope:** Offline review of the F0.3 descriptor correction, focused Java
tests, SDK validation, and the locally built development PAK. No source,
package, comparator, VMware system, or VCF Operations system was modified by
this reviewer.

## Verdict

**CHANGES REQUESTED — one focused regression assertion is incomplete.**

The implementation is otherwise the exact correction conditionally approved
by F0.2: the type-7 adapter-instance `ResourceKind` now explicitly declares
`isCredentialRequired="false"`; it retains no `credentialKind` attribute and
the descriptor has no `CredentialKinds` block. The embedded descriptor in the
new PAK has the same shape. No credential, endpoint, authentication code, or
foreign-parent relationship behavior was added or changed.

The new deterministic test checks that there are zero `CredentialKind`
*children*, no instance `credentialKind` attribute, and an explicit false
value. It does **not** assert that the `CredentialKinds` *container* is
absent. An invalid/undesired empty `<CredentialKinds/>` block would therefore
pass the regression test, despite F0.3 requiring all three credential-free
properties. Add an explicit namespace-aware assertion that
`getElementsByTagNameNS(..., "CredentialKinds")` has length zero, then rerun
the focused tests and SDK validation. This is a small test-only follow-up; do
not add credential metadata to address it.

## Evidence

| Check | Result |
|---|---|
| Authoritative `describe.xml` diff | Exactly one semantic metadata change on the type-7 instance: `isCredentialRequired="false"`. The accompanying build-number and generated-document changes are normal build-3 provenance updates. |
| Source descriptor | No `CredentialKinds` container, no `CredentialKind` entry, and no adapter-instance `credentialKind`; `isCredentialRequired="false"` is present on key `vcfcf_rdm_topology_poc`, type `7`. |
| Focused Java tests | Ran `VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar bash content/sdk-adapters/rdm-topology-poc/scripts/run-tests.sh`: **PASS (7 tests)**. The compiler emitted its existing Java 11 source/target warning only. |
| SDK validation | Ran `PYTHONPATH=src VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar python -m vcfcf_managementpacks validate-sdk content/sdk-adapters/rdm-topology-poc`: **PASS**. |
| PAK integrity and embedded metadata | `unzip -t` passed for `dist/vcfcf_sdk_rdm_topology_poc.0.0.0.3.pak`; its nested `adapters.zip` embeds the reviewed descriptor, with only `isCredentialRequired="false"` among credential-related tokens. No `vrops-adapters-sdk` JAR was present in the inspected archive layout. |
| Development artifact | `vcfcf_sdk_rdm_topology_poc.0.0.0.3.pak`; SHA-256 `2ef03219ee2f9c4da5d1f5bc7f13faa0dc34b10e53dacbbc097970c8c7554375`. This local `0.x` artifact is a development preview, not an approved release (RULE-014). |
| Diff hygiene | `git diff --check` passed in the independent adapter repository. |

## Required follow-up

Change only the regression test to assert absence of the `CredentialKinds`
container (in addition to the existing `CredentialKind` entry check), then
repeat the two commands above. A fresh independent review may approve if that
check passes and the correction remains otherwise unchanged.

## Comparison and deployment disposition

The approved F0.1 Synology comparison is **unchanged and not cleared**:
**2 BLOCKING, 3 WARNING, 20 INFO**. Its two BLOCKING findings remain the
Synology comparator's `CredentialKinds` and adapter-instance `credentialKind`
presence differences. F0.2 correctly concluded that those structural
differences do not authorize dummy credentials, and this review neither
suppresses nor reclassifies them.

Accordingly, F0.3 is **NO-GO** for deployment and release. Even after the
test-only follow-up, RULE-005 still requires a separately approved comparison
path with zero BLOCKING findings, along with the outstanding CI, release, and
authorized live-persistence gates.

## Build-4 addendum — final re-review

**Date:** 2026-10-14  
**Verdict:** **APPROVE** for the F0.3 credential-free metadata correction and
its focused regression coverage. This supersedes the narrow test-coverage
request above; it does not supersede the comparison or deployment gate.

The author made the requested test-only follow-up. The namespace-aware test
now asserts all four required properties of the authoritative descriptor:

1. no `CredentialKinds` container;
2. no `CredentialKind` entry;
3. no `credentialKind` on the type-7 adapter-instance resource kind; and
4. `isCredentialRequired="false"` on that same type-7 resource kind.

Independent re-run evidence:

| Check | Result |
|---|---|
| Focused Java test | `VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar bash content/sdk-adapters/rdm-topology-poc/scripts/run-tests.sh` — **PASS (7 tests)**. The existing Java 11 source/target warning remains non-failing. |
| SDK validation | `PYTHONPATH=src VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar python -m vcfcf_managementpacks validate-sdk content/sdk-adapters/rdm-topology-poc` — **PASS**. |
| Build-4 artifact | `vcfcf_sdk_rdm_topology_poc.0.0.0.4.pak`; SHA-256 `5354acc09b4afa5a2fad5aed9429adebd8fe0f0e751b0b64b909c59854381d61`. Outer ZIP integrity passed; independently extracted nested `adapters.zip` contains the corrected descriptor and no credential tokens other than `isCredentialRequired="false"`. No `vrops-adapters-sdk` JAR was present. |
| Diff hygiene | `git diff --check` passed. |

This remains a local `0.x` development artifact, not an approved release.
The approved F0.1 Synology comparison remains **2 BLOCKING, 3 WARNING, 20
INFO**, unchanged and **not cleared**. The resulting overall deployment and
release disposition remains **NO-GO** under RULE-005.
