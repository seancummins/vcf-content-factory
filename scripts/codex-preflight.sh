#!/usr/bin/env bash
# Read-only Codex preflight. Bootstrap is deliberately opt-in because it may
# contact registered Git remotes and change gitignored local clones.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

bootstrap=false
if [[ "${1:-}" == "--bootstrap" ]]; then
    bootstrap=true
elif [[ $# -ne 0 ]]; then
    echo "Usage: scripts/codex-preflight.sh [--bootstrap]" >&2
    exit 2
fi

if $bootstrap; then
    "${REPO_ROOT}/scripts/bootstrap_references.sh"
    "${REPO_ROOT}/scripts/bootstrap_managed_paks.sh"
fi

for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c \
        'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
        exec "$candidate" "${REPO_ROOT}/src/vcfcf_common/doctor.py"
    fi
done

echo "VCF Content Factory preflight skipped: Python 3.9+ is not available on PATH." >&2
exit 0
