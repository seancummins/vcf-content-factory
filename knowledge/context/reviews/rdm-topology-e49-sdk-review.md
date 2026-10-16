# E4.9 — Independent SDK dispatcher review

## Scope and authority

Read-only review of the independent `rdm-topology-poc` repository's same-kind
dispatcher, union descriptor and development candidate. Authorities:
`.claude/agents/sdk-adapter-reviewer.md`, the Tier 2 SDK playbook,
`knowledge/context/authoring/guide_reviewer_doctrine.md`, RULE-005/007/008/012,
and the approved [E4.7 contract](../../designs/managementpacks/vsphere-rdm-topology-e47-diagnostic-packaging.md).
The defect registry was inspected: no open `Affects:` token targets this adapter.
No adapter code was edited by this reviewer; no live requests or installation.

## Source findings and resolved review requests

- Actual supplied SDK `AdapterInterface3` ABI supports the direct facade. Its
  public no-argument construction and bare `describe()` succeed without
  constructing the fixture's `AdapterBase`. Diagnostic collect/discover return
  empty actual SDK payloads, not a publishing base callback guarded by a flag.
- Default fixture selection forwards the **original** SDK configuration to the
  unchanged fixture delegate. Mapping/LUN identities, fixture parser and additive
  relationship implementation are retained. Diagnostic never constructs that
  delegate and never falls back to it on failure.
- Mode and SDK instance ID/UUID latch; invalid refresh, mutation, owner/mode
  switching, stop/discard and concurrent execution fail closed. Valid fresh
  same-owner carriers are covered. A review request to enforce selector presence
  and duplicate rejection in the public same-kind binding itself was fixed and
  independently rerun, rather than relying only on caller validation.
- The union descriptor has three existing kinds, one optional vCenter credential
  association and twelve nonunique optional settings without defaults. Missing
  mode selects fixture; explicit blank/null/unknown mode rejects. Actual UI
  serialization remains unproven, not silently treated as absence.
- Unsaved `test()` is configuration-only and deliberately rejects invalid
  fixtures unlike the old unconditional null-tester success. It does not arm,
  decrypt or connect. Fixture collection/discovery serialize through the facade;
  fixture stop waits for the finite callback instead of claiming preemption.
- Existing strict trust/credential contracts are reused, not relaxed. Managed
  enterprise-CA delivery, SDK secret decryption/injection, RBAC and collector or
  Cloud Proxy routing still require explicitly authorized runtime qualification.
  The per-object one-shot latch is not durable across restart/failover.

## Independently executed evidence

| Check | Actual result |
|---|---|
| Shim-free dispatcher runner, real SDK carriers/payloads, selector/owner/refresh/interleaving cases | PASS, 317 assertions |
| Actual SDK union descriptor and bare facade `describe()` | PASS within dispatcher runner; genuine seven-library classpath, no test shims |
| SDK validation | PASS, 22 production sources; existing source/target-11 and deprecation warnings |
| Existing diagnostic/runtime composition and isolated SOAP wire | PASS, 243 and 22 assertions |
| Existing fixture/topology | PASS, 8 topology/descriptor tests, 42 invalid-runtime cases, 34 invalid-LUN cases and positive matrices |
| Optional full fixture SDK lifecycle probe | BLOCKED, exit 2, missing `com.vmware.vrops.secure.connection.ConnectionCategory` |

The last missing class belongs to the unchanged SDK fixture-base construction
path. Seven descriptor libraries do not constitute the full collector runtime.
No replacement class, platform shim or dependency download was introduced.
Delegate-seam tests prove exact dispatch and output forwarding, **not** full
fixture SDK lifecycle execution. Older fixture tests retain their explicit
test-only logging/constructor-bypass limitations; these are not substituted for
the shim-free descriptor results. A same-kind upgrade remains untested.

The proprietary SDK and seven genuine platform JARs are external local-only
artifacts, not reproducible from Git or redistributed. Checksums/provenance are
fully summarized in the [E4.8 record](../../designs/managementpacks/vsphere-rdm-topology-e48-supplied-platform-libraries.md).

## Final package and disposition

Independently inspected local development candidate
`vcfcf_sdk_rdm_topology_poc.0.0.0.10.pak`, SHA-256
`df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`.
Outer/inner ZIP and both JAR integrity checks pass. Registration selects
`RdmTopologyDispatcher` under the original kind. There are only the entry JAR
and factory base JAR; no SDK, Log4j, Commons or platform secure-connection
classes are bundled. All nine existing RDM class files found in build 9 are
byte-identical in build 10; the new dormant components and dispatcher are
additions, not replacements of the fixture identity/relationship code.
The build-9 artifact remains SHA-256
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.

The standalone shim-free loader also passes, exit 0,
`resource_kinds=3 credential_kinds=1`. Real SDK-loaded metadata tests verify
the optional association and required username/password credential fields with
the password flag. Landing README, overview, installation and inventory docs
now distinguish default fixture publication from explicit read-only diagnostic
execution and link the mode/credential/trust procedure.

Independent structural comparison against the approved Synology v1.0.0.30
reference, SHA-256
`beaa8555ab3d8648fcb7dda6c26e2e4a295f0f2f854db467468060dd048480a1`,
passes exit 0 with **0 BLOCKING, 4 WARNING, 21 INFO**. Warnings are unchanged
policy findings, not suppressed: D3 credential-field count 2 versus 5; D8
instance-identifier count 12 versus 3; D23 traversal-spec count 0 versus 1;
D25 empty versus populated traversal specs. All 21 INFO findings are retained
in the comparison record. No unrelated adapter exception or policy change.

**Verdict: APPROVE the offline implementation and local development candidate;
zero outstanding review findings.** If shipped as-is, old valid fixture
configurations route to unchanged collection code; explicit diagnostic mode
uses the empty-output direct SDK path. However, same-kind upgrade/UI behavior,
full platform fixture lifecycle, managed CA delivery and actual injected
authentication/RBAC/routing are **not qualified** by these tests. Installation
is not authorized. Missing runtime evidence is a named prerequisite, not a
waived failure or production-readiness claim. Retain the E4.7 conservative
shared-kind recovery plan; do not uninstall the shared pack as diagnostic
cleanup. No live calls, commits, pushes or releases occurred.
