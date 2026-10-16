# E4.9.2 — Independent framework entry-constructor review

Verdict: **APPROVE** — zero outstanding BLOCKING, WARNING or NIT findings
within the reviewed framework change. This is an offline tooling verdict, not
approval to install or change the development Operations environment.

## Scope and authority

Reviewed the complete working-tree diff under `src/vcfcf_*/`: only
`src/vcfcf_managementpacks/sdk_builder.py` is changed. The review covers the new
constructor guard and rechecks the retained E3.5.1 descriptor guard, whose
authority and original independent review are recorded in
`knowledge/context/sdk-describe-key-contract.md` and
`knowledge/context/reviews/framework/sdk-descriptor-keys-e351.md`.

The collector's operator-reported reflection call requires exactly public
`(String, Integer)` construction. Independent inspection of the authorized
local Broadcom SDK confirms `AdapterBase` declares public no-arg and
`(String, Integer)` constructors. The controller's bare describe requirement
is independently documented in
`knowledge/lessons/controller-describe-bare-instantiation.md`. Constructors
are not inherited; a successfully compiled direct-interface entry class can
therefore still violate either platform construction contract.

This review applies RULE-005 and RULE-013, the shared reviewer doctrine and
the named global-default/key-collision escape anchors `00d3382` and `6c59f6b`.
The local SDK is proprietary and not reproducible from Git; only the bounded
findings above are summarized, not the artifact or its implementation.

## Implementation assessment

- The generic guard inspects the configured compiled entry class with
  `javap -public -s`, without class loading, static initialization, constructor
  execution, network access or platform credential access.
- It requires a public concrete class and both exact declared public JVM
  constructor descriptors. Primitive `int`, `Object`, varargs, private and
  inherited alternatives cannot satisfy the boxed-Integer reflection ABI.
  Generic constructors with matching erased descriptors are correctly accepted.
- Missing class/tool, invalid binary name, timeout, nonzero inspection result,
  malformed metadata and excessive class/output size fail closed. There are no
  adapter-specific names, exceptions, finding waivers or suppressions.
- `validate_sdk_project` checks after successful compilation; direct
  `build_sdk_pak` checks before adapter properties, JAR/document generation or
  PAK assembly. Public CLI and generated portable buildkit delegate to these
  same functions; no alternate packaging bypass was found.
- Existing no-SDK/no-JDK validation behavior remains a documented skip, now
  explicitly reporting constructor checks as **unverified**. Actual builds
  cannot claim a verified ABI without successful inspection. Missing `javap`
  after compilation is an error, not a skip.
- Both modified buildkit test fixtures now implement the real ABI; their
  assertions and release-policy checks were not weakened. The retained
  descriptor guard still runs after the existing release/warn-only rejection,
  preserving its previously corrected error precedence.

The change adds no renderer defaults, transformations, localization-key
derivation, resource identity or relationship changes. It does not alter the
standalone content-import path or assembly templates; a global template-version
bump or broad content ZIP rebuild is not warranted by this validation-only
change. The adapter implementation, PAK bytes and real collector lifecycle
qualification remain separate SDK/security-review surfaces.

## Independent reruns

Commands were run locally without installation, live calls or release builds.
Factory tests used `PYTHONPATH=src` and the explicitly supplied local
`VCFCF_SDK_JAR`; no substitute dependency or shim was introduced.

| Check | Actual result |
|---|---|
| New constructor regression module | 21 passed |
| Complete management-pack test directory | 339 passed, 8 skipped, 115 warnings |
| Complete factory suite | 2,521 passed, 15 skipped, 131 deselected, 293 warnings; one existing failure |
| `scripts/validate-changed-content.sh --all` | PASS, exit 0 |
| Codex skill parity | PASS: five paired, seven Codex-only |
| Path-reference audit | PASS: no dead references; six documented standing-exception warnings |
| `git diff --check` | PASS |

The full-suite failure is the unchanged
`tests/test_common_setup.py::test_a_128_with_no_git_anywhere_above_reads_as_not_a_repo`:
the test expects the reassuring no-repository sentence, while the implementation
returns the conservative unknown-git-ignore verdict. Neither setup production
code nor that test is changed here. This failure is recorded, not waived or
reported as a green factory suite; it does not originate in constructor or
descriptor validation. Full-suite render/localization tests were included;
no new rendering failure appeared. No PAK comparison was run by this framework
reviewer because it is an artifact/SDK review surface and this guard does not
change emitted PAK content.

Reviewed source SHA-256:

```text
10c7f9eff6464bba8667adf84bedb8b37b0f78d41602cddde3dcf851d1a3b5ce  sdk_builder.py
7999ccd4940c8134cf49fe9117e1741b0a988fda8ed6384af7e12253011ffec8  test_sdk_entry_constructor_contract.py
```

If shipped as-is: a native Java entry class lacking either platform constructor
fails local SDK validation/build before packaging instead of yielding another
installable-but-uninstantiable adapter. Correct entry classes retain existing
output behavior. This static guard does not prove initialization, injected
credentials, collector compatibility or successful topology collection.

No framework or adapter source was edited by this reviewer. No staging,
commits, PAK builds, live API calls, installation, publishing or settings changes
were performed.
