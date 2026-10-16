# E4.8 final shim-free descriptor-loader qualification — independent review

## Verdict

**APPROVE — the actual SDK descriptor-loading gate is qualified for both
exercised descriptors using the recorded external classpath.** Zero outstanding
findings. This is not approval of a diagnostic PAK, a second adapter kind,
installation, same-kind dispatcher implementation or live runtime behavior.
If used as-is, the offline launcher completes both SDK model loads successfully
without test logging shims. The deployed build-9 adapter remains unchanged.

This final result supersedes the **remaining loader-dependency blocker**, not
the historical evidence, in the [six-library review](rdm-topology-e48-local-libraries-review.md)
and [initial review](rdm-topology-e48-sdk-review.md).

## Independent dependency and provenance verification

The operator supplied the matching Commons Lang **2.6** JAR alongside Lang 3.
Actual ZIP entries contain
`org/apache/commons/lang/exception/NestableException.class`; manifest
implementation/specification version is 2.6. Destination SHA-256 is
`50f11b09f877c294d56f24463f47d28f929cf5044f648661c0f0cfbae9a2f49c`.
This resolves the superclass required by Commons Configuration 1.10; it is not
a substitution for the distinct `org.apache.commons.lang3` package.

Independently ran `sha256sum --check SHA256SUMS` in the external library
directory: **all seven JARs OK, exit 0**. The updated operator-provided
appliance-source manifest has SHA-256
`4c9f61b2537ead0488d84f52f8c531389df322d223a3fa0cdd51ec13f0f2f9d3`.
The other six versions/hashes are unchanged from the six-library review.
Destination bytes match the operator-provided source record; appliance origin
is operator-asserted, not independently attested through SSH or source filesystem
inspection. No source provenance stronger than that is claimed.

The local-only proprietary SDK remains SHA-256
`2d53a91fc2b9a99d9b685ed10c1e37a471c2f71f04e7ae0fb2c53fdaa14b4f54`.
SDK/platform libraries remain external to both Git repositories and PAK inputs,
are not redistributed/reproducible from Git, and are summarized here rather
than copied into the review. The specific SDK requires Java 17+ execution.

## Independently rerun actual SDK loads

Used the guarded launcher with the supplied SDK and explicit external JAR order:
Log4j API 2.17.2, Log4j Core 2.17.2, Commons Configuration 1.10, Commons Lang 3
3.14.0, Commons Collections 3.2.2, Commons Logging 1.3.5, Commons Lang 2.6.
No directories, wildcards, inherited Java injection, `tests/org` classes,
synthetic platform classes or logging shims were used. The checker verified
archive integrity/class inventory before the real SDK `AdapterDescribe.make()`
was invoked in the standalone hardened JVM.

| Descriptor | Actual SDK result | Exit |
|---|---|---|
| Current `vcfcf_rdm_topology_poc` | `PASS resource_kinds=3 credential_kinds=0` | **0** |
| Historical unregistered diagnostic descriptor | `PASS resource_kinds=1 credential_kinds=1` | **0** |

No additional missing class was encountered on these two successful model-load
paths. This is sufficient closure for **these exercised descriptors**, not proof
that every SDK method, optional feature or future descriptor needs only these
libraries. Nor was each JAR individually removed to establish a minimal set;
Log4j Core's supplied presence does not prove it mandatory.

The inventory still correctly prints `INVENTORY_ONLY
platform_compatibility=UNVERIFIED`: inventory alone does not certify provenance
or compatibility. The separate actual-loader PASS above supplies the narrower
empirical compatibility evidence. In particular, the supplied Commons Logging
1.3.5 works on these tested paths despite an older SDK build property; broader
platform compatibility is not implied.

All **15** dependency/guard tests independently passed again. They remain
metadata-only synthetic tests, not substitutes for the actual model loads.
The unchanged build-9 PAK SHA-256 is
`9f452ebcea4a3abbddf4224707407831ef2b7543a0aebcdb05aabb13d4e0cbfb`.
No new PAK/build/comparison or production-code result is claimed.

## Remaining boundary and E4.9 recommendation

The loader dependency prerequisite is resolved. Proceed with the previously
approved **same-kind dispatcher** implementation design as the next offline
increment, preserving fixture behavior and proving zero diagnostic publication
across all lifecycle/error/cancellation paths. Its new union descriptor must
undergo its own shim-free actual-loader check; success for the historical
distinct-kind candidate does not approve creating that parallel identity.

Controller bare instantiation, UI/configuration serialization, managed CA
delivery, injected credentials/decryption, authentication, RBAC, collector and
Cloud Proxy routing, actual discovery and upgrade safety remain separate
runtime prerequisites. No live execution, topology publication or installation
is authorized by this review.

Authority: SDK skill “Classloader isolation,” “Gaps” and “Build / verify loop”;
RULE-001, RULE-005, RULE-008, RULE-015 and reviewer-doctrine independent
verification. The declared defect registry has no open entry naming this RDM
adapter; no closure or new surviving implementation defect is proposed.
Only this review report was written. No live calls, credential reads, dependency
downloads/transfers, runtime/descriptor/metadata changes, PAK generation,
installation, commits or pushes occurred in this review.
