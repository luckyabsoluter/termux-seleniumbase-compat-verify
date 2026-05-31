import argparse
import importlib
from importlib import metadata
import json
import os
from pathlib import Path
import sys


def default_summary_path():
    repo_root = Path(__file__).resolve().parents[2]
    artifact_dir = Path(os.environ.get("TERMUX_ARTIFACT_DIR", repo_root / "artifacts"))
    return Path(os.environ.get("TERMUX_NATIVE_SUMMARY_PATH", artifact_dir / "termux-native-summary.json"))


def get_distribution_version(distribution_name):
    try:
        return metadata.version(distribution_name)
    except metadata.PackageNotFoundError:
        return None


def verify_import(distribution_name, module_name):
    module = importlib.import_module(module_name)
    version = get_distribution_version(distribution_name)
    if version is None:
        version = getattr(module, "__version__", None)

    return {
        "distribution": distribution_name,
        "module": module_name,
        "version": version,
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Verify imports supplied by Termux-native Python packages.",
    )
    parser.add_argument("--summary", type=Path, default=default_summary_path())
    return parser.parse_args()


def main():
    args = parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    verified_imports = []

    for package in summary.get("matched_packages", []):
        if not package.get("applied"):
            continue
        distribution_name = package["python_package"]
        for module_name in package.get("verify_imports", []):
            verified_imports.append(verify_import(distribution_name, module_name))

    if not verified_imports:
        print("No Termux-native Python imports to verify.")
        return

    print(json.dumps({"verified_imports": verified_imports}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Termux-native dependency verification failed: {exc}", file=sys.stderr)
        sys.exit(1)
