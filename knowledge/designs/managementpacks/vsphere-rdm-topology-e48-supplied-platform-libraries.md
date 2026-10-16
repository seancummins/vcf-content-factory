# E4.8 continuation — Supplied platform libraries

Latest outcome: [seven-library offline qualification](#seven-library-offline-qualification)
passes both actual descriptor loads. The six-library rejection below is retained
as historical evidence, not the current disposition.

## Six-library checkpoint (historical)

**Full shim-free descriptor qualification remains BLOCKED.** The six supplied
external libraries resolve the previous Log4j/Configuration dependency stage,
but both actual SDK descriptor loads now fail on
`org.apache.commons.lang.exception.NestableException` (exit 2). No PAK or
dispatcher is built, no installed adapter is changed, and no live API is called.
This continues the [initial E4.8 assessment](vsphere-rdm-topology-e48-descriptor-dependencies.md)
without replacing its historical evidence.

## Available artifacts and provenance boundary

The operator reports copying these libraries from the authorized development
Operations appliance into an external local descriptor-library directory.
The files are outside both Git repositories and PAK inputs. ZIP integrity,
actual class entries, manifest versions and destination SHA-256 were verified:

| Actual filename | Verified implementation version | Destination SHA-256 |
|---|---|---|
| `log4j-api-2.17.2.jar` | 2.17.2 | `09351b5a03828f369cdcff76f4ed39e6a6fc20f24f046935d0b28ef5152f8ce4` |
| `log4j-core-2.17.2.jar` | 2.17.2 | `5adb34ff4197cd16a8d24f63035856a933cb59562a6888dde86e9450fcfef646` |
| `commons-configuration-1.10.jar` | 1.10 | `95d4e6711e88ce78992c82c25bc03c8df9ecf5a357f0de0bec72a26db3399374` |
| `commons-lang3-3.14.0.jar` | 3.14.0 | `7b96bf3ee68949abb5bc465559ac270e0551596fa34523fddf890ec418dde13c` |
| `commons-collections-3.2.2.jar` | 3.2.2 | `eeeae917917144a68a741d4c0dff66aa5c5c5fd85593ff217bced3fc8ca783b8` |
| `commons-logging-1.3.5.jar` | 1.3.5 | `6d7a744e4027649fbb50895df9497d109f98c766a637062fe8d2eabbb3140ba4` |

**All six destination hashes match the recorded appliance hashes.** After the
initial search, the operator supplied the local source record
`/home/scummins/Documents/vmware-sdk/descriptor-libs/SHA256SUMS`.
Running `sha256sum --check SHA256SUMS` from that external directory returned
six `OK` results, exit 0. The table above therefore records both the source
manifest hashes and verified destination hashes. The record's appliance origin
is operator-attested; this is not an independent live appliance attestation.
No source checksum is invented or retrieved through a live connection.
The source-record file itself has SHA-256
`3a1c5a4429e2b55cc9dc2d0e6a1e419e01a3de37db50987b22e080e752d97dd9`.

The supplied SDK remains SHA-256
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
All binaries are local-only artifacts, not reproducible from Git; the evidence
is summarized here without copying or redistributing their bytes. Version
differences from embedded SDK build properties are recorded, not silently
"corrected": actual Commons Logging is 1.3.5; that is not proof the platform
must use the SDK's older inherited property value.

## Class inspection and exact remaining dependency

The actual JAR indexes supply Log4j `LogManager`/`Logger` and Core
`LoggerContext`, Commons Configuration `ConfigurationException` and
`PropertiesConfiguration`, Commons Lang3 builder helpers, Commons Logging
`LogFactory` and Commons Collections `CollectionUtils`. The actual new loader
failure is **not** a missing `org.apache.commons.lang3` class.

Verified with `javap` on the supplied Configuration JAR:

`org.apache.commons.configuration.ConfigurationException` extends
`org.apache.commons.lang.exception.NestableException`.

That JAR's embedded Maven POM explicitly declares
`commons-lang:commons-lang:2.6`. The expected artifact is **Commons Lang 2.6**,
conventionally `commons-lang-2.6.jar`; the matching appliance's actual filename
and bytes still need to be identified. Keep it **alongside**, not instead of,
Commons Lang3. No replacement, shim, synthetic class or dependency download is
used. Further transitive requirements remain unknown until execution advances.

Operator-only read-only lookup on the same appliance; **not executed here**:

```bash
python3 - <<'PY'
from pathlib import Path
from zipfile import ZipFile
from hashlib import sha256
root = Path('/usr/lib/vmware-vcops/common/lib')
if not root.is_dir():
    raise SystemExit('Platform library directory unavailable')
target = 'org/apache/commons/lang/exception/NestableException.class'
found = False
for jar in sorted(root.glob('*.jar')):
    with ZipFile(jar) as archive:
        match = target in archive.namelist()
    if match:
        found = True
        print(str(jar), 'sha256=' + sha256(jar.read_bytes()).hexdigest())
if not found:
    print('NOT_FOUND_IN_COMMON_LIB', target)
PY
```

This reads library ZIPs only, not credentials, configuration or inventory.
Record the actual source hash and provenance, transfer only the matching JAR
through the approved operator channel to the same external local directory,
and compare destination hash before adding it to the explicit validation
classpath. Multiple owners or directory-scoped absence need investigation;
do not pick an arbitrary version. No automated transfer or appliance access is
authorized by this document.

## Reproduction and qualification boundary

The existing checker and launcher were run with exactly the supplied SDK plus
the six explicit local JAR paths, no wildcard/directory classpath, no test
logging classes and no platform shims. The external directory is
`/home/scummins/Documents/vmware-sdk/descriptor-libs/`.

Use the [E4.8 checker/loader commands](vsphere-rdm-topology-e48-descriptor-dependencies.md)
with `VCFCF_DESCRIPTOR_CLASSPATH` explicitly listing those six files, adding
the genuine matching Lang 2 JAR only after its provenance/contents are verified.
The inventory's exit 0 means inventory completed, not full-loader PASS.

| Check | Result |
|---|---|
| Explicit dependency inventory / integrity | Completed, exit 0; class ownership and versions inspected, not a compatibility attestation |
| Current build-9 descriptor, actual SDK | BLOCKED, exit 2, missing `org.apache.commons.lang.exception.NestableException` |
| Historical proposed diagnostic descriptor, actual SDK | BLOCKED, exit 2, same exact class |
| Source/destination provenance comparison | All six match operator-supplied appliance `SHA256SUMS`; exit 0 |

The dependency checker now additionally reports the actually observed
`NestableException` under `observed_transitive_loader`; a deterministic
metadata-only Lang3-does-not-satisfy-Lang2 regression was added. **15 tests pass.**
Runtime code, active descriptor, metadata, identities,
relationships and installed build 9 are outside this continuation's changes.
No PAK build, installation, commit, push or release occurs.

`validate-sdk` passes for all 21 production sources with the existing source/
target-11 and deprecated-API warnings. Existing fixture/topology tests pass:
8 topology/descriptor tests, 42 invalid runtime cases, 34 invalid LUN cases and
positive roundtrip/idempotence matrices. Their explicitly test-only logging
linkage is not used in either full descriptor-loader attempt. Changed/full
content validation, skill parity and path audit pass (six standing path warnings,
no dead references). No new full factory-suite run is claimed for this narrow
continuation; the unchanged Git-detection failure remains in the initial record.

Independent [SDK continuation review](../../context/reviews/rdm-topology-e48-local-libraries-review.md):
**APPROVE** the assessment and narrow tooling correction, with no outstanding
findings. The reviewer independently verified all six source-record checksum
matches, JAR contents, 15 tests and both blocked loader results. Full loader
qualification remains BLOCKED, not waived or reclassified as PASS.

**E4.9 recommendation:** retain the approved same-kind dispatcher design, but
do not claim E4.8 qualified until both full loaders succeed with the genuine
dependency closure and recorded source hashes agree. Those results would still
not establish collector lifecycle, trust delivery, credentials, RBAC or routing.

## Seven-library offline qualification

The operator subsequently supplied `commons-lang-2.6.jar`, SHA-256
`50f11b09f877c294d56f24463f47d28f929cf5044f648661c0f0cfbae9a2f49c`.
The destination exactly matches the independently supplied source hash and the
updated local `SHA256SUMS` record. All **seven** manifest entries verify `OK`,
exit 0. The updated manifest SHA-256 is
`4c9f61b2537ead0488d84f52f8c531389df322d223a3fa0cdd51ec13f0f2f9d3`.
The original six JAR hashes above remain unchanged. Appliance-source provenance
is operator-attested, not independently fetched from a live system.

Actual ZIP inspection confirms both
`org/apache/commons/lang/exception/NestableException.class` and
`org/apache/commons/lang/NotImplementedException.class`; the manifest identifies
implementation/specification version **2.6**. The genuine Lang 2 library is
present alongside Lang3, not substituted for it. All seven remain external to
both repositories and PAK inputs.

Re-ran the existing dependency checker and actual SDK loader using the supplied
SDK plus the explicit seven-file classpath (the original six in their recorded
order, followed by the new Commons Lang 2.6 path). No test logging classes,
substitute classes, runtime downloads or inherited classpath were used.

| Final check | Actual result |
|---|---|
| Integrity/version/class inventory | Completed; all probed dependency classes present, no hidden classpath or duplicate-class rejection |
| Current build-9 descriptor | **PASS**, exit 0; `resource_kinds=3 credential_kinds=0` |
| Historical proposed diagnostic descriptor | **PASS**, exit 0; `resource_kinds=1 credential_kinds=1` |
| Current descriptor with deliberately wrong expected adapter kind | Correct rejection, exit 1, `INVALID_DESCRIPTOR` |
| Dependency/launcher regression tests | **15 passed** |

No further missing transitive dependencies were observed for these **two
exercised descriptors**. The seven-file set is sufficient for these loads, not
proven minimal or universally complete for all SDK paths/descriptors. This run
used local OpenJDK **25.0.4.1**; it is not an empirical collector-JDK/FIPS matrix.
The supplied SDK class-file major 61 still requires Java 17+.

**E4.8 descriptor-loader dependency gate: QUALIFIED offline for these inputs.**
This does not approve a separate adapter kind or establish UI/localization,
bare entrypoint construction, collector lifecycle, CA delivery, injected
authentication/RBAC/routing, installation or topology publication. E4.9 can
proceed with the preferred same-kind dispatcher implementation once separately
requested; its modified union descriptor must undergo the actual loader again.

Independent [final SDK review](../../context/reviews/rdm-topology-e48-qualified-loader-review.md):
**APPROVE**, zero outstanding findings; both full loads, all seven hash matches
and 15 tests independently rerun. Changed/full content validation, skill parity
and path audit pass (six standing path warnings, no dead references).
This continuation changes documentation only. Production
Java, active descriptors, library binaries and build-9 PAK are unchanged;
build-9 SHA-256 remains
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
No live calls, builds, installation, Git staging, commits, pushes or releases.
