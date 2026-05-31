#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PATCHES_JSON="${PATCHES_JSON:-[]}"

pkg update -y
pkg install -y x11-repo
pkg install -y python

has_patch() {
  python -c "import os, json, sys; sys.exit(0 if sys.argv[1] in json.loads(os.environ.get('PATCHES_JSON', '[]')) else 1)" "$1"
}

get_chromium_spec() {
  python -c "import os, json; print(next((p for p in json.loads(os.environ.get('PATCHES_JSON', '[]')) if p.startswith('chromium')), 'chromium'))"
}

get_sb_spec() {
  python -c "import os, json; print(next((p for p in json.loads(os.environ.get('PATCHES_JSON', '[]')) if p.startswith('seleniumbase==')), 'seleniumbase'))"
}

CHROMIUM_PACKAGE_SPEC="$(get_chromium_spec)"
SELENIUMBASE_SPEC="$(get_sb_spec)"
TERMUX_ARTIFACT_DIR="${TERMUX_ARTIFACT_DIR:-${REPO_ROOT}/artifacts}"
PIP_REPORT_PATH="${PIP_REPORT_PATH:-${TERMUX_ARTIFACT_DIR}/pip-resolve-report.json}"
TERMUX_NATIVE_PACKAGES_PATH="${TERMUX_NATIVE_PACKAGES_PATH:-${TERMUX_ARTIFACT_DIR}/termux-native-packages.txt}"
TERMUX_NATIVE_SUMMARY_PATH="${TERMUX_NATIVE_SUMMARY_PATH:-${TERMUX_ARTIFACT_DIR}/termux-native-summary.json}"
export TERMUX_ARTIFACT_DIR PIP_REPORT_PATH TERMUX_NATIVE_PACKAGES_PATH TERMUX_NATIVE_SUMMARY_PATH

pkg install -y "${CHROMIUM_PACKAGE_SPEC}"

mkdir -p "${TERMUX_ARTIFACT_DIR}"

if ! has_patch "seleniumbase-with-termux-python-psutil"; then
  python -m pip install -r "${REPO_ROOT}/requirements.txt"
  python -m pip install --upgrade --upgrade-strategy only-if-needed "${SELENIUMBASE_SPEC}"
  python -m pip check
  exit 0
fi

python "${SCRIPT_DIR}/resolve_termux_native_deps.py" --manifest-package psutil

if [[ -s "${TERMUX_NATIVE_PACKAGES_PATH}" ]]; then
  mapfile -t TERMUX_NATIVE_PACKAGES < "${TERMUX_NATIVE_PACKAGES_PATH}"
  pkg install -y "${TERMUX_NATIVE_PACKAGES[@]}"
  python "${SCRIPT_DIR}/verify_termux_native_deps.py"
else
  python "${SCRIPT_DIR}/verify_termux_native_deps.py"
fi

PIP_REPORT_IGNORE_INSTALLED=0 bash "${SCRIPT_DIR}/create_pip_report.sh"
python "${SCRIPT_DIR}/resolve_termux_native_deps.py" --manifest-package psutil

python -m pip install -r "${REPO_ROOT}/requirements.txt"
python -m pip install --upgrade --upgrade-strategy only-if-needed "${SELENIUMBASE_SPEC}"
python -m pip check
