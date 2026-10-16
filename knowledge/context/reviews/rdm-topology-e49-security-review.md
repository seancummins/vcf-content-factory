# E4.9 — Same-kind dispatcher security review

## Verdict

**APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT outstanding.** This is offline
implementation/package approval, not authorization to install or execute.
If shipped as-is, the same kind defaults to its existing fixture route; only
explicit, complete diagnostic configuration can execute the read-only engine.
A shared-kind upgrade and real platform credential/trust delivery still need
the separately authorized qualification described in the
[E4.9 record](../../designs/managementpacks/vsphere-rdm-topology-e49-same-kind-dispatcher.md).

## Independent verification

Reviewed the complete dispatcher, owner-specific diagnostic binding changes,
combined descriptor, lifecycle tests and operator instructions in the independent
`content/sdk-adapters/rdm-topology-poc` repository. The review followed
`.claude/agents/sdk-adapter-reviewer.md`, the shared reviewer doctrine,
`vcfops-sdk-adapter` (failure granularity, stitching identity, logging, resource
hygiene and named gaps), RULE-005, RULE-007 and RULE-008.

- Independently reran `scripts/run-dispatcher-tests.sh` with the authorized SDK
  and all seven genuine external platform libraries: **317 assertions PASS**,
  compilation with `--release 11`; actual SDK combined-descriptor loading and
  bare facade `describe()` included, without logging/platform shims.
- Independently reran the existing diagnostic suite: **243 coordinator**, **22
  SOAP wire**, and **19 localhost-only TLS/integration assertions PASS**.
  Sandbox initially prohibited the test server socket; the authorized rerun
  used synthetic local endpoints only, not VMware systems.
- Independently checked nested ZIP integrity and package registration: exactly
  one existing adapter kind, dispatcher entrypoint and three resource kinds.
  Only entry JAR and factory base JAR are included. Neither contains proprietary
  SDK, Log4j or Commons classes, test classes or test probe payloads.
- Independently verified development build 10 SHA-256:
  `df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`.
  Build 9 remains
  `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
- Adapter `git diff --check` passed. No live API calls, installation, build,
  repository operation or credential retrieval was performed by this reviewer.

The candidate and proprietary dependencies are local-only, not reproducible
from factory Git or redistributed here; the relevant findings are summarized
in full above. Package filename: `vcfcf_sdk_rdm_topology_poc.0.0.0.10.pak`.

## Safety conclusions

The direct `AdapterInterface3` facade does not extend the publishing SDK base.
Diagnostic dispatch never constructs the fixture delegate and returns empty
real SDK collect/discovery payloads on success, failure, cancellation, disabled,
repeated and unconfigured paths. Fixed adapter status/counts are distinct from
resource metrics/properties. The actual engine's source inventory reads do not
become platform discovery output.

Absent mode selects a fully validated legacy fixture, not a fallback from a
diagnostic error. Explicit blank/unknown/duplicate/mixed settings fail closed.
Mode and instance identity are latched. Reconfiguration retires invalid routes;
fixture callbacks are serialized and stamped before and after dispatch so a
retired configuration cannot return stale publication payloads. At review
request, the author added a deterministic regression returning nonempty SDK
payloads after an in-callback configuration mutation; both collect and discover
correctly discard those results. This coverage request is resolved.

Unsaved validation is configuration-only: no configuration replacement, secret
decryption, API call or one-shot consumption. Diagnostic cancellation and
reconfiguration retain the existing generation fence and object-local one-shot
limit, with no new worker while an old worker retires. Restart/failover is not a
durable authorization ledger; instructions explicitly disarm before either.

Associated vCenter credentials and injected Operations identity retain separate
SDK carriers. No fallback to another integration, local file, environment secret
or guessed endpoint was added. Existing strict private-JVM/enterprise-CA chain
validation, independent hostname checks, direct no-proxy sockets, response/XML
limits and redaction remain intact. The synthetic TLS suite verifies chain/name
rejection, approved CA handling and resistance to permissive global TLS and
proxy/auth/cookie handlers.

## Explicit qualification limits

Seven descriptor libraries do not supply the complete platform runtime.
Unchanged fixture construction needs
`com.vmware.vrops.secure.connection.ConnectionCategory`; full shim-free fixture
lifecycle through the facade is therefore **BLOCKED offline**, not represented
as proven by delegate-seam tests or historical build-9 evidence. No dependency
was substituted or bundled to conceal the gap.

Actual UI serialization of optional fields/credentials, injected secret
decryption/RBAC, managed CA delivery, collector routing, lifecycle acceptance
and same-kind upgrade behavior remain unverified. Both transports use the same
instance CA collection with separate contexts, as documented. No insecure lab
default is offered. Stop/disarm only the dedicated diagnostic instance; do not
uninstall the shared pack or delete VMware/POC topology or shared credentials.

Registry check (`knowledge/context/defects.md`): **no open defect names this RDM
adapter**. No defect closure or finding suppression is proposed.
