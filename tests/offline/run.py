#!/usr/bin/env python3
"""Opt-in, serial Linux pytest runner for an externally read-only checkout."""
from __future__ import annotations

import argparse
import ctypes
import errno
import importlib.metadata
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[2]
WHEEL_TEST = "tests/test_core_row4_seams.py::test_offline_reverse_from_the_wheel_alone_matches_the_factory_path"
SENSITIVE = {".env", ".ssh", ".aws", ".password-store", ".netrc", "memory"}


class GuardUnavailable(RuntimeError):
    """A required execution boundary is unavailable; no tests may start."""


def selection(value: str, repo: Path = REPO) -> str:
    """Accept only existing in-tree pytest paths/node IDs, never pytest flags."""
    filename, *nodes = value.split("::")
    candidate = Path(filename)
    if candidate.is_absolute() or ".." in candidate.parts or not filename.startswith("tests/"):
        raise argparse.ArgumentTypeError("--test must name tests/<file.py>[::node] inside this checkout")
    resolved = (repo / candidate).resolve()
    if not resolved.is_relative_to((repo / "tests").resolve()) or not resolved.exists():
        raise argparse.ArgumentTypeError("--test must resolve to an existing path inside tests/")
    if resolved.is_file() and resolved.suffix != ".py":
        raise argparse.ArgumentTypeError("--test files must be Python tests")
    if any(not node or "\x00" in node or "\n" in node for node in nodes):
        raise argparse.ArgumentTypeError("--test contains an invalid pytest node ID")
    return value


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, epilog="No installs, downloads, live access, remounting, or arbitrary command/pytest flags.")
    parser.add_argument("--smoke", action="store_true", help="test restrictions using synthetic local files; do not run pytest")
    parser.add_argument("--sdk-jar", type=Path, help="optional explicit nonsecret path to an authorized local SDK JAR")
    parser.add_argument("--test", action="append", type=selection, default=[], metavar="tests/PATH[::NODE]", help="bounded pytest selection; repeatable; default: all tests serially")
    args = parser.parse_args(argv)
    if args.smoke and args.test:
        parser.error("--smoke and --test are separate actions")
    if args.sdk_jar is not None:
        args.sdk_jar = args.sdk_jar.resolve()
        if args.sdk_jar.suffix != ".jar" or not args.sdk_jar.is_file():
            parser.error("--sdk-jar must name an existing authorized .jar file")
    return args


def readonly_inputs(repo: Path, sdk: Path | None = None):
    """Landlock cannot deny chmod/utime/xattrs: require read-only input mounts."""
    inputs = [repo, *(p for p in repo.iterdir() if p.name not in SENSITIVE)]
    if sdk is not None:
        inputs.append(sdk)

    def require_readonly(path):
        if not os.statvfs(path).f_flag & os.ST_RDONLY:
            raise GuardUnavailable("source/SDK inputs must already be externally read-only; use a read-only execution environment (this runner does not remount)")

    # Refuse writable inputs before requiring Linux-specific mount enumeration.
    for path in inputs:
        require_readonly(path)
    try:
        mounts = Path("/proc/self/mountinfo").read_text().splitlines()
    except OSError:
        raise GuardUnavailable("Linux mountinfo is unavailable; no tests started") from None
    # Detect separate mounts at any depth, including bind-mounted input trees.
    for line in mounts:
        mount = Path(line.split()[4].replace("\\040", " ").replace("\\011", "\t").replace("\\134", "\\"))
        if mount.is_relative_to(repo) and not any(part in SENSITIVE for part in mount.parts):
            require_readonly(mount)


def environment(repo: Path, work: Path, sdk: Path | None = None) -> dict[str, str]:
    """Build from constants, not inherited credentials or tool configuration."""
    env = {
        "PATH": str(Path(sys.executable).parent) + ":/usr/bin:/bin",
        "HOME": str(work / "home"), "TMPDIR": str(work / "tmp"),
        "XDG_CACHE_HOME": str(work / "cache"), "XDG_CONFIG_HOME": str(work / "config"),
        "XDG_DATA_HOME": str(work / "data"), "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "Etc/UTC",
        "PYTHONDONTWRITEBYTECODE": "1", "PYTHONNOUSERSITE": "1",
        "PYTHONPATH": str(work / "guard") + os.pathsep + str(repo / "src"),
        "VCFCF_OFFLINE_ACTIVE": "1", "VCFCF_OFFLINE_WORK": str(work),
        "VCFCF_OFFLINE_GUARD": str(work / "guard"),
        "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
        "PIP_NO_INDEX": "1", "PIP_NO_CACHE_DIR": "1",
    }
    if sdk is not None:
        env["VCFCF_SDK_JAR"] = str(sdk)
    return env


def pytest_argv(work: Path, tests: list[str]) -> list[str]:
    return [sys.executable, "-B", "-m", "pytest", *(tests or ["tests"]), "--override-ini=addopts=", "-m", "", "-p", "no:cacheprovider", "--basetemp=" + str(work / "pytest"), "--deselect=" + WHEEL_TEST, "-q", "-ra"]


def wheel_prerequisites() -> str:
    missing = []
    for name, minimum in (("setuptools", 64), ("setuptools-scm", 8), ("wheel", 0)):
        try:
            version = importlib.metadata.version(name)
            adequate = version.split(".", 1)[0].isdigit() and int(version.split(".", 1)[0]) >= minimum
        except importlib.metadata.PackageNotFoundError:
            adequate = False
        if not adequate:
            missing.append(name + (">=" + str(minimum) if minimum else ""))
    return "missing local prerequisites: " + ", ".join(missing) if missing else "local build prerequisites present; wheel isolation/install remains excluded"


def install_native_guard(repo: Path, work: Path, sdk: Path | None = None) -> int:
    if sys.platform != "linux" or platform.machine() not in {"x86_64", "aarch64"}:
        raise GuardUnavailable("Linux x86_64/aarch64 with Landlock ABI>=3 and libseccomp is required")
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    libc.prctl.argtypes = [ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong]
    libc.prctl.restype = ctypes.c_int

    def checked(value, operation):
        if value < 0:
            raise GuardUnavailable(operation + " unavailable; Linux Landlock ABI>=3 and seccomp must be enabled")
        return value

    class Ruleset(ctypes.Structure):
        _fields_ = [("handled_access_fs", ctypes.c_uint64)]

    class Beneath(ctypes.Structure):
        _layout_ = "ms"  # Explicit packed UAPI layout: offsets 0/8, size 12.
        _pack_ = 1
        _fields_ = [("allowed_access", ctypes.c_uint64), ("parent_fd", ctypes.c_int32)]

    checked(libc.prctl(38, 1, 0, 0, 0), "PR_SET_NO_NEW_PRIVS")
    abi = checked(libc.syscall(444, None, 0, 1), "Landlock ABI query")
    if abi < 3:
        raise GuardUnavailable("Landlock ABI>=3 is required; tests were not started")
    handled = (1 << 15) - 1
    attr = Ruleset(handled)
    ruleset = checked(libc.syscall(444, ctypes.byref(attr), ctypes.sizeof(attr), 0), "Landlock ruleset")
    read = (1 << 0) | (1 << 2) | (1 << 3)
    file_rights = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 14)

    def allow(path, rights):
        path = Path(path)
        if not path.exists():
            return
        if not path.is_dir():
            rights &= file_rights
        fd = os.open(path, os.O_PATH | os.O_CLOEXEC)
        try:
            rule = Beneath(rights, fd)
            checked(libc.syscall(445, ruleset, 1, ctypes.byref(rule), 0), "Landlock path rule")
        finally:
            os.close(fd)

    try:
        allow("/", 1 << 3)
        for runtime in ("/usr", "/etc", "/proc", "/sys", "/bin", "/sbin", "/lib", "/lib64"):
            allow(runtime, read)
        allow("/tmp", 1 << 3)
        allow(repo, 1 << 3)
        for child in repo.iterdir():
            if child.name not in SENSITIVE:
                allow(child, read)
        if sdk is not None:
            allow(sdk, read)
        allow(work, handled)
        allow("/dev/null", file_rights)
        allow("/dev/urandom", 1 << 2)
        allow("/dev/random", 1 << 2)
        checked(libc.syscall(446, ruleset, 0), "Landlock restriction")
    finally:
        os.close(ruleset)

    sec = None
    for path in ("/usr/lib64/libseccomp.so.2", "/usr/lib/x86_64-linux-gnu/libseccomp.so.2", "/lib/x86_64-linux-gnu/libseccomp.so.2", "/usr/lib/aarch64-linux-gnu/libseccomp.so.2", "/lib/aarch64-linux-gnu/libseccomp.so.2"):
        if Path(path).is_file():
            try:
                sec = ctypes.CDLL(path, use_errno=True)
            except OSError:
                raise GuardUnavailable("system libseccomp.so.2 could not load; no tests started") from None
            break
    if sec is None:
        raise GuardUnavailable("libseccomp.so.2 is required from the existing system installation; no tests started")
    sec.seccomp_init.argtypes = [ctypes.c_uint32]
    sec.seccomp_init.restype = ctypes.c_void_p
    sec.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    sec.seccomp_syscall_resolve_name.restype = ctypes.c_int
    sec.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int, ctypes.c_uint]
    sec.seccomp_rule_add.restype = ctypes.c_int
    sec.seccomp_load.argtypes = [ctypes.c_void_p]
    sec.seccomp_load.restype = ctypes.c_int
    sec.seccomp_release.argtypes = [ctypes.c_void_p]
    ctx = sec.seccomp_init(0x7FFF0000)
    if not ctx:
        raise GuardUnavailable("seccomp initialization failed; no tests started")
    try:
        for name in ("socket", "socketpair", "connect", "sendto", "sendmsg", "sendmmsg"):
            number = sec.seccomp_syscall_resolve_name(name.encode())
            if number < 0 or sec.seccomp_rule_add(ctx, 0x00050000 | errno.EPERM, number, 0) != 0:
                raise GuardUnavailable("required seccomp network rule unavailable; no tests started")
        if sec.seccomp_load(ctx) != 0:
            raise GuardUnavailable("seccomp could not load; no tests started")
    finally:
        sec.seccomp_release(ctx)
    return abi


def smoke(work: Path, outside: Path) -> int:
    # -S bypasses sitecustomize: these denials must come from inherited kernel rules.
    probe = """import os,socket,sys
from pathlib import Path
outside=Path(sys.argv[1])
for action in (lambda: outside.read_text(),lambda: outside.write_text('synthetic-change'),lambda: socket.socket()):
 try: action()
 except PermissionError: pass
 else: raise AssertionError('native restriction missing')
print('NATIVE_CHILD_READ_WRITE_SOCKET_DENIED')
"""
    subprocess.run([sys.executable, "-B", "-S", "-c", probe, str(outside)], check=True)
    valid = """import os,sys
from pathlib import Path
work=Path(sys.argv[1]); p=work/'smoke'; p.mkdir()
d=os.open(p,os.O_RDONLY|os.O_DIRECTORY)
f=os.open('dir-fd.txt',os.O_WRONLY|os.O_CREAT|os.O_TRUNC,0o600,dir_fd=d)
os.close(f); os.close(d)
link=p/'interpreter-link';link.symlink_to(sys.executable);link.unlink()
from vcfcf_common import _env
(p/'.env').write_text('VCFCF_OFFLINE_SYNTHETIC=fixture_only\\n')
assert _env.load_dotenv(p)==p/'.env'
assert os.environ['VCFCF_OFFLINE_SYNTHETIC']=='fixture_only'
assert _env.load_dotenv(Path('/synthetic-not-scratch')) is None
print('DIR_FD_SYMLINK_AND_SYNTHETIC_DOTENV_PASS')
"""
    subprocess.run([sys.executable, "-B", "-c", valid, str(work)], check=True)
    print("OFFLINE_SMOKE_PASS (synthetic files only; source read-only prerequisite checked)", flush=True)
    return 0


def create_smoke_sentinel(path: Path):
    """Refuse collisions/symlinks; never overwrite another /tmp entry."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as sentinel:
        sentinel.write("artificial sentinel, no credentials")


def main(argv=None) -> int:
    args = arguments(argv)
    if os.environ.get("VCFCF_OFFLINE_ACTIVE") == "1":
        print("OFFLINE_RUNNER_REFUSED: already guarded; run the outer command only", file=sys.stderr)
        return 2
    try:
        if sys.platform != "linux":
            raise GuardUnavailable("Linux with Landlock and seccomp is required; no tests started")
        readonly_inputs(REPO, args.sdk_jar)
        work = Path(tempfile.mkdtemp(prefix="vcfcf-offline-", dir="/tmp"))
        for name in ("home", "tmp", "cache", "config", "data", "guard"):
            (work / name).mkdir(mode=0o700)
        shutil.copyfile(Path(__file__).with_name("sitecustomize.py"), work / "guard/sitecustomize.py")
        outside = work.with_name(work.name + "-synthetic-outside")
        if args.smoke:
            create_smoke_sentinel(outside)
        os.environ.clear()
        os.environ.update(environment(REPO, work, args.sdk_jar))
        os.chdir(REPO)
        abi = install_native_guard(REPO, work, args.sdk_jar)
        print(f"OFFLINE_NATIVE_GUARD Landlock_ABI={abi}; externally read-only inputs; scratch={work}; child networking denied", flush=True)
        if args.smoke:
            return smoke(work, outside)
        print("GUARDED_SUITE_WITH_EXCLUSION " + WHEEL_TEST, flush=True)
        print("WHEEL_PREREQUISITES " + wheel_prerequisites() + "; nothing installed", flush=True)
        command = pytest_argv(work, args.test)
        print("PYTEST_ARGV " + repr(command), flush=True)
        return subprocess.run(command).returncode
    except (GuardUnavailable, OSError, subprocess.CalledProcessError) as error:
        # Do not expose inputs, environment or exception payloads from subprocesses.
        message = str(error) if isinstance(error, GuardUnavailable) else "guard/smoke execution failed (" + type(error).__name__ + "); no successful run claimed"
        print("OFFLINE_RUNNER_BLOCKED: " + message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
