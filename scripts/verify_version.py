import json
import shutil
import subprocess
import sys

from seleniumbase_runner import run_seleniumbase_check


def run_command(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_binary_version(binary_name):
    binary_path = shutil.which(binary_name)
    if not binary_path:
        return None, None
    version = run_command([binary_path, "--version"])
    return binary_path, version


def find_chromium():
    for chromium_binary in ["chromium", "chromium-browser"]:
        chromium_path, chromium_version = get_binary_version(chromium_binary)
        if chromium_path:
            break
    return chromium_path, chromium_version


def emit_versions():
    chromium_path, chromium_version = find_chromium()
    chromedriver_path, chromedriver_version = get_binary_version("chromedriver")

    if not chromium_path:
        print("Chromium binary was not found in PATH.", file=sys.stderr)
        sys.exit(1)

    print(
        json.dumps(
            {
                "chromium_path": chromium_path,
                "chromium_version": chromium_version,
                "chromedriver_path": chromedriver_path,
                "chromedriver_version": chromedriver_version,
            },
            indent=2,
        )
    )
    return chromium_path


if __name__ == "__main__":
    chromium_binary = emit_versions()
    try:
        run_seleniumbase_check(chromium_binary)
    except Exception as exc:
        print(f"SeleniumBase verification failed: {exc}", file=sys.stderr)
        sys.exit(1)
