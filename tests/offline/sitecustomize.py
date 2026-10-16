"""Startup guard for the opt-in runner; native restrictions are installed first."""
import importlib.machinery
import os
from pathlib import Path
import sys

try:
    WORK = Path(os.environ["VCFCF_OFFLINE_WORK"]).resolve()
    GUARD = os.environ["VCFCF_OFFLINE_GUARD"]
    if not WORK.is_absolute() or Path(GUARD).resolve() != WORK / "guard":
        raise ValueError("invalid guard root")
except (KeyError, ValueError):
    os._exit(2)  # sitecustomize exceptions would otherwise be printed and ignored.


def audit(event, args):
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        raw = Path(os.fsdecode(args[0])).absolute()
        path = raw.resolve()
        sensitive = any(p in {".env", ".ssh", ".aws", ".password-store", ".netrc"} for p in (*raw.parts, *path.parts))
        if sensitive and not path.is_relative_to(WORK):
            raise PermissionError("OFFLINE_GUARD: real credential-file access refused")
        mode = args[1] if len(args) > 1 else "r"
        flags = args[2] if len(args) > 2 else 0
        writing = isinstance(mode, str) and any(m in mode for m in "wax+")
        writing = writing or (isinstance(flags, int) and bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)))
        if writing and Path(os.fsdecode(args[0])).is_absolute() and path != Path("/dev/null") and not path.is_relative_to(WORK):
            raise PermissionError("OFFLINE_GUARD: non-scratch write refused")
    if event in {"socket.connect", "socket.connect_ex", "socket.getaddrinfo", "socket.__new__"}:
        raise PermissionError("OFFLINE_GUARD: networking refused")
    if event == "subprocess.Popen":
        env = args[3]
        if env is not None:
            existing = env.get("PYTHONPATH", "")
            if GUARD not in existing.split(os.pathsep):
                env["PYTHONPATH"] = GUARD + (os.pathsep + existing if existing else "")
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["PYTHONNOUSERSITE"] = "1"
            env["VCFCF_OFFLINE_ACTIVE"] = "1"
            env["VCFCF_OFFLINE_WORK"] = str(WORK)
            env["VCFCF_OFFLINE_GUARD"] = GUARD
            env.setdefault("HOME", str(WORK / "home"))
            env.setdefault("TMPDIR", str(WORK / "tmp"))
            env["PIP_NO_INDEX"] = "1"
    if event in {"os.remove", "os.rmdir", "os.mkdir", "os.chmod"} and args and isinstance(args[0], (str, bytes, os.PathLike)):
        raw = Path(os.fsdecode(args[0]))
        if not raw.is_absolute():
            return  # Python omits dir_fd in some events; the kernel enforces it.
        path = raw.resolve() if event == "os.chmod" else raw.parent.resolve() / raw.name
        if not path.is_relative_to(WORK):
            raise PermissionError("OFFLINE_GUARD: non-scratch mutation refused")


sys.addaudithook(audit)


class GuardEnvLoader:
    def __init__(self, original):
        self.original = original

    def create_module(self, spec):
        return self.original.create_module(spec)

    def exec_module(self, module):
        self.original.exec_module(module)
        original = module.load_dotenv

        def fixture_only(start=None):
            here = Path(start or os.getcwd()).resolve()
            if not here.is_relative_to(WORK):
                return None
            # Preserve the real parser/idempotence for synthetic fixtures, but
            # never let its upward search escape this owned scratch directory.
            for candidate in (here, *here.parents):
                if not candidate.is_relative_to(WORK):
                    break
                if (candidate / ".env").is_file():
                    return original(start)
            module._LOADED = True
            return None

        module.load_dotenv = fixture_only


class GuardEnvFinder:
    def find_spec(self, fullname, path=None, target=None):
        if fullname != "vcfcf_common._env":
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
        if spec and spec.loader:
            spec.loader = GuardEnvLoader(spec.loader)
        return spec


sys.meta_path.insert(0, GuardEnvFinder())
