# E4.5 — Independent native Operations identity-provider SDK review

**APPROVE — 0 BLOCKING / 0 WARNING / 0 NIT**, for the dormant offline
implementation only. This is not approval of runtime authentication, collector
activation, installation, migration or topology publication.

## Scope and independent evidence

Reviewed all five new adapter `ops/` production classes, the complete synthetic
`OperationsProviderTest`, standalone runner and adapter-local
`docs/operations-identity-provider.md`, plus the
[implementation record](../../designs/managementpacks/vsphere-rdm-topology-e45-operations-provider.md).
The independent adapter repository remains separate from the factory. No active
entrypoint, descriptor, fixture contract or existing relationship code is changed
by this increment. This reviewer edited only this report.

Authority: SDK reviewer contract and shared reviewer doctrine; RULE-001,
RULE-005, RULE-007, RULE-008 and RULE-012; Tier 2 skill sections on scoped foreign
identity, actual uniqueness flags, classloader isolation and gap honesty;
[E4.4 qualification](../../designs/managementpacks/vsphere-rdm-topology-e44-runtime-contract-qualification.md).
Inspected the public `reference/docs/operations-api.json` token/list/detail
schemas and actual authorized SDK signatures/bytecode. The proprietary SDK is
local-only and not reproducible from Git; no binary was copied or redistributed.
`AdapterCredentialConfig.getPassword()` invokes platform
`com.vmware.vcops.security.Crypt`, not a plaintext SDK field accessor.

## Correctness and boundary findings

- **Injected-only binding:** only the distinct SDK `AdapterConfig` injected
  credential is read. Missing values, changed association and decryption linkage
  fail closed. Synthetic readers are package-private tests, not another runtime
  identity source. Associated vCenter credentials, environment variables and
  maintenance files are not consulted. Owned secret arrays/request bytes are
  cleared; immutable JVM/SDK strings cannot be securely erased.
- **Public API contract:** acquire omits a guessed authentication source;
  resource GETs use `OpsToken`; token release is an authenticated bodyless POST,
  not inventory mutation. Acquired tokens are released even when later token
  metadata or collection validation fails. Cleanup has a separate finite budget
  and a sanitized diagnostic that does not replace the primary result.
- **Complete scoped identity:** one batch inventory scan follows bounded,
  zero-based pages with stable totals, expected page/size, duplicate detection
  and exact coverage. Both vCenter UUID and VM MOID must be unique-bearing and
  exact. Other-vCenter same-MOID and duplicate display-name candidates cannot
  redirect resolution. Missing/null values and malformed or absent flags reject;
  explicit empty nonunique strings survive. All identifiers, flags, ordering and
  display name survive the immutable key. Fresh detail must reproduce the full
  listing key before resolution succeeds. No approximate foreign key is built.
- **Strict isolated transport:** explicit FQDN, separate in-memory trust, chain
  validation and independent SAN verification precede all HTTP/authentication
  bytes. Native TLS sockets avoid global cookie/authenticator/proxy inheritance;
  no JVM-global production setting is modified. Fixed public paths, bounded
  framing/JSON/I/O, cancellation and sanitized errors contain remote inputs.
  The initial URLConnection ambient-handler concern was corrected before this
  verdict and independently tested; it was not waived.
- **HTTP subset is a deliberate limitation:** duplicate headers, chunk
  extensions/trailers, compression and informational responses reject even when
  otherwise legal HTTP. Content-length, basic chunked and EOF framing are tested,
  including ambiguous/truncated/oversized cases. This safe availability tradeoff
  is explicit in both documents; target Operations gateway interoperability is
  still unproven. No broad standards-compatibility claim is accepted here.
- **Dormancy and gap honesty:** the production factory returns
  `RUNTIME_UNQUALIFIED`; development construction itself performs no network
  access. No entrypoint references the provider. No resource/relationship write
  methods exist in it. Successful enumeration cannot prove global RBAC coverage,
  atomic inventory or absence outside caller-visible scope. Real injected
  decryption, permissions, collector/Cloud Proxy routing, managed CA delivery,
  failover and provider/FIPS behavior remain empirical prerequisites.

## Independently rerun validation

| Check | Observed result |
|---|---|
| Provider runner, no-network mode | **281 synthetic assertions passed**, exit 0 |
| Full provider runner | **345 synthetic assertions passed**, exit 0 |
| Existing runtime binder | **62 deterministic cases passed**, exit 0 |
| Existing discovery, no-network mode | **54 deterministic cases passed**, exit 0 |
| Existing actual-SDK topology/fixture/LUN runner | **8 topology tests, 42 invalid-runtime and 34 invalid-LUN cases plus positive matrices passed**, exit 0 |
| `validate-sdk` | **PASS**, 18 production sources; existing source-11 system-modules warning |
| Java compatibility/dependencies | Runner compiles with `--release 11`; production provider depends on JDK and provided Operations SDK/E4.2 classes only |
| Factory and adapter whitespace checks | PASS |

The full provider runner used ephemeral synthetic CA/server keys and localhost
TLS sockets only. Sandbox socket denial was retried with explicit execution
permission; no VMware endpoint, real credential, private fixture or inventory was
accessed. Tests demonstrate successful four-step acquire/list/detail/release,
TLS distrust/name rejection before authentication bytes, ignored global HTTP
handlers, bounded slow responses, complete-key freshness and redacted failures.
Assertions are not represented as 345 separate test methods or live proof.

Final frozen-source re-review confirmed the orchestrator's snapshot-null-input
finding is corrected with sanitized front-door identity validation, including
the graph resolver bridge. Header budgets count CR and LF, the name-mismatch
test proves EOF with no HTTP bytes, and the full TLS flow verifies the exact
synthetic authentication body. Response retention now validates every row but
retains only requested keys, with a 32 MiB aggregate response budget and 2 MiB
selected-key character budget. Deterministic limit tests fail closed and release
the token. These changes were independently reread and the final 345-assertion
suite and 18-source SDK validation rerun; no finding was deferred or waived.

No new PAK, build version or comparison is appropriate for this dormant source
increment; there is no new installation candidate. Existing active fixture
semantics remain the regression baseline. No proprietary SDK is packaged, no
non-platform dependency or runtime download is introduced, and no SDK API is
invented. The main orchestration record owns broader factory validation results.

Registry check: `knowledge/context/defects.md` inspected; **no open defect affects
the RDM topology POC**. No closure, exemption or new surviving defect is proposed.

**If shipped as-is:** installed build-9 fixture behavior remains unchanged.
Downstream developers gain an explicit, inert read-only provider candidate;
production activation still fails closed pending separately authorized in-process
contract qualification. The recommended E4.6 remains read-only composition and
runtime qualification, not topology publication.
