#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CHROMIUM_PACKAGE_SPEC="${CHROMIUM_PACKAGE_SPEC:-chromium}"
SELENIUMBASE_SPEC="${SELENIUMBASE_SPEC:-seleniumbase}"

pkg update -y
pkg install -y x11-repo
pkg install -y python "${CHROMIUM_PACKAGE_SPEC}"

python -m pip install -r "${REPO_ROOT}/requirements.txt"
python -m pip install "${SELENIUMBASE_SPEC}"
