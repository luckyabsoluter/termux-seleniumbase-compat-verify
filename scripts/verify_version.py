import json
import shutil
import subprocess
import sys

from seleniumbase import Driver


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


def emit_versions():
    chromium_path, chromium_version = get_binary_version("chromium")
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


def verify_seleniumbase(chromium_path):
    driver = None
    try:
        driver = Driver(
            browser="chrome",
            headless=True,
            binary_location=chromium_path,
        )
        driver.get("https://github.com/")
        print(f"Loaded title: {driver.title}")
    except Exception as exc:
        print(f"SeleniumBase verification failed: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    chromium_binary = emit_versions()
    verify_seleniumbase(chromium_binary)
