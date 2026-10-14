#!/usr/bin/env bash
# Codex-facing content validation. The Python hook keeps Claude's JSON stdin
# contract and also exposes --path for this script.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

if [[ "${1:-}" == "--all" ]]; then
    shift
    if [[ $# -ne 0 ]]; then
        echo "Usage: scripts/validate-changed-content.sh [--all|<content-file>]" >&2
        exit 2
    fi
    exec python3 "${REPO_ROOT}/scripts/validate-content.py" --all
fi

if [[ $# -ne 1 ]]; then
    echo "Usage: scripts/validate-changed-content.sh [--all|<content-file>]" >&2
    exit 2
fi

exec python3 "${REPO_ROOT}/scripts/validate-content.py" --path "$1"
