# E4.8 — Shim-free SDK descriptor dependency qualification

## Disposition

This is the initial E4.8 checkpoint. See the
[supplied-library continuation](vsphere-rdm-topology-e48-supplied-platform-libraries.md)
for the later local library inventory, transitive-dependency result and final
successful seven-library qualification of both exercised descriptors.

**BLOCKED: matching external platform libraries have not been supplied locally.**
The actual full SDK loader cannot yet complete. No replacement libraries were
downloaded, no appliance was contacted and no platform/SDK binary was copied,
committed, redistributed or bundled. This is not a descriptor rejection or a
successful qualification. The [E4.7 same-kind dispatcher design](vsphere-rdm-topology-e47-diagnostic-packaging.md)
remains the preferred next architecture; no runtime or registered metadata is
changed and no PAK is built.

## Source and compatibility evidence

Inspected the operator-supplied SDK using JAR inventory, embedded Maven metadata,
`javap` and `jdeps`. It is a **local-only proprietary artifact, not reproducible
from Git**; findings are summarized here without copying its contents. Existing
[E4.4 evidence](vsphere-rdm-topology-e44-runtime-contract-qualification.md)
records its authorized development-appliance provenance. Embedded build metadata
corroborates build 25137845; it is not an independently observed current appliance
filesystem or proof of the external dependencies installed there.

| Available artifact | Verified evidence |
|---|---|
| Supplied `vrops-adapters-sdk-2.2.jar` | SHA-256 `2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54` |
| Embedded Maven coordinates | `com.vmware.vcops:vrops-adapters-sdk:1.0`; the filename's `2.2` is not its Maven version |
| SDK `AdapterDescribe` class | Class-file major 61: this SDK requires Java 17+ at execution; compiling test/adapter code with `--release 11` does not make the SDK Java-11 compatible |

No external platform dependency is locally available with qualified provenance,
version and checksum. Those checksums therefore remain **unavailable**, not
inferred from version strings or fabricated. The supplied SDK directory and
bounded local dependency searches found no matching platform dependency set.
The operator also confirmed that only the SDK is known to have been copied.

## Dependency inventory: do not confuse scopes

| Library/classes | Evidence and status | Version evidence, not installation proof |
|---|---|---|
| Log4j API: `org.apache.logging.log4j.LogManager`, `Logger` | Actual clean loader first fails on `LogManager`; descriptor static initialization references these classes | Embedded SDK build property `log4j2.version=2.17.2` |
| Commons Configuration **1.x**: `org.apache.commons.configuration.ConfigurationException`, `PropertiesConfiguration` | SDK localization/descriptor-loading path references these; earlier shim-assisted tests reached this missing dependency. Configuration **2.x** does not supply these package names | Explicit SDK dependency `commons-configuration:commons-configuration:1.10` |
| Commons Lang **3**: `org.apache.commons.lang3.*` | SDK-wide direct references include `ResourceIdentifierConfig`, localization and string helpers; runtime closure still needs actual execution | Explicit SDK dependency `org.apache.commons:commons-lang3:3.14.0` |
| Commons Lang **2**, Commons Logging and Commons Collections | Potential transitive dependencies of the matching Commons Configuration stack, not a proven complete loader list | Exact matching JAR/POM versions and bytes must be supplied; SDK properties mention Logging 1.1 and Collections 3.2.2, but do not establish their necessity or actual appliance versions |
| Log4j Core | Full SDK logging infrastructure references Core; **not established as mandatory for this descriptor-only path** | Same build property is a clue, not a mandatory loader gate |
| Commons Codec, JAXB API, platform security/trust-manager libraries | Full SDK dependencies, **not all proven descriptor-loader requirements** | Explicit POM declarations: Codec 1.15, JAXB API 2.3.1, `vcops-security` 1.0-SNAPSHOT, `vrops-trustmanager` 3.0-SNAPSHOT |

The embedded Codec property says 1.4 while the explicit dependency says 1.15;
do not substitute the property for the declaration. Likewise Lang 2 and Lang 3
are not interchangeable. The whole-SDK `jdeps --missing-deps` list includes
unrelated credential, TLS and logging paths; demanding every such library would
overstate the minimum loader requirements. Conversely, resolving one missing
class or satisfying a class-presence inventory does not prove binary
compatibility or a complete dynamically exercised dependency closure.

## External validation classpath and operator handoff

Keep binaries outside tracked source and PAK inputs. The preferred source is
the **same authorized development appliance/build as the SDK**, obtained by the
operator through an approved file-transfer path. This increment performs no
remote retrieval. Do not copy another integration's entire `lib/`, SDK copies,
credentials, logging configuration or raw inventory.

Minimum handoff:

1. Identify the actual JAR owning each required class above in the approved
   platform library directory. Do not guess a filename or blindly substitute
   current Internet versions. Include the dependencies of those matching JARs
   as needed; the minimal closure may emerge over successive loader attempts.
2. Record source product/build, original relative library path, exact filename,
   manifest/Maven version, SHA-256 and transfer provenance. Hash at source and
   destination and require equality. File-copy access is not permission for
   configuration changes or VMware API probes.
3. Place the already authorized copies in a local directory outside both Git
   repositories, for example an operator-managed descriptor-library directory
   beside the supplied SDK. Supply its path without credentials. No automated
   dependency fetch, installation or redistribution is needed.
4. Set `VCFCF_SDK_JAR` to the supplied SDK and
   `VCFCF_DESCRIPTOR_CLASSPATH` to an **explicit colon-separated list of local
   dependency JAR files**. This is offline validator configuration, never
   deployed adapter configuration. No wildcard/directory/test-class/shim
   classpath is appropriate.
5. Run the dependency inventory and both actual loader checks described below.
   An inventory success is not provenance approval or full loader success.
   Resolve errors from actual returned categories; never mask them with stubs.

Use only an already compatible local JDK (Java 17+ for this SDK). Do not install
Java or libraries as a side effect of validation. Do not place these dependencies
in the adapter's `lib/`, runtime classpath, source tree or generated PAK.

### Read-only appliance command — operator execution only

Run on the authorized development appliance, **not executed by E4.8**. This
uses Python's standard library only and reads JARs in the platform common
library directory documented in the
[existing platform investigation](../../context/investigations/platform-edge-engine-2026-07-02.md).
It does not invoke
VMware APIs, retrieve credentials, initialize Java classes or write files.
If that directory or Python is absent, stop and report the location/runtime
gap; do not install tools or search credential directories.

```bash
python3 - <<'PY'
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
root = Path('/usr/lib/vmware-vcops/common/lib')
if not root.is_dir():
    raise SystemExit('Platform library directory unavailable')
classes = {
    'org/apache/logging/log4j/LogManager.class',
    'org/apache/commons/configuration/ConfigurationException.class',
    'org/apache/commons/lang3/StringUtils.class',
    'org/apache/commons/lang/StringUtils.class',
    'org/apache/commons/logging/LogFactory.class',
    'org/apache/commons/collections/CollectionUtils.class',
    'org/apache/logging/log4j/core/LoggerContext.class',
}
found = set()
for jar in sorted(root.glob('*.jar')):
    with ZipFile(jar) as archive:
        hits = sorted(classes.intersection(archive.namelist()))
    if hits:
        found.update(hits)
        print(str(jar), 'sha256=' + sha256(jar.read_bytes()).hexdigest())
        print('  classes=' + ','.join(hits))
for name in sorted(classes - found):
    print('NOT_FOUND_IN_COMMON_LIB', name)
PY
```

This deliberately discovers actual filenames by class ownership. Conventional
candidate names suggested by build metadata are `log4j-api-2.17.2.jar`,
`commons-configuration-1.10.jar` and `commons-lang3-3.14.0.jar`; **those filenames
have not been observed on the appliance** and are not instructions to download
them. Lang 2/Logging/Collections and optional Core filenames/versions must come
from the command's actual output. Multiple owners need review, not blind
classpath inclusion. `NOT_FOUND_IN_COMMON_LIB` is a directory-scoped result,
not proof that the appliance lacks a class. This candidate inventory is not a
claim all seven classes are mandatory for this descriptor path.

Recommended local destination for operator-transferred, authorized files:
`/home/scummins/Documents/vmware-sdk/descriptor-libs/`. It is outside both Git
repositories. Retain a local provenance manifest there and compare source and
destination SHA-256 values before use. No transfer command containing credentials
is requested or prescribed, and no directory or binary is created by E4.8.

## Checks and implementation record

Adapter-local changes only:

- New `scripts/check-descriptor-dependencies.py`: explicit local-JAR inventory,
  SHA-256/manifest versions, scoped class-presence diagnostics. It rejects hidden
  manifest classpaths, duplicate paths/classes, ambiguous ZIPs, directories,
  wildcards and empty classpath entries. No extraction or class initialization.
- Updated `scripts/check-sdk-descriptor-load.sh`: runs that inventory before the
  actual loader and rejects inherited Java option/classpath injection. Existing
  secure child-JVM XML restrictions remain unchanged.
- New `tests/test_descriptor_dependencies.py`: metadata-only synthetic JAR
  tests, never supplied to a JVM as loader substitutes.
- New `docs/descriptor-loader-dependencies.md`: standalone operator contract.

The inventory exits 0 when it successfully inspects a valid explicit classpath,
even if it reports missing classes. Its final code is `INVENTORY_ONLY` with
`platform_compatibility=UNVERIFIED`, **not PASS/readiness**. The loader still runs
and returns its own nonzero blocked result. The candidate scopes are not a
universal mandatory dependency list. Actual parsing/linkage remains decisive.

From the factory root, with the operator's legitimate explicit external
classpath set if available:

```bash
VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
  python3 content/sdk-adapters/rdm-topology-poc/scripts/check-descriptor-dependencies.py

VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
  bash content/sdk-adapters/rdm-topology-poc/scripts/check-sdk-descriptor-load.sh \
  content/sdk-adapters/rdm-topology-poc/describe.xml vcfcf_rdm_topology_poc

VCFCF_SDK_JAR=/home/scummins/Documents/vmware-sdk/vrops-adapters-sdk-2.2.jar \
  bash content/sdk-adapters/rdm-topology-poc/scripts/check-sdk-descriptor-load.sh \
  content/sdk-adapters/rdm-topology-poc/docs/diagnostic/diagnostic-describe.xml \
  vcfcf_rdm_discovery_diagnostic
```

Both real descriptor attempts returned **exit 2**:
`BLOCKED_PLATFORM_DEPENDENCY missing_class=org.apache.logging.log4j.LogManager`.
The full loader classpath excludes `tests/org` and all test-only logging shims.
Existing partial key/descriptor tests retain their explicitly test-only logging
linkage; they do not replace this full-loader result. The proposed diagnostic
descriptor remains E4.6's unregistered historical candidate, not a new kind
implemented or approved for installation by E4.8.

| Offline validation | Actual result |
|---|---|
| New dependency inventory/guard tests | PASS, 14 unittest methods, including four inherited-JVM-option variants |
| Actual full SDK descriptor loading | Both BLOCKED as above; no positive result fabricated |
| `validate-sdk` | PASS, 21 production Java sources; unchanged legacy source/target-11 and deprecation warnings |
| Existing diagnostic / SOAP wire regressions | PASS, 243 + 22 assertions, without sockets |
| Existing Operations / runtime / discovery regressions | PASS, 281 assertions / 62 cases / 54 cases, no live endpoints |
| Existing fixture/topology regressions | PASS, 8 topology/descriptor tests, 42 invalid runtime cases and 34 invalid LUN cases plus positive matrices |
| Complete factory test suite | 2,500 passed, 15 skipped, 131 deselected, 293 warnings; one unchanged Git-detection failure |
| Content validation / skill parity / path audit | PASS; 5 paired/7 Codex-only skills, six standing path warnings, no dead references |

The unchanged factory failure is
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
expected no-repository wording differs from the conservative unknown Git-ignore
verdict. It was not modified or weakened. No new TLS transport test was needed
for this offline classpath/tooling-only change; existing transport code is
unchanged. No PAK build/comparison is performed or claimed.

No external dependency version/checksum/provenance has been qualified beyond
the supplied SDK. New checker output is an inventory, not a trusted-artifact
attestation; keep supplied files immutable during validation. It does not sandbox
malicious JARs. Use only an operator-approved, clean local classpath/environment.

Independent [SDK review](../../context/reviews/rdm-topology-e48-sdk-review.md):
**APPROVE** the bounded tooling/documentation and honest BLOCKED disposition,
zero outstanding findings. This is not full-loader or installation approval.
The reviewer independently reran the new tests and both real loader attempts.

## E4.9 recommendation

Do not replace or reconfigure live build 9. First supply the dependency handoff
and complete shim-free loading of the current and proposed descriptors. Once
qualified, implement the small same-kind dispatcher and backward-compatible
conditional descriptor from E4.7, with fixture parity and empty diagnostic
publication tests. Re-run the real loader against that changed descriptor.
Successful offline loading will still not establish collector lifecycle/UI,
injected authentication, RBAC, routing, managed CA delivery or topology behavior.
