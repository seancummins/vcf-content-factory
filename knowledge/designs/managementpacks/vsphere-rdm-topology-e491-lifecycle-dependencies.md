# E4.9.1 — SDK fixture lifecycle dependency qualification

## Latest disposition: PASS for bounded offline fixture lifecycle

The supplied genuine trust-manager dependency clears the original blocker.
The extended actual-SDK lifecycle harness passes **460 assertions** across four
fixture/mode scenarios and both original/dispatcher routes; diagnostic isolation
passes **317 assertions**. See the follow-up results below. This is offline
qualification, not live upgrade or collector qualification. Historical blocked
results are retained below to show the evidence sequence.

## Original dependency investigation

The E4.9 dispatcher remained independently approved offline; the original
dependency investigation did **not** qualify its complete fixture SDK lifecycle. No appliance connection,
adapter source change, PAK build, installation, commit or publication occurred.
Existing build-9 and build-10 artifact checksums remain unchanged.

## Verified dependency evidence

Local inspection found only the authorized SDK and seven descriptor libraries
in the supplied SDK directory. All seven libraries pass their operator-supplied
`SHA256SUMS` manifest. None supplies either missing secure-connection class.
The SDK is a local-only proprietary artifact, not redistributable/reproducible
from factory Git; bytecode findings are summarized here in full. SDK SHA-256:
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.

`javap -c -p` establishes this construction chain:

`RdmTopologyPocAdapter → VcfCfAdapter → AdapterBase → CustomTrustManager`.

`CustomTrustManager`'s constructor immediately invokes:

1. `ConnectionCategory.ADAPTER_TO_SOURCE`.
2. `SSLOptions.getSSLOptions(ConnectionCategory)`.
3. `SSLOptions.getStoreType()`, then JDK `KeyStore.getInstance(...)`.

Both classes belong to `com.vmware.vrops.secure.connection`. These are verified
direct dependencies, not a complete transitive closure. The SDK embedded POM
declares `com.vrops.certificate-validation:vrops-trustmanager:3.0-SNAPSHOT`.
The cleanroom classpath inventory identifies the package with the
`vrops-trustmanager-*.jar` family
([classpath contract](../../context/cleanroom-spec/spec/13-classloading-and-classpath.md)).
Neither establishes the exact installed filename, checksum or runtime dependency
versions. Those require inspection of the matching development appliance.

Separately, `CertificateChecker.getCertificate(String)` invokes
`javax.xml.bind.DatatypeConverter.parseHexBinary(...)`. The embedded POM declares
`javax.xml.bind:jaxb-api:2.3.1`. This class is absent locally and not provided by
modern JDKs. It is a verified certificate-processing branch dependency, **not**
the current constructor failure or proof that the no-certificate fixture path
requires JAXB. Do not preemptively copy all SDK POM dependencies or substitute
public Maven libraries. Further dependencies of `SSLOptions`, including any
provider/configuration requirements, remain unknown until its real JAR is read.

## Operator: read-only appliance inventory

Run on the authorized development appliance. This only reads installed JARs;
it prints matching paths/classes and SHA-256, not configuration or credentials.
It does not load Java classes, extract files or change the runtime. Python is
an administrative inspection utility here, not a deployed adapter dependency.
Unreadable/corrupt archives abort rather than imply complete discovery.

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib
import os
import zipfile

root = Path('/usr/lib/vmware-vcops')
if not root.is_dir():
    raise SystemExit('Expected Operations library root absent; locate it explicitly.')
wanted = {
    'com/vmware/vrops/secure/connection/ConnectionCategory.class',
    'com/vmware/vrops/secure/connection/SSLOptions.class',
    'javax/xml/bind/DatatypeConverter.class',
}
found = set()
def fail(error):
    raise error
for directory, _, files in os.walk(root, onerror=fail):
    for filename in sorted(files):
        if not filename.endswith('.jar'):
            continue
        path = Path(directory) / filename
        with zipfile.ZipFile(path) as jar:
            matches = wanted.intersection(jar.namelist())
        if matches:
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1048576), b''):
                    digest.update(chunk)
            print(digest.hexdigest(), str(path))
            print('  classes=' + ','.join(sorted(matches)))
            found.update(matches)
missing = wanted - found
if missing:
    print('NOT_FOUND_IN_SCANNED_TREE=' + ','.join(sorted(missing)))
    raise SystemExit(2)
PY
```

The command uses only the Python 3 standard library. Symlinked JAR files are
read; directory symlinks are not traversed.
An unresolved class or symlink-only library directory requires an explicitly
identified additional library root, not a categorical platform-absence claim.

Have the administrator copy only the matching, legitimately available libraries
to the existing external local directory
`/home/scummins/Documents/vmware-sdk/descriptor-libs/`, preserving filenames.
Record appliance version/build, original paths and source hashes; independently
verify destination SHA-256 and JAR contents before adding explicit paths to the
local test classpath. Keep the source hash record separate from newly computed
destination hashes. Never place platform JARs in adapter `lib/`, Git or a PAK.

## Actual offline results and qualification boundary

`run-dispatcher-tests.sh --fixture-lifecycle` with the genuine seven-library
classpath reports:

- Dispatcher: **PASS, 317 assertions**, including diagnostic empty SDK payloads,
  repeated calls, invalid configuration and lifecycle interleavings.
- Fixture readiness: **BLOCKED, exit 2**, missing
  `com.vmware.vrops.secure.connection.ConnectionCategory`.

Importantly, the original `FixtureLifecycleProbe` constructed the original fixture
adapter, calls `configure` and `discard`; it does **not** exercise a complete
fixture collection through the dispatcher. A future `CONFIGURE_PASS` alone is
insufficient. Once genuine dependencies are supplied, qualify default/explicit
fixture dispatch using actual SDK construction, configuration, discovery,
repeated collection, stop/discard and synthetic build-9 fixtures. Assert stable
keys, additive relationships and expected output against the unchanged fixture
implementation. Include the full positive/negative fixture matrices without
logging shims, constructor bypass or a synthetic publishing delegate. If actual
SDK initialization requires more platform services/configuration, name that
additional blocker; do not simulate it as a completed qualification.

Diagnostic no-publication regression evidence remains valid but does not prove
live credential injection, upgrade compatibility or collector behavior. No
additional platform dependency is bundled to make a test pass.

Changed-content and complete content validation, Codex skill parity and both
repositories' whitespace checks pass. The path-reference audit is clear with
only its existing RULE-015 standing-exception warnings. Nothing is staged.

Independent review: [E4.9.1 SDK review](../../context/reviews/rdm-topology-e491-sdk-review.md).
At that checkpoint complete lifecycle approval remained **BLOCKED** pending the provider JAR,
provenance, immediate dependency inspection and genuine lifecycle re-execution.

## Follow-up: authorized trust-manager supplied

The operator supplied `vrops-trustmanager-3.0-SNAPSHOT.jar` from the development
appliance's `/usr/lib/vmware-vcops/common/lib/` into the external SDK dependency
directory. Its SHA-256 matches the updated appliance-hash manifest:
`64f915e64bbee1a69b75dcc8b4eef6038da3993c0b1c1cc212f2c047ac502e37`.
All eight dependency manifest checks pass. Origin/build matching remains
operator-attested; no connection to the appliance was made for this check.
ZIP class inspection confirms both exact entries:

- `com/vmware/vrops/secure/connection/ConnectionCategory.class`
- `com/vmware/vrops/secure/connection/SSLOptions.class`

The genuine eight-library classpath passes the dependency checker and combined
actual SDK descriptor load (3 resource kinds, 1 credential kind). Initial rerun
passes all 317 dispatcher assertions and the original readiness probe now
reports `FIXTURE_LIFECYCLE code=CONFIGURE_PASS`, exit 0. This clears the original
constructor/configure/discard dependency blocker; it does not alone prove the
full fixture lifecycle. The following evidence supersedes the original blocked
dependency result rather than retroactively changing that historical outcome.

### Static dependency branches, not observed runtime failures

`jdeps --multi-release 17 --ignore-missing-deps -verbose:class`, with the actual
SDK/eight-library classpath, identifies these unresolved trust-manager branch
references:

| Exact classes | Likely matching-appliance provider / evidence |
|---|---|
| `com.vmware.vcops.security.Crypt`, `com.vmware.vcops.security.CryptUtils` | `vcops-security` JAR; trust-manager POM declares `com.vmware.vcops:vcops-security:1.0-SNAPSHOT` |
| `io.jsonwebtoken.Claims`, `Header`, `Jws`, `JwsHeader`, `JwtException`, `JwtParser`, `JwtParserBuilder`, `Jwts`, `Locator`, `JweHeader`, `LocatorAdapter`, `io.jsonwebtoken.security.SignatureException` | `jjwt-api` JAR; POM declares 0.12.6, plus `jjwt-impl`/`jjwt-jackson` runtime dependencies, also 0.12.6 |

The security classes are referenced by `SSLOptions`' password-processing
branches; JWT references occur in `ndc.NdcCertificateRefresher`, not the tested
fixture constructor path. The separate SDK JAXB reference noted above remains
a certificate-processing branch requirement. None was an observed missing-class
failure in the successful eight-library readiness run. Exact appliance provider
filenames/checksums and their further dependencies remain unqualified. Do not
copy them preemptively, treat static reachability as an executed failure, or
load every appliance library indiscriminately. Preserve the no-certificate,
no-decryption fixture test boundary and qualify other branches separately.

### Completed actual-SDK lifecycle follow-up

Only the test helper `tests/com/vcfcf/adapters/rdmtopologypoc/FixtureLifecycleProbe.java`
changed in the independent adapter repository. No production source, descriptor,
build number, script or PAK was changed. The existing runner compiles against
the actual SDK, factory base and eight explicit external platform JARs, excluding
test logging shims. There is no constructor bypass, synthetic publishing
delegate or replacement platform class in this lifecycle run.

`run-dispatcher-tests.sh --fixture-lifecycle` now reports **exit 0**:

```text
DispatcherTest: PASS 317 assertions (delegate seam, actual SDK carriers/payloads)
FIXTURE_LIFECYCLE code=PASS assertions=460 scenarios=4 routes=2
```

The 460 assertions exercise legacy mapping-only and version-2 CanonicalLun
synthetic fixtures, each with absent/default mode and explicit `fixture` mode.
Each case runs against both the unchanged original adapter and the real public
dispatcher: constructor, configure, discovery, first collection, repeated
collection, same-config refresh and third collection, stop and discard.
Assertions compare stable resource keys, the complete foreign VM identifiers
and uniqueness flags, exact additive edges/no clearing, and matching topology
output across routes. Dispatcher collection/discovery after stop and collection
after discard are empty.

The fixture harness uses supported `AttributeConfigs`/`AttributePolicyConfigs`
carriers to model monitored property policy: configuring resource attributes
alone does not cause actual `AdapterCache.shouldCollect` to accept samples.
The first CanonicalLun collection must emit all seven expected property values,
including synthetic capacity 524288 bytes. Subsequent collections and same-config
refresh may legitimately omit unchanged property deltas: the actual SDK
`AdapterCache.updatePropertyChanges` retains unchanged-value knowledge (900000 ms
resend window). Any nonempty property set must equal the complete expected set;
the test does not accept partial or changed values to force parity. Topology
keys and additive edges remain stable every collection. This is SDK property
delta behavior, not a production correction.

The 317 dispatcher assertions separately reconfirm empty diagnostic publication
payloads on success, repeat, invalid configuration, cancellation and lifecycle
interleavings. Actual descriptor loading passes with 3 resource kinds and
1 credential kind. SDK validation passes for 22 production sources, with
existing source/target and deprecation warnings. Dependency-checker regression
tests pass (15 tests, 4 subtests). Content validation, skill parity, path audit
and whitespace checks pass; the path audit retains only its existing standing
exceptions.

No additional missing class was observed on these exercised fixture/diagnostic
paths. Static security/JWT/JAXB branches listed above are not thereby qualified.
This bounded positive lifecycle matrix is not a rerun of every historical
negative parser test, nor evidence of real credential decryption, certificate
delivery, SDK deployment classloader behavior, UI compatibility, collector
failover, shared-kind upgrade safety or live topology persistence under build 10.

Production-source/descriptor/build-metadata and both PAK hashes match the
pre-test snapshot. Build 9 remains
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`;
build 10 remains
`df136333f9ea8ec4ad24b3da6cff489fa4825d49cc02854003327fa909b6314a`.
No installed adapter was contacted or changed. No commit, push or release.

The independent SDK reviewer reproduced the final **317 + 460** assertion
results using the genuine eight-library classpath: **APPROVE, zero outstanding
findings**, for this bounded offline lifecycle qualification only. See the
[final review](../../context/reviews/rdm-topology-e491-sdk-review.md). The original
`ConnectionCategory` blocker is resolved; no additional platform library is
currently required to repeat these tested no-certificate/no-decryption paths.
