# E4.8 supplied-library continuation — independent SDK review

## Verdict

**APPROVE the evidence assessment; full shim-free descriptor qualification remains
BLOCKED.** No implementation defect or unsafe workaround identified. Both real
SDK descriptor attempts now reach a missing Commons Lang **2** superclass, not
Log4j. No descriptor PASS, installation approval or complete dependency closure
is claimed. If used as-is, the launcher fails closed with the exact sanitized
missing-class category.

This continuation supplements, rather than rewrites, the historical
[initial E4.8 review](rdm-topology-e48-sdk-review.md). Read-only inspection and
offline class loading only; no Java/runtime/descriptor changes or PAK build.

## Independently inspected local files

The operator reports these six JARs were copied from the authorized development
appliance. ZIP integrity, manifest versions, class ownership and destination
SHA-256 were independently checked. The operator subsequently supplied the
appliance-source `SHA256SUMS` record: independent `sha256sum --check` returned
**all six OK, exit 0**. Destination bytes therefore match the operator-provided
source hash record. This relies on the operator's asserted source provenance;
no independent SSH/appliance attestation or source filesystem access occurred.
The manifest itself has SHA-256
`3a1c5a4429e2b55cc9dc2d0e6a1e419e01a3de37db50987b22e080e752d97dd9`.
The libraries are local-only, outside both Git repositories and
PAK inputs; not redistributed or reproducible from Git. Findings are summarized
fully below.

| Supplied filename | Manifest implementation version | Destination SHA-256 |
|---|---|---|
| `log4j-api-2.17.2.jar` | 2.17.2 | `09351b5a03828f369cdcff76f4ed39e6a6fc20f24f046935d0b28ef5152f8ce4` |
| `log4j-core-2.17.2.jar` | 2.17.2 | `5adb34ff4197cd16a8d24f63035856a933cb59562a6888dde86e9450fcfef646` |
| `commons-configuration-1.10.jar` | 1.10 | `95d4e6711e88ce78992c82c25bc03c8df9ecf5a357f0de0bec72a26db3399374` |
| `commons-lang3-3.14.0.jar` | 3.14.0 | `7b96bf3ee68949abb5bc465559ac270e0551596fa34523fddf890ec418dde13c` |
| `commons-collections-3.2.2.jar` | 3.2.2 | `eeeae917917144a68a741d4c0dff66aa5c5c5fd85593ff217bced3fc8ca783b8` |
| `commons-logging-1.3.5.jar` | 1.3.5 | `6d7a744e4027649fbb50895df9497d109f98c766a637062fe8d2eabbb3140ba4` |

The supplied Logging version differs from the SDK's inherited 1.1 build
property. The property alone is not the appliance's installed dependency list;
do not reject or certify this supplied version solely from that difference.
Runtime compatibility remains incompletely exercised because loading stops
earlier. Log4j Core's inclusion does not establish that Core is mandatory.

## Actual-loader results and exact remaining dependency

Used the real SDK plus the six explicit JARs, no wildcard/directory or `tests/org`
logging shims. The checker completed ZIP/hash/class inventory with
`INVENTORY_ONLY platform_compatibility=UNVERIFIED`. Both descriptor probes then
ran `AdapterDescribe.make()` in their standalone guarded JVM:

| Descriptor | Result |
|---|---|
| Current `vcfcf_rdm_topology_poc` descriptor | exit **2**, `BLOCKED_PLATFORM_DEPENDENCY missing_class=org.apache.commons.lang.exception.NestableException` |
| Historical diagnostic descriptor | exit **2**, same missing class |

The supplied Commons Configuration 1.10 bytecode independently establishes:

`ConfigurationException extends org.apache.commons.lang.exception.NestableException`.

Its embedded Maven POM explicitly depends on `commons-lang:commons-lang:2.6`.
This is evidence for the next dependency, not speculation from a filename.
The supplied `commons-lang3` JAR provides `org.apache.commons.lang3.*`, **not**
`org.apache.commons.lang.*`; both package families may legitimately be needed.
Do not replace Lang 3, invent an exception shim, or modify descriptor validation.
Ask the operator to identify the appliance-owned JAR supplying
`org/apache/commons/lang/exception/NestableException.class`, record its actual
filename/version/source and SHA-256, and supply that matching JAR externally.
`commons-lang-2.6.jar` is a conventional filename inferred from the POM, not an
observed appliance file. Further transitive gaps may emerge; optional POM
dependencies are not automatically mandatory for this loading path.

## Other independent checks and next step

All **15** dependency/guard tests passed on the final continuation, including
the new deterministic proof that Lang 3 metadata cannot satisfy the observed
Lang 2 class requirement. The checker now reports `NestableException` under
`observed_transitive_loader`, accurately distinguishing actual loading evidence
from SDK-wide candidates. Frozen checker SHA-256 is
`d23f610ef7a8578009f6a3a86c2c8151dcdbff97342ed1300d797a931388b413`;
test SHA-256 is
`5e97bd46dc988fe2030f61d1fec9335ca9286f46076c16424695a2f73e4f2cd4`.
Adapter whitespace check passed.
Build-9 PAK remains SHA-256
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`;
no new package, comparison or production test result is claimed. No runtime,
registered metadata, fixture, identity or topology semantics changed.

Reviewed the [supplied-library addendum](../../designs/managementpacks/vsphere-rdm-topology-e48-supplied-platform-libraries.md):
its unexecuted operator-only class-owner locator uses read-only standard-library
ZIP inspection and file hashing, not API access, credentials or Java class
initialization. It distinguishes the conventional Lang 2 filename from actual
appliance observation, handles directory-scoped absence without a global claim,
and records hash equality against the operator-provided source manifest without
claiming independently observed appliance provenance. No additional
finding arose from these instructions.

Authority: SDK skill “Classloader isolation,” “Gaps” and “Build / verify loop”;
RULE-001, RULE-005, RULE-008, RULE-015 and reviewer-doctrine gap honesty.
The declared defect registry has no open entry naming this RDM adapter; no
registry closure or new surviving implementation defect is proposed.

Continue dependency qualification with the matching Lang 2 library and its source
transfer evidence. The six existing files now match the supplied source record;
the missing library has not yet been supplied. Re-run both actual loaders before
describing E4.8 as complete.
E4.9's same-kind dispatcher remains conditional on loader qualification; no
live UI/lifecycle, credential injection, RBAC, trust delivery or routing claim
follows from classpath progress. No live access, downloads, binary copying,
installation, commits, pushes or PAK generation occurred in this review.
