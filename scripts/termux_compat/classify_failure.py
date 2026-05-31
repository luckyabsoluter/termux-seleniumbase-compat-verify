import argparse
import json
from pathlib import Path
import re
import sys


RULES = [
    (
        "native_build_android_unsupported",
        [
            r"platform android is not supported",
            r"android.*not supported",
        ],
    ),
    (
        "missing_python_dependency",
        [
            r"ModuleNotFoundError: No module named",
            r"ImportError: No module named",
        ],
    ),
    (
        "dependency_version_conflict",
        [
            r"ResolutionImpossible",
            r"dependency conflict",
            r"conflicting dependencies",
            r"Cannot install .* because these package versions have conflicting dependencies",
        ],
    ),
    (
        "chromedriver_missing",
        [
            r"Chromedriver binary was not found",
            r"Unable to obtain driver for chrome",
            r"chromedriver.*not found",
        ],
    ),
    (
        "chromium_missing",
        [
            r"Chromium binary was not found",
            r"chrome binary.*not found",
            r"cannot find Chrome binary",
        ],
    ),
    (
        "seleniumbase_runtime_failure",
        [
            r"SeleniumBase verification failed",
            r"seleniumbase_runner",
        ],
    ),
    (
        "selenium_runtime_failure",
        [
            r"Selenium verification failed",
            r"selenium_runner",
        ],
    ),
]


def read_inputs(paths):
    if paths:
        chunks = []
        for path in paths:
            if path.exists():
                chunks.append(path.read_text(encoding="utf-8", errors="replace"))
        return "\n".join(chunks)

    if not sys.stdin.isatty():
        return sys.stdin.read()

    return ""


def classify(text):
    for category, patterns in RULES:
        for pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                return {
                    "category": category,
                    "matched_pattern": pattern,
                }

    return {
        "category": "unknown_failure",
        "matched_pattern": None,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Classify Termux compatibility failure text.")
    parser.add_argument("inputs", nargs="*", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main():
    args = parse_args()
    text = read_inputs(args.inputs)
    result = classify(text)
    result["input_files"] = [str(path) for path in args.inputs]

    output = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
