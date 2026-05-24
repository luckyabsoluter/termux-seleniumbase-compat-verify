import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def run_command(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }


def command_version(binary_name):
    binary_path = shutil.which(binary_name)
    if not binary_path:
        return {
            "path": None,
            "version": None,
        }

    version_result = run_command([binary_path, "--version"])
    return {
        "path": binary_path,
        "version": version_result["stdout"] or version_result["stderr"] or None,
    }


def find_chromium():
    for binary_name in ["chromium", "chromium-browser"]:
        version = command_version(binary_name)
        if version["path"]:
            return version

    return {
        "path": None,
        "version": None,
    }


def default_output_path():
    repo_root = Path(__file__).resolve().parents[1]
    artifact_dir = Path(os.environ.get("TERMUX_ARTIFACT_DIR", repo_root / "artifacts"))
    return artifact_dir / "env-snapshot.json"


def parse_args():
    parser = argparse.ArgumentParser(description="Collect Termux CI environment diagnostics.")
    parser.add_argument("--output", type=Path, default=default_output_path())
    return parser.parse_args()


def main():
    args = parse_args()
    snapshot = {
        "collected_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "python": {
            "version": sys.version,
            "executable": sys.executable,
            "paths": {
                "python": shutil.which("python"),
                "pip": shutil.which("pip"),
            },
        },
        "termux_compat_mode": os.environ.get("TERMUX_COMPAT_MODE"),
        "seleniumbase_platform_shim_disabled": os.environ.get(
            "TERMUX_DISABLE_SELENIUMBASE_PLATFORM_SHIM"
        ),
        "pip_freeze": run_command([sys.executable, "-m", "pip", "freeze"]),
        "pip_check": run_command([sys.executable, "-m", "pip", "check"]),
        "pkg_list_installed": run_command(["pkg", "list-installed"]),
        "chromium": find_chromium(),
        "chromedriver": command_version("chromedriver"),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(snapshot, indent=2))


if __name__ == "__main__":
    main()
