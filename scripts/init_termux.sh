#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CHROMIUM_PACKAGE_SPEC="${CHROMIUM_PACKAGE_SPEC:-chromium}"
SELENIUMBASE_SPEC="${SELENIUMBASE_SPEC:-seleniumbase}"
TERMUX_COMPAT_MODE="${TERMUX_COMPAT_MODE:-seleniumbase-with-termux-python-psutil}"
TERMUX_ARTIFACT_DIR="${TERMUX_ARTIFACT_DIR:-${REPO_ROOT}/artifacts}"
PIP_REPORT_PATH="${PIP_REPORT_PATH:-${TERMUX_ARTIFACT_DIR}/pip-resolve-report.json}"
TERMUX_NATIVE_PACKAGES_PATH="${TERMUX_NATIVE_PACKAGES_PATH:-${TERMUX_ARTIFACT_DIR}/termux-native-packages.txt}"
TERMUX_NATIVE_SUMMARY_PATH="${TERMUX_NATIVE_SUMMARY_PATH:-${TERMUX_ARTIFACT_DIR}/termux-native-summary.json}"
export TERMUX_ARTIFACT_DIR PIP_REPORT_PATH TERMUX_NATIVE_PACKAGES_PATH TERMUX_NATIVE_SUMMARY_PATH

pkg update -y
pkg install -y x11-repo
pkg install -y python "${CHROMIUM_PACKAGE_SPEC}"

mkdir -p "${TERMUX_ARTIFACT_DIR}"

if [[ "${TERMUX_COMPAT_MODE}" == "unmodified-seleniumbase" ]]; then
  python -m pip install -r "${REPO_ROOT}/requirements.txt"
  python -m pip install --upgrade --upgrade-strategy only-if-needed "${SELENIUMBASE_SPEC}"
  python -m pip check
  exit 0
fi

if [[ "${TERMUX_COMPAT_MODE}" != "seleniumbase-with-termux-python-psutil" ]]; then
  echo "Unsupported TERMUX_COMPAT_MODE: ${TERMUX_COMPAT_MODE}" >&2
  exit 2
fi

if bash "${SCRIPT_DIR}/create_pip_report.sh"; then
  python "${SCRIPT_DIR}/resolve_termux_native_deps.py"
else
  python "${SCRIPT_DIR}/resolve_termux_native_deps.py" --all-manifest-rules
fi

if [[ -s "${TERMUX_NATIVE_PACKAGES_PATH}" ]]; then
  mapfile -t TERMUX_NATIVE_PACKAGES < "${TERMUX_NATIVE_PACKAGES_PATH}"
  pkg install -y "${TERMUX_NATIVE_PACKAGES[@]}"
  python "${SCRIPT_DIR}/verify_termux_native_deps.py"

  if [[ ! -s "${PIP_REPORT_PATH}" ]]; then
    PIP_REPORT_IGNORE_INSTALLED=0 bash "${SCRIPT_DIR}/create_pip_report.sh"
  fi
else
  python "${SCRIPT_DIR}/verify_termux_native_deps.py"
fi

python -m pip install -r "${REPO_ROOT}/requirements.txt"
python -m pip install --upgrade --upgrade-strategy only-if-needed "${SELENIUMBASE_SPEC}"
python -m pip check
