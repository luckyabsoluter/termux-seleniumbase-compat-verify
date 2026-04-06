#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

pkg update -y
pkg install -y x11-repo
pkg install -y python chromium

python -m pip install -r "${REPO_ROOT}/requirements.txt"
