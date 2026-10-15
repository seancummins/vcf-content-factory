"""Structural comparison of two .pak files.

Compares a factory-built .pak against a reference MPB-built .pak and
reports structural divergences at three severity levels:

  BLOCKING  — differences that change adapter schema registration and
               will likely cause install failure or silent non-registration.
  WARNING   — differences in optional structural elements that may cause
               runtime issues (missing count metrics, wrong export.json shape).
  INFO      — cosmetic differences unlikely to affect install
               (display_name, vendor, icon format, version).

Usage (direct):
    from vcfcf_managementpacks.pak_compare import compare_paks, format_report
    findings = compare_paks(factory_pak_path, reference_pak_path)
    print(format_report(findings, factory_label, reference_label))

Wire format references:
  knowledge/context/mpb/wire_reference/vsphere_storage_paths_aria_ops_stitch.json
  knowledge/context/investigations/mpb_adapter_jar_reverse_engineering.md
"""
from __future__ import annotations

import io
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from xml.etree import ElementTree as ET

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

BLOCKING = "BLOCKING"
WARNING = "WARNING"
INFO = "INFO"

_SEVERITY_ORDER = {BLOCKING: 0, WARNING: 1, INFO: 2}


class Finding:
    """A single comparison finding."""

    def __init__(self, severity: str, code: str, message: str) -> None:
        self.severity = severity
        self.code = code
        self.message = message

    def __repr__(self) -> str:
        return f"Finding({self.severity}, {self.code!r}, {self.message!r})"


class CompareResult:
    """All findings from one factory-vs-reference comparison."""

    def __init__(
        self,
        factory_label: str,
        reference_label: str,
        findings: List[Finding],
        *, policy: str = "legacy", metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        self.factory_label = factory_label
        self.reference_label = reference_label
        self.findings = findings
        self.policy = policy
        self.metadata = metadata or {}

    def blocking(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == BLOCKING]

    def warnings(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == WARNING]

    def infos(self) -> List[Finding]:
        return [f for f in self.findings if f.severity == INFO]

    def score_summary(self) -> str:
        b, w, i = len(self.blocking()), len(self.warnings()), len(self.infos())
        return f"{b} BLOCKING, {w} WARNING, {i} INFO"


# ---------------------------------------------------------------------------
# PAK reading helpers
# ---------------------------------------------------------------------------

def _read_pak_inventory(pak_path: Path) -> Set[str]:
    """Return the set of names in the top-level .pak zip."""
    with zipfile.ZipFile(pak_path, "r") as zf:
        return {info.filename for info in zf.infolist() if not info.is_dir()}


def _read_from_pak(pak_path: Path, member: str) -> Optional[bytes]:
    """Read a member from the .pak zip; return None if absent."""
    try:
        with zipfile.ZipFile(pak_path, "r") as zf:
            try:
                return zf.read(member)
            except KeyError:
                return None
    except (zipfile.BadZipFile, OSError):
        return None


def _read_adapters_zip(pak_path: Path) -> Optional[bytes]:
    """Extract adapters.zip bytes from the pak."""
    return _read_from_pak(pak_path, "adapters.zip")


def _read_adapters_zip_inventory(adapters_zip_bytes: Optional[bytes]) -> Set[str]:
    """Return the set of non-directory members in adapters.zip."""
    if not adapters_zip_bytes:
        return set()
    try:
        buf = io.BytesIO(adapters_zip_bytes)
        with zipfile.ZipFile(buf, "r") as zf:
            return {info.filename for info in zf.infolist() if not info.is_dir()}
    except (zipfile.BadZipFile, Exception):
        return set()


def _read_from_adapters_zip(adapters_zip_bytes: Optional[bytes], member: str) -> Optional[bytes]:
    """Read a member from the in-memory adapters.zip; return None if absent."""
    if not adapters_zip_bytes:
        return None
    try:
        buf = io.BytesIO(adapters_zip_bytes)
        with zipfile.ZipFile(buf, "r") as zf:
            try:
                return zf.read(member)
            except KeyError:
                return None
    except (zipfile.BadZipFile, Exception):
        return None


def _detect_adapter_dir(adapters_inventory: Set[str]) -> Optional[str]:
    """Infer the adapter directory name from the adapters.zip member list.

    Tier 1 (MPB) paks use a '<something>_adapter3/' top-level directory.
    Tier 2 (SDK) paks use a '<adapterkind>/' top-level directory that does NOT
    end in '_adapter3', but always contains '<adapterkind>/conf/describe.xml'.

    Detection order:
      1. Look for any top-level dir prefix ending in '_adapter3'  (Tier 1).
      2. Look for any entry of the form '<name>/conf/describe.xml'  (Tier 2).
    """
    # --- Tier 1: MPB adapter3 layout ---
    candidates: Set[str] = set()
    for name in adapters_inventory:
        parts = name.split("/")
        if len(parts) >= 2 and parts[0].endswith("_adapter3"):
            candidates.add(parts[0])
    if candidates:
        # If there's only one, return it.  If multiple, pick shortest (most likely base).
        return sorted(candidates, key=len)[0]

    # --- Tier 2: SDK adapter layout — find '<adapterkind>/conf/describe.xml' ---
    sdk_candidates: Set[str] = set()
    for name in adapters_inventory:
        parts = name.split("/")
        # Expecting exactly '<adapterkind>/conf/describe.xml' (3 parts, no trailing /)
        if len(parts) == 3 and parts[1] == "conf" and parts[2] == "describe.xml":
            sdk_candidates.add(parts[0])
    if sdk_candidates:
        return sorted(sdk_candidates, key=len)[0]

    return None


# ---------------------------------------------------------------------------
# Manifest comparison
# ---------------------------------------------------------------------------

_MANIFEST_COSMETIC_FIELDS = {
    "display_name", "name", "description", "vendor", "pak_icon",
}

_MANIFEST_VERSION_FIELDS = {"version", "vcops_minimum_version"}

_MANIFEST_SCRIPT_FIELDS = {
    "pak_validation_script", "adapter_pre_script", "adapter_post_script",
}

_MANIFEST_STRUCTURAL_FIELDS = {
    "license_type", "adapter_kinds", "adapters", "run_scripts_on_all_nodes",
    "platform", "disk_space_required", "eula_file",
}


def _compare_manifest(
    factory_bytes: Optional[bytes],
    ref_bytes: Optional[bytes],
    findings: List[Finding],
) -> None:
    if not factory_bytes:
        findings.append(Finding(BLOCKING, "M0", "manifest.txt: factory pak has no manifest.txt"))
        return
    if not ref_bytes:
        findings.append(Finding(INFO, "M0R", "manifest.txt: reference pak has no manifest.txt (cannot compare)"))
        return

    try:
        fm = json.loads(factory_bytes.decode("utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        findings.append(Finding(BLOCKING, "M0P", f"manifest.txt: factory manifest.txt is not valid JSON: {e}"))
        return
    try:
        rm = json.loads(ref_bytes.decode("utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        findings.append(Finding(INFO, "M0RP", f"manifest.txt: reference manifest.txt is not valid JSON: {e}"))
        return

    # --- Script fields (BLOCKING if factory has script path and reference has empty/absent) ---
    for field in sorted(_MANIFEST_SCRIPT_FIELDS):
        fv = fm.get(field)
        rv = rm.get(field)
        # Normalise: {"script": ""} and "" and absent all mean "no script"
        fv_script = (fv or {}).get("script", "") if isinstance(fv, dict) else (fv or "")
        rv_script = (rv or {}).get("script", "") if isinstance(rv, dict) else (rv or "")
        if bool(fv_script) != bool(rv_script):
            f_desc = f'"{fv_script}"' if fv_script else '(empty/absent)'
            r_desc = f'"{rv_script}"' if rv_script else '(empty/absent)'
            findings.append(Finding(
                BLOCKING, "M1",
                f"manifest.txt: {field}: factory={f_desc}, reference={r_desc}"
            ))

    # --- license_type format ---
    fv_lic = fm.get("license_type", "")
    rv_lic = rm.get("license_type", "")
    if fv_lic and rv_lic:
        f_has_adapter_prefix = fv_lic.startswith("adapter:")
        r_has_adapter_prefix = rv_lic.startswith("adapter:")
        if f_has_adapter_prefix != r_has_adapter_prefix:
            findings.append(Finding(
                BLOCKING, "M2",
                f"manifest.txt: license_type format differs: factory={fv_lic!r}, reference={rv_lic!r}"
            ))

    # --- adapter_kinds structure ---
    fv_ak = fm.get("adapter_kinds", [])
    rv_ak = rm.get("adapter_kinds", [])
    if not isinstance(fv_ak, list) or len(fv_ak) == 0:
        findings.append(Finding(BLOCKING, "M3", "manifest.txt: factory adapter_kinds is empty or not a list"))
    if isinstance(fv_ak, list) and isinstance(rv_ak, list):
        if len(fv_ak) != len(rv_ak):
            findings.append(Finding(
                WARNING, "M4",
                f"manifest.txt: adapter_kinds count differs: factory={len(fv_ak)}, reference={len(rv_ak)}"
            ))

    # --- run_scripts_on_all_nodes ---
    fv_rsoan = fm.get("run_scripts_on_all_nodes")
    rv_rsoan = rm.get("run_scripts_on_all_nodes")
    if fv_rsoan is not None and rv_rsoan is not None and str(fv_rsoan) != str(rv_rsoan):
        findings.append(Finding(
            WARNING, "M5",
            f"manifest.txt: run_scripts_on_all_nodes differs: factory={fv_rsoan!r}, reference={rv_rsoan!r}"
        ))

    # --- platform list ---
    fv_plat = sorted(fm.get("platform", []))
    rv_plat = sorted(rm.get("platform", []))
    if fv_plat != rv_plat:
        findings.append(Finding(
            WARNING, "M6",
            f"manifest.txt: platform list differs: factory={fv_plat}, reference={rv_plat}"
        ))

    # --- Cosmetic fields ---
    for field in sorted(_MANIFEST_COSMETIC_FIELDS):
        fv = fm.get(field)
        rv = rm.get(field)
        if fv != rv:
            findings.append(Finding(
                INFO, "M7",
                f"manifest.txt: {field} differs: factory={fv!r}, reference={rv!r}"
            ))

    # --- pak_icon format (svg vs png) ---
    fv_icon = fm.get("pak_icon", "")
    rv_icon = rm.get("pak_icon", "")
    if fv_icon and rv_icon and fv_icon != rv_icon:
        f_ext = Path(fv_icon).suffix
        r_ext = Path(rv_icon).suffix
        if f_ext != r_ext:
            findings.append(Finding(
                INFO, "M8",
                f"manifest.txt: pak_icon format differs: factory={fv_icon!r} ({f_ext}), reference={rv_icon!r} ({r_ext})"
            ))


# ---------------------------------------------------------------------------
# Pak-level file inventory comparison
# ---------------------------------------------------------------------------

# Files whose absence is BLOCKING for pak installs.
_PAK_BLOCKING_FILES = {
    "manifest.txt", "adapters.zip", "eula.txt",
}

# Files that are important but not mandatory for install.
_PAK_WARNING_FILES = {
    "post-install.py", "validate.py", "preAdapters.py",
}


def _compare_pak_inventory(
    factory_inv: Set[str],
    ref_inv: Set[str],
    findings: List[Finding],
) -> None:
    """Compare top-level pak file inventories."""
    factory_only = factory_inv - ref_inv
    ref_only = ref_inv - factory_inv

    for name in sorted(factory_only):
        if name in _PAK_BLOCKING_FILES:
            sev = BLOCKING
        elif name in _PAK_WARNING_FILES:
            sev = WARNING
        else:
            sev = INFO
        findings.append(Finding(sev, "I1", f"pak inventory: {name!r} present in factory, absent from reference"))

    for name in sorted(ref_only):
        if name in _PAK_BLOCKING_FILES:
            sev = BLOCKING
        elif name in _PAK_WARNING_FILES:
            sev = WARNING
        else:
            sev = INFO
        findings.append(Finding(sev, "I2", f"pak inventory: {name!r} present in reference, absent from factory"))


# ---------------------------------------------------------------------------
# adapters.zip inventory comparison
# ---------------------------------------------------------------------------

# Adapter-relative paths (without adapter dir prefix) whose presence is BLOCKING.
_ADAPTERS_BLOCKING_RELATIVE = {
    "conf/describe.xml",
    "conf/export.json",
    "conf/template.json",
}

# Adapter-relative paths that are WARNING if absent.
_ADAPTERS_WARNING_RELATIVE = {
    "conf/resources/resources.properties",
}

# Adapter-relative subdirectory presence (inferred from members) — WARNING if absent.
_ADAPTERS_CONTENT_DIRS = {
    "conf/dashboards",
    "conf/views",
    "conf/supermetrics",
    "conf/reports",
    "conf/images",
}


def _normalise_adapter_inventory(inv: Set[str], adapter_dir: Optional[str]) -> Set[str]:
    """Strip the adapter_dir prefix from all paths, returning relative paths."""
    if not adapter_dir:
        return inv
    prefix = adapter_dir + "/"
    result: Set[str] = set()
    for name in inv:
        if name.startswith(prefix):
            result.add(name[len(prefix):])
        else:
            result.add(name)
    return result


def _compare_adapters_inventory(
    factory_inv: Set[str],
    ref_inv: Set[str],
    factory_adapter_dir: Optional[str],
    ref_adapter_dir: Optional[str],
    findings: List[Finding],
) -> None:
    """Compare adapters.zip inventories (normalised to adapter-relative paths)."""
    f_norm = _normalise_adapter_inventory(factory_inv, factory_adapter_dir)
    r_norm = _normalise_adapter_inventory(ref_inv, ref_adapter_dir)

    factory_only = f_norm - r_norm
    ref_only = r_norm - f_norm

    for name in sorted(factory_only):
        sev = BLOCKING if name in _ADAPTERS_BLOCKING_RELATIVE else (
            WARNING if name in _ADAPTERS_WARNING_RELATIVE else INFO
        )
        findings.append(Finding(sev, "A1", f"adapters.zip: {name!r} present in factory, absent from reference"))

    for name in sorted(ref_only):
        sev = BLOCKING if name in _ADAPTERS_BLOCKING_RELATIVE else (
            WARNING if name in _ADAPTERS_WARNING_RELATIVE else INFO
        )
        findings.append(Finding(sev, "A2", f"adapters.zip: {name!r} present in reference, absent from factory"))

    # Check for content subdirectory presence (by dir prefix)
    def _has_dir(inv_norm: Set[str], dir_prefix: str) -> bool:
        return any(p.startswith(dir_prefix + "/") or p == dir_prefix for p in inv_norm)

    for content_dir in sorted(_ADAPTERS_CONTENT_DIRS):
        f_has = _has_dir(f_norm, content_dir)
        r_has = _has_dir(r_norm, content_dir)
        if not f_has and r_has:
            findings.append(Finding(
                INFO, "A3",
                f"adapters.zip: directory {content_dir!r} present in reference, absent from factory"
            ))
        elif f_has and not r_has:
            findings.append(Finding(
                INFO, "A4",
                f"adapters.zip: directory {content_dir!r} present in factory, absent from reference"
            ))


# ---------------------------------------------------------------------------
# describe.xml comparison
# ---------------------------------------------------------------------------

def _parse_describe_xml(data: Optional[bytes]) -> Optional[ET.Element]:
    """Parse describe.xml bytes; return root element or None on failure."""
    if not data:
        return None
    try:
        # Strip namespace for simpler querying
        xml_str = data.decode("utf-8", errors="replace")
        # Remove namespace declarations to simplify ElementTree queries
        xml_str = xml_str.replace(
            ' xmlns="http://schemas.vmware.com/vcops/schema"', ""
        )
        return ET.fromstring(xml_str)
    except ET.ParseError:
        return None


def _describe_credential_kinds_info(root: ET.Element) -> Dict[str, Any]:
    """Extract structural info about CredentialKinds block."""
    ck_block = root.find("CredentialKinds")
    if ck_block is None:
        return {"has_block": False, "credential_kinds": 0, "total_fields": 0}
    cks = ck_block.findall("CredentialKind")
    total_fields = sum(len(ck.findall("CredentialField")) for ck in cks)
    return {
        "has_block": True,
        "credential_kinds": len(cks),
        "total_fields": total_fields,
    }


def _describe_resource_kinds_summary(root: ET.Element) -> Dict[str, Any]:
    """Summarise all ResourceKind elements."""
    rks_block = root.find("ResourceKinds")
    if rks_block is None:
        return {}
    result: Dict[str, Any] = {}
    for rk in rks_block.findall("ResourceKind"):
        key = rk.get("key", "<no-key>")
        rk_type = rk.get("type")
        sub_type = rk.get("subType")
        cred_kind = rk.get("credentialKind")
        dynamic = rk.get("dynamic")
        show_tag = rk.get("showTag")

        idents = rk.findall("ResourceIdentifier")
        groups = rk.findall("ResourceGroup")
        attrs = rk.findall("ResourceAttribute")

        # ResourceGroup keys
        group_keys = [g.get("key", "") for g in groups]
        has_summary_group = "summary" in group_keys
        has_relationships_group = "relationships" in group_keys

        # Count all ResourceAttributes within ResourceGroups
        group_attrs: List[ET.Element] = []
        for g in groups:
            group_attrs.extend(g.findall("ResourceAttribute"))

        # ComputedMetrics
        cm_block = rk.find("ComputedMetrics")
        computed_metrics = len(cm_block.findall("ComputedMetric")) if cm_block is not None else 0

        result[key] = {
            "type": rk_type,
            "subType": sub_type,
            "credentialKind": cred_kind,
            "dynamic": dynamic,
            "showTag": show_tag,
            "identifier_count": len(idents),
            "identifier_keys": [i.get("key", "") for i in idents],
            "group_keys": group_keys,
            "has_summary_group": has_summary_group,
            "has_relationships_group": has_relationships_group,
            "direct_attrs": len(attrs),
            "group_attrs": len(group_attrs),
            "computed_metrics": computed_metrics,
        }
    return result


def _get_suffix_normalised_rks(
    rks: Dict[str, Any], adapter_dir: Optional[str]
) -> Dict[str, Any]:
    """Return a copy of rks with adapter-kind-specific prefixes stripped.

    Maps '<ak>_relatives' -> '_relatives', '<ak>_world' -> '_world',
    '<ak>' -> '_adapter_instance', and any other key to its suffix
    after the adapter kind prefix (e.g. '<ak>_volume' -> '_volume').

    This lets us compare structural patterns between paks with
    different adapter kinds.
    """
    if not adapter_dir:
        return rks
    # adapter_dir is like "mpb_synology_nas_adapter3"; ak = adapter_dir[:-len("_adapter3")]
    if adapter_dir.endswith("_adapter3"):
        ak = adapter_dir[: -len("_adapter3")]
    else:
        # Infer ak from rk keys (longest common prefix)
        ak_candidates = [k for k in rks if not k.endswith("_relatives") and not k.endswith("_world")]
        if not ak_candidates:
            return rks
        # The adapter instance kind key == ak itself
        # It has type="7" and a credentialKind attribute
        for k, v in rks.items():
            if v.get("type") == "7":
                ak = k
                break
        else:
            ak = ""

    result: Dict[str, Any] = {}
    for key, info in rks.items():
        if key == ak:
            norm_key = "_adapter_instance"
        elif key == f"{ak}_relatives":
            norm_key = "_relatives"
        elif key == f"{ak}_world":
            norm_key = "_world"
        elif key.startswith(f"{ak}_"):
            norm_key = key[len(ak):]  # e.g. "_volume"
        else:
            norm_key = key
        result[norm_key] = info
    return result


def _compare_describe_xml(
    factory_bytes: Optional[bytes],
    ref_bytes: Optional[bytes],
    factory_adapter_dir: Optional[str],
    ref_adapter_dir: Optional[str],
    findings: List[Finding],
) -> None:
    if not factory_bytes:
        findings.append(Finding(BLOCKING, "D0", "describe.xml: factory has no describe.xml"))
        return
    if not ref_bytes:
        findings.append(Finding(INFO, "D0R", "describe.xml: reference has no describe.xml (cannot compare)"))
        return

    f_root = _parse_describe_xml(factory_bytes)
    r_root = _parse_describe_xml(ref_bytes)

    if f_root is None:
        findings.append(Finding(BLOCKING, "D0P", "describe.xml: factory describe.xml failed to parse"))
        return
    if r_root is None:
        findings.append(Finding(INFO, "D0RP", "describe.xml: reference describe.xml failed to parse (cannot compare)"))
        return

    # CredentialKinds comparison
    f_creds = _describe_credential_kinds_info(f_root)
    r_creds = _describe_credential_kinds_info(r_root)

    if f_creds["has_block"] != r_creds["has_block"]:
        f_desc = "has <CredentialKinds>" if f_creds["has_block"] else "has no <CredentialKinds>"
        r_desc = "has <CredentialKinds>" if r_creds["has_block"] else "has no <CredentialKinds>"
        findings.append(Finding(
            BLOCKING, "D1",
            f"describe.xml: CredentialKinds presence: factory {f_desc}, reference {r_desc}"
        ))
    elif f_creds["has_block"] and r_creds["has_block"]:
        if f_creds["credential_kinds"] != r_creds["credential_kinds"]:
            findings.append(Finding(
                BLOCKING, "D2",
                f"describe.xml: CredentialKind count: factory={f_creds['credential_kinds']}, "
                f"reference={r_creds['credential_kinds']}"
            ))
        if f_creds["total_fields"] != r_creds["total_fields"]:
            findings.append(Finding(
                WARNING, "D3",
                f"describe.xml: total CredentialField count: factory={f_creds['total_fields']}, "
                f"reference={r_creds['total_fields']}"
            ))

    # ResourceKinds structural comparison (normalised)
    f_rks = _describe_resource_kinds_summary(f_root)
    r_rks = _describe_resource_kinds_summary(r_root)
    f_norm = _get_suffix_normalised_rks(f_rks, factory_adapter_dir)
    r_norm = _get_suffix_normalised_rks(r_rks, ref_adapter_dir)

    # Check for mandatory structural kinds
    for kind_suffix, kind_label in [
        ("_adapter_instance", "adapter instance kind (type=7)"),
        ("_relatives", "_relatives kind (type=4)"),
        ("_world", "_world kind (type=8)"),
    ]:
        f_has = kind_suffix in f_norm
        r_has = kind_suffix in r_norm
        if f_has and not r_has:
            findings.append(Finding(INFO, "D4", f"describe.xml: {kind_label} present in factory, absent from reference"))
        elif not f_has and r_has:
            findings.append(Finding(BLOCKING, "D5", f"describe.xml: {kind_label} absent from factory, present in reference"))

    # Adapter instance kind structural checks
    if "_adapter_instance" in f_norm and "_adapter_instance" in r_norm:
        fi = f_norm["_adapter_instance"]
        ri = r_norm["_adapter_instance"]

        # credentialKind attribute
        if bool(fi.get("credentialKind")) != bool(ri.get("credentialKind")):
            f_desc = f'credentialKind="{fi["credentialKind"]}"' if fi.get("credentialKind") else "no credentialKind attr"
            r_desc = f'credentialKind="{ri["credentialKind"]}"' if ri.get("credentialKind") else "no credentialKind attr"
            findings.append(Finding(
                BLOCKING, "D6",
                f"describe.xml: adapter instance (type=7): factory {f_desc}, reference {r_desc}"
            ))

        # summary ResourceGroup presence
        if fi["has_summary_group"] != ri["has_summary_group"]:
            f_desc = "has <ResourceGroup key='summary'>" if fi["has_summary_group"] else "no summary group"
            r_desc = "has <ResourceGroup key='summary'>" if ri["has_summary_group"] else "no summary group"
            findings.append(Finding(
                WARNING, "D7",
                f"describe.xml: adapter instance: factory {f_desc}, reference {r_desc}"
            ))

        # ResourceIdentifier count
        if fi["identifier_count"] != ri["identifier_count"]:
            findings.append(Finding(
                WARNING, "D8",
                f"describe.xml: adapter instance identifier count: factory={fi['identifier_count']}, "
                f"reference={ri['identifier_count']}"
            ))

        # Check for mandatory mpb_ identifiers
        f_ident_keys = set(fi["identifier_keys"])
        r_ident_keys = set(ri["identifier_keys"])
        mpb_idents = {
            "mpb_hostname", "mpb_port", "mpb_connection_timeout",
            "mpb_concurrent_requests", "mpb_max_retries", "mpb_ssl_config",
            "mpb_min_event_severity", "support_autodiscovery",
        }
        f_missing_mpb = mpb_idents - f_ident_keys
        r_has_mpb = bool(mpb_idents & r_ident_keys)
        if f_missing_mpb and r_has_mpb:
            findings.append(Finding(
                BLOCKING, "D9",
                f"describe.xml: adapter instance missing mpb_ identifiers: {sorted(f_missing_mpb)}"
            ))

    # _relatives kind structural checks
    if "_relatives" in f_norm and "_relatives" in r_norm:
        fi = f_norm["_relatives"]
        ri = r_norm["_relatives"]

        if fi.get("type") != ri.get("type"):
            findings.append(Finding(
                BLOCKING, "D10",
                f"describe.xml: _relatives: type attr: factory={fi.get('type')!r}, reference={ri.get('type')!r}"
            ))

        if fi.get("dynamic") != ri.get("dynamic"):
            findings.append(Finding(
                WARNING, "D11",
                f"describe.xml: _relatives: dynamic attr: factory={fi.get('dynamic')!r}, reference={ri.get('dynamic')!r}"
            ))

        # ResourceAttributes in _relatives group
        if fi["group_attrs"] != ri["group_attrs"]:
            findings.append(Finding(
                WARNING, "D12",
                f"describe.xml: _relatives group attributes: factory={fi['group_attrs']}, reference={ri['group_attrs']}"
            ))

    # _world kind structural checks
    if "_world" in f_norm and "_world" in r_norm:
        fi = f_norm["_world"]
        ri = r_norm["_world"]

        if fi.get("type") != "8":
            findings.append(Finding(
                BLOCKING, "D13",
                f"describe.xml: _world kind: factory type={fi.get('type')!r}, expected '8'"
            ))
        if fi.get("subType") != ri.get("subType"):
            findings.append(Finding(
                BLOCKING, "D14",
                f"describe.xml: _world kind subType: factory={fi.get('subType')!r}, reference={ri.get('subType')!r}"
            ))
        if fi["has_summary_group"] != ri["has_summary_group"]:
            f_desc = "has summary group" if fi["has_summary_group"] else "no summary group"
            r_desc = "has summary group" if ri["has_summary_group"] else "no summary group"
            findings.append(Finding(
                WARNING, "D15",
                f"describe.xml: _world kind: factory {f_desc}, reference {r_desc}"
            ))
        if bool(fi["computed_metrics"]) != bool(ri["computed_metrics"]):
            f_desc = f"{fi['computed_metrics']} ComputedMetric(s)" if fi["computed_metrics"] else "no ComputedMetrics"
            r_desc = f"{ri['computed_metrics']} ComputedMetric(s)" if ri["computed_metrics"] else "no ComputedMetrics"
            findings.append(Finding(
                WARNING, "D16",
                f"describe.xml: _world kind: factory {f_desc}, reference {r_desc}"
            ))

    # Data kinds (all except adapter_instance, _relatives, _world) structural patterns
    structural_keys = {"_adapter_instance", "_relatives", "_world"}
    f_data_keys = {k for k in f_norm if k not in structural_keys}
    r_data_keys = {k for k in r_norm if k not in structural_keys}

    if len(f_data_keys) != len(r_data_keys):
        findings.append(Finding(
            INFO, "D17",
            f"describe.xml: data kind count: factory={len(f_data_keys)}, reference={len(r_data_keys)}"
        ))

    # Check structural patterns on common normalised data kinds
    for k in sorted(f_data_keys & r_data_keys):
        fi = f_norm[k]
        ri = r_norm[k]

        # adapter_instance_id as first identifier
        f_has_ai_id = "adapter_instance_id" in fi["identifier_keys"]
        r_has_ai_id = "adapter_instance_id" in ri["identifier_keys"]
        if f_has_ai_id != r_has_ai_id:
            f_desc = "has adapter_instance_id" if f_has_ai_id else "no adapter_instance_id"
            r_desc = "has adapter_instance_id" if r_has_ai_id else "no adapter_instance_id"
            findings.append(Finding(
                BLOCKING, "D18",
                f"describe.xml: data kind {k}: factory {f_desc}, reference {r_desc}"
            ))

        # relationships group
        if fi["has_relationships_group"] != ri["has_relationships_group"]:
            f_desc = "has relationships group" if fi["has_relationships_group"] else "no relationships group"
            r_desc = "has relationships group" if ri["has_relationships_group"] else "no relationships group"
            findings.append(Finding(
                WARNING, "D19",
                f"describe.xml: data kind {k}: factory {f_desc}, reference {r_desc}"
            ))

        # group attributes count (WARNING if divergent)
        if fi["group_attrs"] != ri["group_attrs"]:
            findings.append(Finding(
                WARNING, "D20",
                f"describe.xml: data kind {k}: group attribute count: factory={fi['group_attrs']}, reference={ri['group_attrs']}"
            ))

        # summary group presence on data kinds (WARNING if factory is missing it).
        #
        # Invariant (2026-05-18): every data ResourceKind MUST have all metric/
        # property ResourceAttributes inside a <ResourceGroup key="summary">.
        # Bare ResourceAttributes directly under <ResourceKind> cause
        # "Adapter install failed" at apply_adapter on VCF Operations 9.1.
        # This check fires as WARNING D27 when the factory pak is missing the
        # summary group that the reference pak has, flagging potential regressions.
        if ri["has_summary_group"] and not fi["has_summary_group"]:
            findings.append(Finding(
                WARNING, "D27",
                f"describe.xml: data kind {k}: reference has <ResourceGroup key='summary'>, factory does not — "
                f"bare ResourceAttributes outside a summary group cause apply_adapter failures on VCF Ops 9.1+"
            ))

    # Discoveries block
    f_disc = root_find_first(f_root, "Discoveries")
    r_disc = root_find_first(r_root, "Discoveries")
    if f_disc is not None and r_disc is not None:
        f_disc_count = len(f_disc.findall("Discovery"))
        r_disc_count = len(r_disc.findall("Discovery"))
        if f_disc_count != r_disc_count:
            findings.append(Finding(
                WARNING, "D21",
                f"describe.xml: Discovery count: factory={f_disc_count}, reference={r_disc_count}"
            ))
        # Key format check (MPB uses <ak>_manual_discovery pattern)
        for d in f_disc.findall("Discovery"):
            key = d.get("key", "")
            if key and not key.endswith("_manual_discovery"):
                findings.append(Finding(
                    WARNING, "D22",
                    f"describe.xml: Discovery key={key!r} does not follow <ak>_manual_discovery pattern"
                ))

    # TraversalSpecKinds
    f_tsk = root_find_first(f_root, "TraversalSpecKinds")
    r_tsk = root_find_first(r_root, "TraversalSpecKinds")
    f_tsk_count = len(f_tsk.findall("TraversalSpecKind")) if f_tsk is not None else 0
    r_tsk_count = len(r_tsk.findall("TraversalSpecKind")) if r_tsk is not None else 0
    if f_tsk_count != r_tsk_count:
        findings.append(Finding(
            WARNING, "D23",
            f"describe.xml: TraversalSpecKind count: factory={f_tsk_count}, reference={r_tsk_count}"
        ))
    if f_tsk_count > 0 and r_tsk_count == 0:
        findings.append(Finding(
            INFO, "D24",
            "describe.xml: factory has TraversalSpecKinds, reference has empty block"
        ))
    elif f_tsk_count == 0 and r_tsk_count > 0:
        findings.append(Finding(
            WARNING, "D25",
            "describe.xml: factory has empty TraversalSpecKinds, reference has entries"
        ))

    # LicenseConfig
    f_lic = root_find_first(f_root, "LicenseConfig")
    r_lic = root_find_first(r_root, "LicenseConfig")
    f_lic_enabled = f_lic.get("enabled") if f_lic is not None else None
    r_lic_enabled = r_lic.get("enabled") if r_lic is not None else None
    if f_lic_enabled != r_lic_enabled:
        findings.append(Finding(
            INFO, "D26",
            f"describe.xml: LicenseConfig enabled: factory={f_lic_enabled!r}, reference={r_lic_enabled!r}"
        ))

    # UnitDefinitions
    f_ud = root_find_first(f_root, "UnitDefinitions")
    r_ud = root_find_first(r_root, "UnitDefinitions")
    if (f_ud is None) != (r_ud is None):
        f_desc = "has UnitDefinitions" if f_ud is not None else "no UnitDefinitions"
        r_desc = "has UnitDefinitions" if r_ud is not None else "no UnitDefinitions"
        findings.append(Finding(
            WARNING, "D27",
            f"describe.xml: {f_desc} vs {r_desc}"
        ))
    elif f_ud is not None and r_ud is not None:
        f_ut_count = len(f_ud.findall("UnitType"))
        r_ut_count = len(r_ud.findall("UnitType"))
        if f_ut_count != r_ut_count:
            findings.append(Finding(
                WARNING, "D28",
                f"describe.xml: UnitType count: factory={f_ut_count}, reference={r_ut_count}"
            ))


def root_find_first(root: ET.Element, tag: str) -> Optional[ET.Element]:
    """Find a child element by tag, tolerating namespace prefixes."""
    el = root.find(tag)
    if el is not None:
        return el
    # Try with namespace stripped variant (should already be handled, but be safe)
    for child in root:
        if child.tag == tag or child.tag.endswith("}" + tag):
            return child
    return None


# ---------------------------------------------------------------------------
# export.json comparison
# ---------------------------------------------------------------------------

def _obj_type_distribution(objects: List[Dict]) -> Dict[str, int]:
    dist: Dict[str, int] = {}
    for obj in objects:
        ot = obj.get("objectType", obj.get("type", "UNKNOWN"))
        dist[ot] = dist.get(ot, 0) + 1
    return dist


def _compare_export_json(
    factory_bytes: Optional[bytes],
    ref_bytes: Optional[bytes],
    findings: List[Finding],
) -> None:
    if not factory_bytes and not ref_bytes:
        return
    if not factory_bytes:
        findings.append(Finding(BLOCKING, "E0", "export.json: factory has no export.json"))
        return
    if not ref_bytes:
        findings.append(Finding(WARNING, "E0R", "export.json: reference has no export.json (cannot compare structure)"))
        return

    try:
        fe = json.loads(factory_bytes.decode("utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        findings.append(Finding(BLOCKING, "E0P", f"export.json: factory export.json is not valid JSON: {e}"))
        return
    try:
        re_ = json.loads(ref_bytes.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        findings.append(Finding(INFO, "E0RP", "export.json: reference export.json failed to parse (cannot compare)"))
        return

    # Top-level keys
    f_keys = set(fe.keys())
    r_keys = set(re_.keys())
    missing = r_keys - f_keys
    extra = f_keys - r_keys
    if missing:
        findings.append(Finding(
            BLOCKING, "E1",
            f"export.json: factory missing top-level keys: {sorted(missing)}"
        ))
    if extra:
        findings.append(Finding(
            INFO, "E2",
            f"export.json: factory has extra top-level keys not in reference: {sorted(extra)}"
        ))

    # source.source structure
    f_src = _nested_get(fe, "source", "source") or {}
    r_src = _nested_get(re_, "source", "source") or {}

    # credentialType
    f_ct = f_src.get("credentialType")
    r_ct = r_src.get("credentialType")
    if f_ct != r_ct:
        findings.append(Finding(
            WARNING, "E3",
            f"export.json: source.source.credentialType: factory={f_ct!r}, reference={r_ct!r}"
        ))

    # configuration keys — entries may be dicts or strings depending on pak version
    def _conf_key(c: Any) -> str:
        if isinstance(c, dict):
            return c.get("key", c.get("id", "")) or ""
        return str(c) if c else ""

    f_conf_keys = {_conf_key(c) for c in (f_src.get("configuration") or [])} - {""}
    r_conf_keys = {_conf_key(c) for c in (r_src.get("configuration") or [])} - {""}
    if f_conf_keys != r_conf_keys:
        missing_conf = r_conf_keys - f_conf_keys
        extra_conf = f_conf_keys - r_conf_keys
        if missing_conf:
            findings.append(Finding(
                WARNING, "E4",
                f"export.json: source.source.configuration keys missing from factory: {sorted(missing_conf)}"
            ))
        if extra_conf:
            findings.append(Finding(
                INFO, "E5",
                f"export.json: source.source.configuration extra keys in factory: {sorted(extra_conf)}"
            ))

    # sessionSettings
    f_ss = f_src.get("sessionSettings", "__absent__")
    r_ss = r_src.get("sessionSettings", "__absent__")
    f_ss_present = f_ss != "__absent__"
    r_ss_present = r_ss != "__absent__"
    if f_ss_present != r_ss_present:
        f_desc = f"sessionSettings={f_ss!r}" if f_ss_present else "no sessionSettings"
        r_desc = f"sessionSettings={r_ss!r}" if r_ss_present else "no sessionSettings"
        findings.append(Finding(
            WARNING, "E6",
            f"export.json: source.source: factory {f_desc}, reference {r_desc}"
        ))

    # Objects list
    f_objs = fe.get("objects") or []
    r_objs = re_.get("objects") or []
    if len(f_objs) != len(r_objs):
        findings.append(Finding(
            INFO, "E7",
            f"export.json: object count: factory={len(f_objs)}, reference={len(r_objs)}"
        ))

    # Object type distribution
    f_dist = _obj_type_distribution(f_objs)
    r_dist = _obj_type_distribution(r_objs)
    if f_dist != r_dist:
        findings.append(Finding(
            INFO, "E8",
            f"export.json: object type distribution: factory={f_dist}, reference={r_dist}"
        ))

    # Per-object structural patterns (check first object of each type)
    f_by_type: Dict[str, List[Dict]] = {}
    for obj in f_objs:
        ot = obj.get("objectType", obj.get("type", "UNKNOWN"))
        f_by_type.setdefault(ot, []).append(obj)
    r_by_type: Dict[str, List[Dict]] = {}
    for obj in r_objs:
        ot = obj.get("objectType", obj.get("type", "UNKNOWN"))
        r_by_type.setdefault(ot, []).append(obj)

    for ot in sorted(set(f_by_type.keys()) & set(r_by_type.keys())):
        fo = f_by_type[ot][0]
        ro = r_by_type[ot][0]
        _compare_export_object(fo, ro, ot, findings)

    # content field
    f_content = fe.get("content", "__absent__")
    r_content = re_.get("content", "__absent__")
    if f_content == "__absent__" and r_content != "__absent__":
        findings.append(Finding(
            WARNING, "E9",
            f"export.json: factory missing 'content' key (reference has it: type={type(r_content).__name__})"
        ))
    elif f_content != "__absent__" and r_content == "__absent__":
        findings.append(Finding(
            INFO, "E10",
            f"export.json: factory has 'content' key (reference does not); type={type(f_content).__name__}"
        ))
    elif f_content != "__absent__" and r_content != "__absent__":
        f_content_type = type(f_content).__name__
        r_content_type = type(r_content).__name__
        if f_content_type != r_content_type:
            findings.append(Finding(
                WARNING, "E11",
                f"export.json: content field type: factory={f_content_type}, reference={r_content_type}"
            ))

    # Events
    f_events = fe.get("events", []) or []
    r_events = re_.get("events", []) or []
    if len(f_events) != len(r_events):
        findings.append(Finding(
            INFO, "E12",
            f"export.json: event count: factory={len(f_events)}, reference={len(r_events)}"
        ))

    # Relationships
    f_rels = fe.get("relationships", []) or []
    r_rels = re_.get("relationships", []) or []
    if len(f_rels) != len(r_rels):
        findings.append(Finding(
            INFO, "E13",
            f"export.json: relationship count: factory={len(f_rels)}, reference={len(r_rels)}"
        ))


def _compare_export_object(
    fo: Dict, ro: Dict, obj_type: str, findings: List[Finding]
) -> None:
    """Compare structural patterns of a single export.json object."""
    # ariaOpsConf presence
    f_has_aria = "ariaOpsConf" in fo
    r_has_aria = "ariaOpsConf" in ro
    if f_has_aria != r_has_aria:
        f_desc = "has ariaOpsConf" if f_has_aria else "no ariaOpsConf"
        r_desc = "has ariaOpsConf" if r_has_aria else "no ariaOpsConf"
        findings.append(Finding(
            WARNING, "E14",
            f"export.json: object type={obj_type}: factory {f_desc}, reference {r_desc}"
        ))

    # metricSet count
    f_ms = fo.get("metricSets") or fo.get("requestedMetrics") or []
    r_ms = ro.get("metricSets") or ro.get("requestedMetrics") or []
    if len(f_ms) != len(r_ms):
        findings.append(Finding(
            INFO, "E15",
            f"export.json: object type={obj_type}: metricSet count: factory={len(f_ms)}, reference={len(r_ms)}"
        ))

    # objectBinding presence
    f_has_ob = any("objectBinding" in ms for ms in f_ms)
    r_has_ob = any("objectBinding" in ms for ms in r_ms)
    if f_has_ob != r_has_ob:
        f_desc = "has objectBinding" if f_has_ob else "no objectBinding"
        r_desc = "has objectBinding" if r_has_ob else "no objectBinding"
        findings.append(Finding(
            WARNING, "E16",
            f"export.json: object type={obj_type}: factory {f_desc}, reference {r_desc}"
        ))


def _nested_get(d: Dict, *keys) -> Any:
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


# ---------------------------------------------------------------------------
# template.json comparison
# ---------------------------------------------------------------------------

def _compare_template_json(
    factory_bytes: Optional[bytes],
    ref_bytes: Optional[bytes],
    findings: List[Finding],
) -> None:
    if not factory_bytes and not ref_bytes:
        return
    if not factory_bytes:
        findings.append(Finding(BLOCKING, "T0", "template.json: factory has no template.json"))
        return
    if not ref_bytes:
        findings.append(Finding(WARNING, "T0R", "template.json: reference has no template.json (cannot compare structure)"))
        return

    try:
        ft = json.loads(factory_bytes.decode("utf-8", errors="replace"))
    except json.JSONDecodeError as e:
        findings.append(Finding(BLOCKING, "T0P", f"template.json: factory template.json is not valid JSON: {e}"))
        return
    try:
        rt = json.loads(ref_bytes.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        findings.append(Finding(INFO, "T0RP", "template.json: reference template.json failed to parse (cannot compare)"))
        return

    # Top-level keys
    f_keys = set(ft.keys())
    r_keys = set(rt.keys())
    missing = r_keys - f_keys
    extra = f_keys - r_keys
    if missing:
        findings.append(Finding(
            BLOCKING, "T1",
            f"template.json: factory missing top-level keys: {sorted(missing)}"
        ))
    if extra:
        findings.append(Finding(
            INFO, "T2",
            f"template.json: factory has extra top-level keys: {sorted(extra)}"
        ))

    # source.resources count
    f_resources = _nested_get(ft, "source", "resources") or []
    r_resources = _nested_get(rt, "source", "resources") or []
    if len(f_resources) != len(r_resources):
        findings.append(Finding(
            INFO, "T3",
            f"template.json: source.resources count: factory={len(f_resources)}, reference={len(r_resources)}"
        ))

    # Total metric count across all resources
    def _count_metrics(resources: List) -> int:
        total = 0
        for res in resources:
            for rm in (res.get("requestedMetrics") or []):
                total += len(rm.get("metrics") or [])
        return total

    f_metric_total = _count_metrics(f_resources)
    r_metric_total = _count_metrics(r_resources)
    if f_metric_total != r_metric_total:
        findings.append(Finding(
            INFO, "T4",
            f"template.json: total metric count: factory={f_metric_total}, reference={r_metric_total}"
        ))


# ---------------------------------------------------------------------------
# Top-level comparison entry point
# ---------------------------------------------------------------------------

POLICIES = ("legacy", "upgrade", "structural")
SCHEMA_CONTRACT = "describeSchema 6.3.0 bounded credential contract; cleanroom-spec/02a Pass 10"


def _credential_contract(pak: Path, side: str, findings: List[Finding]) -> Optional[Dict[str, Any]]:
    """Validate declaration integrity, never reading or reporting credential values.

    This deliberately bounded reader is not a complete XSD validator. C-F* are
    conservative factory policies; C-S* check the documented schema grammar.
    """
    def fail(code: str, path: str, reason: str) -> None:
        findings.append(Finding(BLOCKING, code, f"{side}:{path}: {reason}"))

    def boolean(el: ET.Element, attr: str, path: str, default=None):
        if attr not in el.attrib:
            return default
        value = el.attrib[attr].strip(" \t\r\n")
        if value not in {"true", "false", "1", "0"}:
            fail("C-SBOOL", path + "/@" + attr, "invalid XML Schema boolean")
            return None
        return value in {"true", "1"}

    def required(el: ET.Element, attrs: Tuple[str, ...], path: str) -> None:
        for attr in attrs:
            value = el.get(attr, "").strip(" \t\r\n")
            if not value:
                fail("C-SATTR", path + "/@" + attr, "missing/empty required attribute")
            elif attr in {"nameKey", "dispOrder", "version"} and not re.fullmatch(r"[+-]?[0-9]+", value):
                fail("C-SATTR", path + "/@" + attr, "expected XML Schema integer")

    def archive(data, label):
        with zipfile.ZipFile(data) as zf:
            names = [i.filename for i in zf.infolist()]
            if len(names) != len(set(names)):
                fail("C-FARCHIVE", label, "duplicate archive members")
            if zf.testzip() is not None:
                fail("C-FARCHIVE", label, "archive CRC failure")
            return {n: zf.read(n) for n in names if not n.endswith("/")}

    try:
        outer = archive(pak, "/")
        manifest = json.loads(outer["manifest.txt"])
        nested = archive(io.BytesIO(outer["adapters.zip"]), "/adapters.zip")
        descs = [n for n in nested if n.endswith("/conf/describe.xml")]
        if len(descs) != 1:
            fail("C-FADAPTER", "/adapters.zip", "exactly one adapter descriptor required")
            return None
        dirname = descs[0].split("/")[0]
        # Container SDK packages declare a .conf entry point, not a Java JAR
        # (vcommunity_upgrade_path_experiment.md, architecture table).
        if descs[0] != f"{dirname}/conf/describe.xml" or dirname.endswith("_adapter3") or f"{dirname}.jar" not in nested or f"{dirname}.conf" in nested or manifest.get("adapters", ["adapters.zip"]) != ["adapters.zip"]:
            fail("C-FFAMILY", "/adapters.zip", "unsupported package family; native Java layout required")
        root = ET.fromstring(nested[descs[0]])
        for el in root.iter():
            if el.tag.startswith("{"):
                namespace, tag = el.tag[1:].split("}", 1)
                if namespace not in {"http://schemas.vmware.com/vcops/schema", "http://schemas.vmware.com/vcops/describe"}:
                    fail("C-FXML", "/AdapterKind", "unsupported XML namespace")
                el.tag = tag
        if root.tag != "AdapterKind":
            fail("C-FADAPTER", "/", "expected AdapterKind root")
        required(root, ("key", "nameKey", "version"), "/AdapterKind")
        identity = root.get("key")
        if manifest.get("adapter_kinds") != [identity] or dirname != identity:
            fail("C-FIDENTITY", "/manifest.txt/adapter_kinds", "manifest, descriptor and Java directory identities must agree")
        containers = root.findall("CredentialKinds")
        if len(containers) > 1:
            fail("C-SCONTAINER", "/AdapterKind/CredentialKinds", "duplicate credential containers")
        kinds: Dict[str, Dict] = {}
        for container in containers:
            if not list(container):
                fail("C-FNOAUTH", "/AdapterKind/CredentialKinds", "factory no-auth policy: omit an empty container (XSD permits it)")
            for ck in container:
                path = "/AdapterKind/CredentialKinds/CredentialKind"
                if ck.tag != "CredentialKind":
                    fail("C-SCHILD", path, "unsupported credential child")
                    continue
                required(ck, ("key", "nameKey"), path)
                key = ck.get("key", "")
                if key in kinds:
                    fail("C-SKEY", path + "/@key", "duplicate credential-kind key")
                fields = {}
                if not list(ck):
                    fail("C-SFIELD", path, "credential kind requires at least one field")
                for field in ck:
                    fp = path + "/CredentialField"
                    if field.tag != "CredentialField":
                        fail("C-SCHILD", fp, "unsupported field child")
                        continue
                    required(field, ("key", "nameKey", "dispOrder"), fp)
                    fk = field.get("key", "")
                    if fk in fields:
                        fail("C-SKEY", fp + "/@key", "duplicate credential-field key")
                    typ = field.get("type")
                    if typ is not None and typ not in {"string", "integer", "host", "ip"}:
                        fail("C-STYPE", fp + "/@type", "invalid credential-field type")
                    req = boolean(field, "required", fp)  # no documented default
                    mask = boolean(field, "password", fp, False)
                    boolean(field, "enum", fp, False)
                    for child in field:
                        if child.tag != "enum":
                            fail("C-SCHILD", fp, "unsupported field child")
                        else:
                            if "value" not in child.attrib:
                                fail("C-SATTR", fp + "/enum/@value", "missing required attribute")
                            boolean(child, "default", fp + "/enum")
                    fields[fk] = {"type": typ, "required": req, "password": mask}
                kinds[key] = fields
        rcontainers = root.findall("ResourceKinds")
        if len(rcontainers) != 1:
            fail("C-FRESOURCE", "/AdapterKind/ResourceKinds", "exactly one ResourceKinds container required")
        resources = {}
        instances = []
        used = set()
        for block in rcontainers:
            for rk in block:
                rp = "/AdapterKind/ResourceKinds/ResourceKind"
                if rk.tag != "ResourceKind":
                    fail("C-SCHILD", rp, "unsupported resource child")
                    continue
                required(rk, ("key", "nameKey"), rp)
                key = rk.get("key", "")
                if key in resources:
                    fail("C-SKEY", rp + "/@key", "duplicate resource-kind key")
                refs = ()
                if "credentialKind" in rk.attrib:
                    refs = tuple(token.strip(" \t\r\n") for token in rk.attrib["credentialKind"].split(","))
                    if not all(refs) or len(refs) != len(set(refs)) or any(x not in kinds for x in refs):
                        fail("C-SBINDING", rp + "/@credentialKind", "empty, duplicate or unresolved credential reference")
                    used.update(refs)
                req = boolean(rk, "isCredentialRequired", rp, True)
                resources[key] = {"bindings": refs, "required": req}
                typ = rk.get("type")
                if typ is not None:
                    value = typ.strip(" \t\r\n")
                    if not re.fullmatch(r"[+-]?[0-9]+", value):
                        fail("C-SATTR", rp + "/@type", "expected XML Schema integer")
                    else:
                        if int(value) not in {1, 2, 3, 4, 7, 8}:
                            fail("C-SATTR", rp + "/@type", "unsupported ResourceKind type enumeration")
                        rk.set("type", str(int(value)))
                if rk.get("type") == "7":
                    instances.append(key)
                    if not refs and req is not False:
                        fail("C-FREQUIRED", rp + "/@credentialKind", "factory configuration policy: unbound type-7 instance requires explicit isCredentialRequired=false (omission defaults true)")
        if instances != [identity]:
            fail("C-FINSTANCE", "/AdapterKind/ResourceKinds", "exactly one type-7 resource matching adapter identity required")
        for key in kinds.keys() - used:
            findings.append(Finding(WARNING, "C-UNBOUND", f"{side}:/AdapterKind/CredentialKinds: valid credential declaration is unbound"))
        return {"identity": identity, "kinds": kinds, "resources": resources, "root": root}
    except (OSError, KeyError, ValueError, TypeError, AttributeError, ET.ParseError, zipfile.BadZipFile, RuntimeError) as exc:
        # Do not echo malformed XML or archive contents (may contain secrets).
        fail("C-FINPUT", "/", f"cannot evaluate package contract ({type(exc).__name__})")
        return None


def _upgrade_contract(candidate: Dict, reference: Dict, findings: List[Finding]) -> None:
    def regression(path: str, message: str):
        findings.append(Finding(BLOCKING, "U-CREDENTIAL", "candidate:" + path + ": " + message))
    for key, old in reference["resources"].items():
        new = candidate["resources"].get(key)
        if new is None:
            if old["bindings"]:
                regression("/AdapterKind/ResourceKinds", "removed resource credential binding")
            continue
        if set(old["bindings"]) - set(new["bindings"]):
            regression("/AdapterKind/ResourceKinds/@credentialKind", "removed/renamed credential binding")
        if old["required"] is False and new["required"] is True:
            regression("/AdapterKind/ResourceKinds/@isCredentialRequired", "optional-to-required instance configuration")
    for key, fields in reference["kinds"].items():
        new_fields = candidate["kinds"].get(key)
        if new_fields is None:
            regression("/AdapterKind/CredentialKinds", "removed/renamed credential kind")
            continue
        for fk, old in fields.items():
            new = new_fields.get(fk)
            if new is None:
                regression("/AdapterKind/CredentialKinds/CredentialKind/CredentialField", "removed/renamed credential field")
            elif old["type"] != new["type"] or (old["required"] is not True and new["required"] is True) or (old["password"] is True and new["password"] is not True):
                regression("/AdapterKind/CredentialKinds/CredentialKind/CredentialField", "changed field type, increased requiredness or lost masking")
        if any(v["required"] is True for fk, v in new_fields.items() if fk not in fields):
            regression("/AdapterKind/CredentialKinds/CredentialKind/CredentialField", "new required credential field")
    for key in candidate["kinds"].keys() - reference["kinds"].keys():
        if any(v["required"] is True for v in candidate["kinds"][key].values()):
            regression("/AdapterKind/CredentialKinds", "new required credential fields")


def compare_paks(factory_pak: Path, reference_pak: Path, *, policy: str = "legacy", reference_sha256: Optional[str] = None) -> CompareResult:
    """Compare under an explicit policy; historical callers retain legacy behavior.

    Structural relevance approval remains an external governance requirement.
    The explicit reference digest pins the artifact selected by that review.
    """
    if policy not in POLICIES:
        raise ValueError(f"Unknown comparison policy: {policy}")
    if policy == "structural" and not reference_sha256:
        raise ValueError("Structural policy requires an explicit reference SHA-256")
    factory_pak, reference_pak = Path(factory_pak), Path(reference_pak)
    if reference_sha256 is not None:
        if not re.fullmatch(r"[0-9a-fA-F]{64}", reference_sha256) or hashlib.sha256(reference_pak.read_bytes()).hexdigest() != reference_sha256.lower():
            raise ValueError("Reference SHA-256 mismatch or invalid digest")
    if policy == "legacy":
        return _compare_paks_legacy(factory_pak, reference_pak)
    findings: List[Finding] = []
    f = _credential_contract(factory_pak, "candidate", findings)
    r = _credential_contract(reference_pak, "reference", findings)
    metadata = {"schema-contract": SCHEMA_CONTRACT}
    for side, path, contract in (("candidate", factory_pak, f), ("reference", reference_pak, r)):
        if path.is_file():
            metadata[side + "-sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        metadata[side + "-identity"] = str(contract["identity"]) if contract else "unavailable"
    if f and r:
        same = f["identity"] == r["identity"]
        if (policy == "upgrade" and not same) or (policy == "structural" and same):
            findings.append(Finding(BLOCKING, "P-IDENTITY", "/AdapterKind/@key: upgrade requires the same adapter; structural requires different adapters"))
    if not any(x.severity == BLOCKING for x in findings):
        result = _compare_paks_legacy(factory_pak, reference_pak,
                                     _normalized_descriptors=(ET.tostring(f["root"]), ET.tostring(r["root"])))
        if policy == "structural":
            for finding in result.findings:
                if finding.code in {"D1", "D2", "D6"}:
                    finding.severity = INFO
                    finding.message += ("; /AdapterKind/CredentialKinds or /AdapterKind/ResourceKinds/ResourceKind/@credentialKind: both independent credential contracts valid; optional declarations differ; "
                                        f"candidate kinds={len(f['kinds'])}, bindings={len(f['resources'][f['identity']]['bindings'])}, required={f['resources'][f['identity']]['required']}; "
                                        f"reference kinds={len(r['kinds'])}, bindings={len(r['resources'][r['identity']]['bindings'])}, required={r['resources'][r['identity']]['required']}")
        else:
            _upgrade_contract(f, r, result.findings)
        findings.extend(result.findings)
    findings.sort(key=lambda x: _SEVERITY_ORDER.get(x.severity, 99))
    return CompareResult(factory_pak.name, reference_pak.name, findings, policy=policy, metadata=metadata)

def _compare_paks_legacy(factory_pak: Path, reference_pak: Path, *,
                         _normalized_descriptors=None) -> CompareResult:
    """Compare a factory-built pak against a reference pak.

    Both paths must exist and be valid .pak (ZIP) files.
    Returns a CompareResult containing all findings.
    """
    factory_pak = Path(factory_pak)
    reference_pak = Path(reference_pak)

    findings: List[Finding] = []

    # --- Pak-level inventory ---
    try:
        f_inv = _read_pak_inventory(factory_pak)
    except (zipfile.BadZipFile, OSError) as e:
        findings.append(Finding(BLOCKING, "F0", f"Cannot open factory pak {factory_pak.name}: {e}"))
        return CompareResult(factory_pak.name, reference_pak.name, findings)

    try:
        r_inv = _read_pak_inventory(reference_pak)
    except (zipfile.BadZipFile, OSError) as e:
        findings.append(Finding(BLOCKING, "F1", f"Cannot open reference pak {reference_pak.name}: {e}"))
        return CompareResult(factory_pak.name, reference_pak.name, findings)

    _compare_pak_inventory(f_inv, r_inv, findings)

    # --- Manifest comparison ---
    f_manifest = _read_from_pak(factory_pak, "manifest.txt")
    r_manifest = _read_from_pak(reference_pak, "manifest.txt")
    _compare_manifest(f_manifest, r_manifest, findings)

    # --- adapters.zip inventory ---
    f_adapters_bytes = _read_adapters_zip(factory_pak)
    r_adapters_bytes = _read_adapters_zip(reference_pak)

    f_adapters_inv = _read_adapters_zip_inventory(f_adapters_bytes)
    r_adapters_inv = _read_adapters_zip_inventory(r_adapters_bytes)

    f_adapter_dir = _detect_adapter_dir(f_adapters_inv)
    r_adapter_dir = _detect_adapter_dir(r_adapters_inv)

    _compare_adapters_inventory(
        f_adapters_inv, r_adapters_inv,
        f_adapter_dir, r_adapter_dir,
        findings,
    )

    # --- describe.xml ---
    f_describe_bytes: Optional[bytes] = None
    r_describe_bytes: Optional[bytes] = None
    if f_adapter_dir and f_adapters_bytes:
        f_describe_bytes = _read_from_adapters_zip(
            f_adapters_bytes, f"{f_adapter_dir}/conf/describe.xml"
        )
    if r_adapter_dir and r_adapters_bytes:
        r_describe_bytes = _read_from_adapters_zip(
            r_adapters_bytes, f"{r_adapter_dir}/conf/describe.xml"
        )

    if _normalized_descriptors is not None:
        f_describe_bytes, r_describe_bytes = _normalized_descriptors
    _compare_describe_xml(
        f_describe_bytes, r_describe_bytes,
        f_adapter_dir, r_adapter_dir,
        findings,
    )

    # --- export.json ---
    f_export_bytes: Optional[bytes] = None
    r_export_bytes: Optional[bytes] = None
    if f_adapter_dir and f_adapters_bytes:
        f_export_bytes = _read_from_adapters_zip(
            f_adapters_bytes, f"{f_adapter_dir}/conf/export.json"
        )
    if r_adapter_dir and r_adapters_bytes:
        r_export_bytes = _read_from_adapters_zip(
            r_adapters_bytes, f"{r_adapter_dir}/conf/export.json"
        )

    _compare_export_json(f_export_bytes, r_export_bytes, findings)

    # --- template.json ---
    f_template_bytes: Optional[bytes] = None
    r_template_bytes: Optional[bytes] = None
    if f_adapter_dir and f_adapters_bytes:
        f_template_bytes = _read_from_adapters_zip(
            f_adapters_bytes, f"{f_adapter_dir}/conf/template.json"
        )
    if r_adapter_dir and r_adapters_bytes:
        r_template_bytes = _read_from_adapters_zip(
            r_adapters_bytes, f"{r_adapter_dir}/conf/template.json"
        )

    _compare_template_json(f_template_bytes, r_template_bytes, findings)

    # Sort: BLOCKING first, then WARNING, then INFO; stable within each group
    findings.sort(key=lambda f: _SEVERITY_ORDER.get(f.severity, 99))

    return CompareResult(factory_pak.name, reference_pak.name, findings)


# ---------------------------------------------------------------------------
# Directory-mode: compare factory pak against all paks in a directory
# ---------------------------------------------------------------------------

def compare_pak_directory(
    factory_pak: Path,
    reference_dir: Path,
    *, policy: str = "legacy", reference_sha256: Optional[str] = None,
) -> List[Tuple[Path, CompareResult]]:
    """Compare a factory pak against every .pak in a directory.

    Returns a list of (reference_path, CompareResult) sorted by ascending
    total finding count (closest structural match first).
    """
    if policy not in {"legacy", "upgrade"}:
        raise ValueError("Directory selection is supported only for legacy and upgrade policies")
    if reference_sha256 is not None:
        raise ValueError("A reference digest requires one explicit reference PAK")
    reference_dir = Path(reference_dir)
    ref_paks = sorted(reference_dir.glob("*.pak"))
    results = []
    for ref_path in ref_paks:
        result = compare_paks(factory_pak, ref_path, policy=policy)
        results.append((ref_path, result))
    results.sort(key=lambda x: (len(x[1].blocking()), len(x[1].warnings()), len(x[1].infos())))
    return results


# ---------------------------------------------------------------------------
# Report formatter
# ---------------------------------------------------------------------------

def format_report(result: CompareResult) -> str:
    """Format a CompareResult as a human-readable report string."""
    lines: List[str] = []
    lines.append("")
    lines.append(f"=== PAK COMPARE: {result.factory_label} vs {result.reference_label} ===")
    lines.append("")
    if result.policy != "legacy":
        lines.append(f"Policy: {result.policy}/1")
        for key, value in result.metadata.items():
            lines.append(f"{key}: {value}")
        lines.append("")

    blocking = result.blocking()
    warnings = result.warnings()
    infos = result.infos()

    if not blocking and not warnings and not infos:
        lines.append("No structural divergences found.")
    else:
        if blocking:
            lines.append("BLOCKING (will likely cause install failure):")
            for i, f in enumerate(blocking, 1):
                lines.append(f"  [B{i}] " + (f"{f.code}: " if result.policy != "legacy" else "") + f.message)
            lines.append("")

        if warnings:
            lines.append("WARNING (may cause issues):")
            for i, f in enumerate(warnings, 1):
                lines.append(f"  [W{i}] " + (f"{f.code}: " if result.policy != "legacy" else "") + f.message)
            lines.append("")

        if infos:
            lines.append("INFO (semantic or cosmetic differences):" if result.policy != "legacy" else "INFO (cosmetic, unlikely to affect install):")
            for i, f in enumerate(infos, 1):
                lines.append(f"  [I{i}] " + (f"{f.code}: " if result.policy != "legacy" else "") + f.message)
            lines.append("")

    lines.append(f"Score: {result.score_summary()}")
    if result.policy != "legacy":
        lines.append("Gate: " + ("FAIL" if blocking else "PASS"))
    lines.append("")
    return "\n".join(lines)
