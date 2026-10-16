# E4.7 — Independent diagnostic packaging security review

**APPROVE the offline design and NO-GO packaging disposition: 0 BLOCKING /
0 WARNING / 0 NIT outstanding in the proposal.** This is not approval of an
implemented same-kind dispatcher, an installation candidate or live execution.

## Scope and authority

Independently reviewed the [E4.7 packaging decision](../../designs/managementpacks/vsphere-rdm-topology-e47-diagnostic-packaging.md),
existing E4.6 diagnostic lifecycle/coordinator, active fixture entrypoint and
descriptor, SDK bindings, and candidate descriptor. Read-only adapter review;
only this report was authored. No source, package, credentials or live VMware
environment was changed or accessed.

Authority: `.claude/agents/sdk-adapter-reviewer.md`, the
[reviewer doctrine](../authoring/guide_reviewer_doctrine.md), RULE-001
source-of-truth, RULE-005 validation, RULE-008 secret protection, RULE-012
defect registry, and the Tier 2 skill's resource-hygiene, scoped-identity and
gap-honesty requirements. SDK public signatures and actual supplied SDK
bytecode, not a guessed platform limitation, support the lifecycle conclusion.

## Findings and disposition

- **Prefer the existing kind, but not a callback-only flag.** The active
  `RdmTopologyPocAdapter` extends the factory base and SDK `AdapterBase`.
  Actual `collect()` is final; its base lifecycle emits data outside the
  callback, including system properties, adapter metrics and certificate-event
  paths. An empty diagnostic `onCollect()` cannot meet the zero-output contract.
  `AdapterInterface3` permits a direct dispatcher in principle; this is not
  evidence that existing-kind execution is unsupported. Reusing the E4.6
  coordinator behind a thin direct-interface facade is a proportionate next
  implementation, not duplicating discovery/authentication machinery.
- **A same-kind upgrade is shared, not isolated installation.** Changing the
  entrypoint/descriptor replaces code and metadata for every instance of that
  kind. The proposal correctly requires preserving the fixture delegate and
  identity contracts, missing-mode compatibility, conditional credential/config
  validation, no fallback after diagnostic errors, latched mode and serialized
  retirement. These are unimplemented prerequisites, not demonstrated safety.
  Diagnostic callbacks must never construct/call the fixture base delegate.
- **No publication is not no read-only enumeration.** E4.6 deliberately reads
  bounded caller-visible Operations VM pages and scoped vCenter inventory.
  Those source reads are necessary; SDK discovery/resource/metric/property/
  event/relationship publication is forbidden on the diagnostic route. Current
  E4.6 tests establish empty SDK results for its distinct, unregistered carrier,
  not for a future same-kind dispatcher. No second kind is implemented or
  approved by this review.
- **Credential and trust limitations are explicit.** Associated vCenter
  credentials and the injected per-instance Operations identity remain separate
  SDK carriers; no other integration, fallback file or assumed administrator
  account is permitted. Actual decryption, token acceptance, RBAC and placement
  routing need authorized runtime evidence. Ordinary endpoint/trust selectors
  do not supply CA bytes. Actual instance-managed CA material, or pre-existing
  approved JVM roots on each collector, is necessary; opaque IDs, leaf-only
  trust and disabled verification remain rejected. No collector-local file
  synchronization or TLS-insecure lab shortcut is proposed.
- **Cleanup must not uninstall the shared pack.** Stopping/disarming the exact
  new diagnostic instance is the conservative first action. Shared-kind
  uninstall or kind-wide credential deletion could remove the working POC and
  cascade credential loss, as documented in
  [the credential-cascade lesson](../../lessons/pak-uninstall-cascades-credentials.md).
  Instance/credential removal requires exact ownership and reference checks;
  no VMware, mapping or LUN deletion is prescribed. Retaining build 9 is not
  proof of safe downgrade; recovery must be separately authorized and tested.
- **Loader/package honesty.** An SDK-only test that accepts a sanitized loader
  exception is not actual descriptor-loading validation. The documented clean
  loader attempt remains blocked by missing local platform linkage. No fake
  platform class, downloaded dependency, bundled proprietary SDK or fabricated
  successful load is acceptable. No E4.7 PAK exists, so no checksum or structural
  comparison pass is claimed for one.
- **Standalone loader probe hardening.** Independently inspected
  `DescriptorLoadingProbe.java` and `check-sdk-descriptor-load.sh`. Secure
  preflight alone protects only its first XML parser, not the SDK's second
  parse; this review requested a correction. The final child JVM sets and
  verifies empty JAXP external-DTD/schema/stylesheet access before SDK use,
  retains DOCTYPE/entity rejection, bounds input, suppresses parser/SDK output
  and reports static categories. Security-property failure is blocked, not
  ignored. The settings affect this standalone utility, never the collector.
  Supplied extra platform classpath must be legitimate and trusted; no logging
  shim or automatic dependency discovery is included. The resolved hardening
  request is not an outstanding finding.

## Independent offline verification

| Check | Actual result |
|---|---|
| Diagnostic coordinator/SDK empty-result/composition runner | PASS, 243 assertions |
| Isolated SOAP wire runner | PASS, 22 assertions |
| Synthetic localhost TLS/integration runner | PASS, 19 assertions |
| `validate-sdk` | PASS, 21 production sources compiled |
| Actual SDK loader, active and historical candidate descriptors | Both exit 2, `BLOCKED_PLATFORM_DEPENDENCY`, first missing `org.apache.logging.log4j.LogManager` |
| Loader shell argument guard | Exit 1, static `INVALID_ARGUMENTS` |
| Diagnostic dependency analysis | JDK, supplied SDK and project classes only |
| Adapter whitespace check | PASS |
| Existing build-9 PAK SHA-256 | `9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb` |

The first TLS run was denied socket creation by the sandbox. The explicitly
approved retry used ephemeral synthetic localhost servers only; no VMware
endpoint or real credential was used. Runners compile with `--release 11`;
`validate-sdk` retains its existing source/target-11 warning and deprecated SDK
API note. These reruns validate existing E4.6 implementation only, not the
unimplemented dispatcher, conditional union descriptor, collector acceptance or
UI persistence. No build/comparison was run to manufacture an install candidate.
The clean loader excludes E4.6 test logging classes: its Log4j failure precedes
the later Commons Configuration failure seen on that earlier test classpath.
Neither is successful descriptor loading; missing dependencies may be discovered
incrementally. No unrestricted parse or network request was needed to establish
the present dependency blocker.

Registry check: `knowledge/context/defects.md` inspected; **no open defect
affects the RDM adapter**. No closure or surviving new defect registration is
proposed: the package and runtime prerequisites remain explicitly unaccepted.

**If shipped as-is:** the registered build-9 fixture route remains unchanged;
there is no existing-kind diagnostic PAK ready to install. Proceed with the
small same-kind dispatcher/descriptor implementation and actual loader
qualification first. Installation and one read-only experiment still require
separate operator authorization.
