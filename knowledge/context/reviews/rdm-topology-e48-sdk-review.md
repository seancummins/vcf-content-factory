# E4.8 independent SDK descriptor-dependency review

## Verdict

**APPROVE the offline dependency inventory, guarded launcher and honest BLOCKED
disposition.** Zero outstanding implementation findings. **Full descriptor
qualification remains BLOCKED**; this is not approval of a PAK, installation or
runtime dispatcher. If used as-is, the tool reports the missing platform class
and refuses to claim successful SDK descriptor loading.

Reviewed the [E4.8 dependency assessment](../../designs/managementpacks/vsphere-rdm-topology-e48-descriptor-dependencies.md),
adapter-local checker, launcher, tests and dependency instructions. Independently
inspected the actual supplied SDK's embedded Maven metadata, class references
and loader bytecode. No adapter source, configuration, PAK or SDK binary was
edited by this reviewer.

## Independently established dependency evidence

The supplied SDK is a local-only proprietary artifact, not reproducible from
Git and not redistributed. Its SHA-256 is
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
Its embedded Maven coordinates are `com.vmware.vcops:vrops-adapters-sdk:1.0`,
not a version inferred from its filename. `AdapterDescribe` has class-file
major 61, so this particular SDK requires Java 17+ for execution; compiling the
probe with `--release 11` does not change that requirement.

- `AdapterDescribe` static initialization calls Log4j `LogManager.getLogger`.
  Both clean actual-loader attempts fail on this first missing class.
- SDK localization/descriptor classes reference Commons Configuration **1.x**
  `ConfigurationException` and `PropertiesConfiguration`. Configuration 2.x
  is not an interchangeable dependency.
- Embedded POM evidence supports Commons Configuration 1.10 and Commons Lang 3
  3.14.0 as explicit dependencies, and Log4j 2.17.2 as a build property.
  This is build metadata, not proof of the appliance's installed bytes.
- Commons Lang 2, Logging, Collections, Log4j Core and SDK-wide security/TLS/JAXB
  references do not establish the complete minimum descriptor-loader closure.
  In particular, Core is not made a mandatory gate merely because unrelated SDK
  logging classes reference it. Actual execution with matching genuine libraries
  must establish the dynamic closure.

No matching platform JAR set was available in the authorized SDK directory or
bounded local searches. External library versions, hashes and source provenance
cannot honestly be recorded until those files are supplied. Do not download
arbitrary replacements, construct shims or copy another integration's library
tree to manufacture a pass.

Final documentation re-review: the proposed operator-only appliance command is
read-only Python-standard-library ZIP class-ownership and SHA-256 inspection.
It does not initialize Java classes, call APIs, retrieve credentials or write
files; it was not executed during this increment. The documented platform
directory has prior repository evidence, conventional filenames remain clearly
unobserved candidates, and missing classes are reported only within that
directory's scope. The external local destination is outside both repositories.
These instructions do not qualify provenance or imply permission to transfer
unrelated libraries. No additional finding arose from this documentation change.

## Tool and boundary review

The checker inspects explicitly supplied local JARs without extraction, class
loading or downloads. It bounds archive sizes, verifies ZIP integrity, reports
indexed SHA-256 and sanitized version fields, and rejects wildcard/directory/
empty classpath entries, duplicate paths/classes and hidden manifest classpaths.
The standalone inventory's exit 0 means **INVENTORY_ONLY**, not readiness; its
output explicitly says platform compatibility is unverified. The integrated
launcher still invokes the actual SDK and preserves its blocked/failure status.

The launcher excludes `tests/org` logging linkage and rejects inherited
`JAVA_TOOL_OPTIONS`, `JDK_JAVA_OPTIONS`, `_JAVA_OPTIONS` and `CLASSPATH` before
starting Java. These guards do not authenticate arbitrary JAR provenance or
make the utility a malicious-code sandbox; operator-controlled matching files
and a clean Java environment remain required. External files must remain
immutable during validation; hashes are not a concurrent-file snapshot.

The existing actual-loader probe is unchanged. Its hardened preflight and
standalone-JVM external XML access restrictions remain intact. Synthetic ZIP
entries in new tests are metadata fixtures only and are never loaded by Java.
Partial legacy tests retain explicitly test-only logging linkage; their passing
result is not substituted for full shim-free descriptor loading.

Authority: SDK skill sections “Classloader isolation,” “Gaps” and “Build / verify
loop”; RULE-001, RULE-005, RULE-008, RULE-015 and RULE-016; reviewer doctrine
independent verification and gap honesty. The controller describe lesson remains
applicable: successful model loading would not establish bare entrypoint
construction, platform injection or collector lifecycle acceptance.

## Independent verification

| Check | Observed result |
|---|---|
| New dependency/launcher regression tests | **14 passed**, including four inherited Java-option variants and corrupt-JAR diagnostic redaction |
| Actual SDK loader, current descriptor | **exit 2**, `BLOCKED_PLATFORM_DEPENDENCY`, `org.apache.logging.log4j.LogManager` |
| Actual SDK loader, historical diagnostic descriptor | **exit 2**, same missing class; no shim-free positive result |
| Existing fixture/topology runner | PASS: 42 invalid-runtime cases, 34 invalid-LUN cases, 8 topology/descriptor tests plus positive matrices |
| `validate-sdk` | PASS, 21 production sources; existing source/target-11 and deprecated-callback warnings |
| Shell syntax and adapter whitespace checks | PASS |

Reviewed frozen checker SHA-256:
`44c0a20e5a8c6dc2945d46e89b27e405468964771a954a0ae23c24848b0048ae`;
launcher:
`b9b2ac1f83ac23313ad5d202d691519497f18180b8c6ef828f2f9c15130511cd`;
regression tests:
`7d243012fc207ac9cd106522e92f7f5453e168111d04efebd0d85452ebc7a52c`.
Unchanged actual-loader probe:
`3a00409ce614d47254e6667ee91829bef1f99a7c5c8bb0529df9051456f49dac`.

Rechecked build-9 PAK SHA-256:
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
No new PAK or comparison is warranted for this test-only increment. Runtime
architecture, registered metadata, fixture identity and topology semantics are
not changed by these four adapter-local tooling/documentation files.

## E4.9 prerequisites

Obtain administrator-supplied matching libraries with source appliance/build,
original paths, manifest/Maven versions and source/destination SHA-256 evidence.
Keep them outside both repositories and PAK inputs. Re-run both real descriptor
loads and resolve further observed dependencies without shims. Only then claim
descriptor qualification and proceed with the approved same-kind dispatcher
implementation/testing; its modified descriptor needs its own actual-loader
run. Offline loader success alone does not prove UI serialization, managed CA
delivery, injected authentication, RBAC, Cloud Proxy routing or live collection.

Registry check: inspected the declared defect registry's affected scopes; no
open entry names this RDM adapter. No closure or new surviving defect
registration is proposed. No live API calls, credential reads, package builds,
installation, commits, pushes or external dependency retrieval occurred.
