# E4.2 — Independent native Java SDK/security review

**Verdict: APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT**, for the inert,
offline-tested discovery foundation only. This does not authorize collection
activation, live queries, packaging, installation or topology publication.

## Scope and authority

Independently inspected the five new Java classes under the managed adapter's
`src/com/vcfcf/adapters/rdmtopologypoc/discovery/`, its synthetic
`DiscoveryFoundationTest`, test script and native-discovery documentation.
The adapter remains an independent repository; older dirty POC changes were not
attributed to E4.2. No implementation was changed by this reviewer.

Authority: [approved E4.1 architecture](../../designs/managementpacks/vsphere-rdm-topology-e41-automatic-discovery.md),
[API map](../api-maps/vsphere-rdm-automatic-discovery.md),
[reviewer doctrine](../authoring/guide_reviewer_doctrine.md),
RULE-008 (`knowledge/rules/no-secrets-on-disk.md`) and the Tier 2 skill's
classloader, stitching-identity, bulk-read and gap-honesty contracts.

## Independently verified

- `bash content/sdk-adapters/rdm-topology-poc/scripts/run-discovery-tests.sh`:
  **PASS, 55 deterministic cases, exit 0**, including actual loopback HTTPS.
  The sandbox initially prohibited local socket creation; the rerun used explicit
  escalation for synthetic localhost tests only. No VMware endpoint was contacted.
- Compilation uses `javac --release 11 -proc:none`. Production discovery classes
  resolve only JDK `java.base` and `java.xml`; `jdk.httpserver` belongs to tests.
  `jdeps -s` completed successfully. No runtime Python, subprocess, third-party
  provider, download or collector-local file dependency was found.
- `VCFCF_SDK_JAR=<locally supplied SDK> PYTHONPATH=src .venv/bin/python -m
  vcfcf_managementpacks validate-sdk content/sdk-adapters/rdm-topology-poc`:
  **PASS**, eleven source files compiled. The factory compiler's existing
  `-source/-target 11` warning is not proof of Java-11 API compatibility; the
  separate strict `--release 11` discovery tests provide that compile check.
- No new PAK was built, so no new artifact checksum or comparison pass is claimed.
  The existing development artifact is not evidence of deployed discovery behavior.

## Security and correctness assessment

| Boundary | Evidence checked |
|---|---|
| TLS and credential routing | Fixed HTTPS `/sdk` endpoint; userinfo, query and fragment rejected; redirects disabled. Per-connection context, explicitly supplied in-memory trust and dialed-host SAN verification before writing SOAP credentials. Actual CA-signed localhost success, wrong-name rejection and untrusted-chain rejection passed. No accept-all manager or process-global TLS modification. |
| Deadlines and cancellation | Bounded connect/read/request/response budgets, cycle budget and separately bounded cleanup; active-request watchdog disconnects on deadline/interruption and is retired in `finally`. Actual TLS slow-drip response was rejected within the regression bound; fake-clock exhaustion and interrupt preservation/cleanup passed. |
| XML | Streaming byte/depth/node/attribute/namespace/text bounds precede hardened DOM; DTDs, external entities, external schema access and XInclude disabled. SOAP envelope/body/header cardinality, direct vim25 namespaces and typed fields checked. XXE/DTD, oversized, deep, unexpected-operation and namespace/QName cases reject with sanitized errors. |
| Sessions and query state | Login cookie is retained before parsing for failure cleanup; cookie syntax bounded. Continuation tokens are retained before object decoding; malformed/faulted pages cancel pending queries. Views are destroyed and logout attempted without replacing the primary failure. No automatic authentication retry or foreign credential reuse is implemented. |
| Identity and completeness | Scoped vCenter UUID + VM MOID resolver preserves full ordered keys and actual uniqueness flags, including supported empty nonunique strings. Duplicate/ambiguous/incomplete identities reject. Exact current-host backing UUID join and typed LU-associated NAA validation precede a LUN edge in memory. Missing inventory and unstable VM observations cannot become a complete zero-result finding. |
| Redaction and publication | Standalone fixed-code exceptions carry neither remote response text nor unsafe causes/suppressed exceptions; object `toString()` methods redact inventory. The foundation contains no SDK resource/relationship publication calls, and existing adapter entrypoint does not invoke it. |

During review the author corrected cleanup starvation after cycle exhaustion,
lost continuation/login state on parse failure, missing interruption handling,
scalar namespace checking and the unsupported `jdeps --summary` option. These
were independently rechecked; they are not outstanding findings. The decoder's
repeated signed-decimal SOAP byte elements agree with the locally verified
pyVmomi serializer evidence, rather than an assumed base64 representation.

## Limits and next boundary

Approval is not a claim that a real vCenter response, Operations collector TLS
provider, enterprise trust workflow, injected Suite API identity or Cloud Proxy
route has been exercised. Runtime credential/configuration injection, concrete
strict read-only Operations transport/RBAC, cluster-managed trust propagation,
supported collector/JDK/provider qualification, publication and durable ownership
remain separate integration work. Automatic LU evidence is explicitly intrinsic
vSphere evidence, not independently storage-array-corroborated identity; global
deduplication remains unproven.

Registry check: `knowledge/context/defects.md` was inspected; **no open entry
affects this RDM adapter**. No closure or new registry entry is proposed.

**If shipped as-is:** the existing fixture-driven adapter remains unchanged;
the new discovery foundation is inert and cannot automatically publish topology.
