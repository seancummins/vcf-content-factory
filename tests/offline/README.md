# Opt-in guarded offline tests

Run from an **externally read-only Linux checkout** with the existing project
interpreter, Landlock ABI 3+ and system libseccomp. The runner does not install
anything, remount filesystems or change CI. It derives the checkout root and uses
`sys.executable`; no inherited credentials or Java/Git/Python configuration is
forwarded. Linux x86_64 and aarch64 are supported; unavailable prerequisites fail
closed before pytest starts.

```sh
.venv/bin/python -B tests/offline/run.py --smoke
.venv/bin/python -B tests/offline/run.py
.venv/bin/python -B tests/offline/run.py --test tests/test_offline_runner.py
.venv/bin/python -B tests/offline/run.py --sdk-jar /absolute/authorized/sdk.jar
```

`--test tests/path.py[::node]` can be repeated; paths must remain inside this
checkout's tests tree. There is no arbitrary command or pytest-option passthrough.
The default runs `tests` serially, clears the default slow-marker exclusion, and
disables pytest cache and bytecode writes. The process returns pytest's exit
status, including failures. New runner tests detect the inherited guard and do
not recursively launch another full run.

Every pytest run explicitly deselects exactly:

`tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path`

That test's pip wheel/build-isolation/install fixture may download dependencies
and write build metadata into the real checkout. Missing local `setuptools>=64`,
`setuptools-scm>=8` and `wheel` prerequisites are reported, without installation;
having them does not remove the exclusion. Report results as a **guarded suite
with this exclusion**, including remaining failures/skips, never a complete green
suite. Baseline failures are neither excluded nor xfailed by the runner.

The launcher creates a unique owned mode-0700 `/tmp/vcfcf-offline-*` directory and
prints it for inspection. Scratch and synthetic smoke sentinels are retained;
remove only those exact owned paths when no longer needed. Landlock restricts
content writes to scratch; inherited seccomp denies native child socket creation,
connections and sends, including Python `-S`, shell and JVM children. Project
root credential files/private credential directories are excluded from reads.
Python's startup audit also blocks credential-file reads and network operations,
retains the guard in child Python environments, and preserves the real dotenv
parser only for synthetic `.env` fixtures found inside owned scratch. Discovery
outside scratch is a deliberate no-op: this is a guarded offline run, not an
ambient credential-loader integration test.

**Read-only inputs are required separately:** Landlock does not prevent native
metadata operations such as chmod/chown/utime/xattr. The runner checks read-only
mount flags for the checkout, its input subroots/mountpoints and an explicitly
supplied SDK. It never claims Landlock alone makes source immutable. The smoke
uses artificial local files to prove native outside-scratch read/write denial,
child socket denial, valid relative `dir_fd` writes, symlink unlink and synthetic
dotenv parsing. It does not probe actual credential files or claim a metadata
mutation test. Runtime system paths remain readable; this bounded tool is for
reviewed project tests, not arbitrary untrusted programs.
