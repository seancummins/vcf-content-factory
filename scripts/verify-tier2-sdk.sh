#!/usr/bin/env bash
# Local-only Tier 2 verification. It never installs a pak or contacts VCF Ops.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

if [[ $# -ne 2 && $# -ne 4 ]]; then
    echo "Usage: scripts/verify-tier2-sdk.sh <adapter-dir> <reference-pak-dir> OR <adapter-dir> <reference.pak> <legacy|upgrade|structural> <sha256>" >&2
    exit 2
fi

adapter_dir="$1"
reference_dir="$2"
if [[ ! -f "${adapter_dir}/adapter.yaml" ]]; then
    echo "ERROR: adapter.yaml not found under ${adapter_dir}" >&2
    exit 2
fi
if [[ $# -eq 2 && ! -d "$reference_dir" ]]; then
    echo "ERROR: reference pak directory not found: ${reference_dir}" >&2
    exit 2
fi
build_compare_args=()
compare_args=(--reference-dir "$reference_dir")
if [[ $# -eq 4 ]]; then
    build_compare_args=(--pak-compare-policy "$3" --pak-compare-reference "$2" --pak-compare-reference-sha256 "$4")
    compare_args=("$2" --policy "$3" --reference-sha256 "$4")
fi
if ! command -v javac >/dev/null 2>&1; then
    echo "ERROR: javac is required for Tier 2 verification." >&2
    exit 2
fi

mkdir -p "${REPO_ROOT}/dist"
python3 -m vcfcf_managementpacks validate-sdk "$adapter_dir"
python3 -m vcfcf_managementpacks build-sdk "$adapter_dir" -o "${REPO_ROOT}/dist" "${build_compare_args[@]}"

pak_path="$(python3 - "$adapter_dir" "${REPO_ROOT}/dist" <<'PY'
import sys
from pathlib import Path
import yaml

project = Path(sys.argv[1])
output = Path(sys.argv[2])
with (project / "adapter.yaml").open(encoding="utf-8") as handle:
    adapter_kind = yaml.safe_load(handle)["adapter_kind"]
matches = sorted(output.glob(f"vcfcf_sdk_{adapter_kind.removeprefix('vcfcf_')}.*.pak"))
if not matches:
    raise SystemExit("No Tier 2 pak was produced.")
print(matches[-1])
PY
)"
python3 -m vcfcf_managementpacks pak-compare "$pak_path" "${compare_args[@]}"
