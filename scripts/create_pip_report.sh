#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SELENIUMBASE_SPEC="${SELENIUMBASE_SPEC:-seleniumbase}"
TERMUX_ARTIFACT_DIR="${TERMUX_ARTIFACT_DIR:-${REPO_ROOT}/artifacts}"
PIP_REPORT_PATH="${PIP_REPORT_PATH:-${TERMUX_ARTIFACT_DIR}/pip-resolve-report.json}"
PIP_REPORT_IGNORE_INSTALLED="${PIP_REPORT_IGNORE_INSTALLED:-1}"

mkdir -p "$(dirname "${PIP_REPORT_PATH}")"
rm -f "${PIP_REPORT_PATH}"

pip_args=(
  install
  --dry-run
  --report "${PIP_REPORT_PATH}"
)

if [[ "${PIP_REPORT_IGNORE_INSTALLED}" == "1" ]]; then
  pip_args+=(--ignore-installed)
fi

pip_args+=("${SELENIUMBASE_SPEC}")

python -m pip "${pip_args[@]}"

printf '%s\n' "${PIP_REPORT_PATH}"
