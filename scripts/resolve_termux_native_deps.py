import argparse
import json
import os
from pathlib import Path
import re
import sys
import tomllib


NORMALIZE_RE = re.compile(r"[-_.]+")


def normalize_package_name(name):
    return NORMALIZE_RE.sub("-", name).lower()


def default_artifact_dir(repo_root):
    return Path(os.environ.get("TERMUX_ARTIFACT_DIR", repo_root / "artifacts"))


def load_json(path):
    with path.open("rb") as report_file:
        return json.load(report_file)


def load_manifest(manifest_path):
    with manifest_path.open("rb") as manifest_file:
        return tomllib.load(manifest_file)


def package_from_install_item(item):
    metadata = item.get("metadata") or {}
    name = metadata.get("name") or item.get("name")
    if not name:
        return None

    return {
        "name": name,
        "normalized_name": normalize_package_name(name),
        "version": metadata.get("version"),
        "requested": bool(item.get("requested")),
    }


def build_rule_index(manifest):
    rules = {}
    for package_name, rule in manifest.get("packages", {}).items():
        normalized_name = normalize_package_name(package_name)
        rules[normalized_name] = {
            "python_package": package_name,
            "normalized_name": normalized_name,
            "termux_packages": list(rule.get("termux_packages", [])),
            "verify_imports": list(rule.get("verify_imports", [])),
            "policy": rule.get("policy"),
            "reason": rule.get("reason"),
            "references": list(rule.get("references", [])),
        }
    return rules


def append_unique(items, new_items):
    for item in new_items:
        if item not in items:
            items.append(item)


def make_match(rule, match_source, resolved_version=None):
    matched_rule = dict(rule)
    matched_rule["match_source"] = match_source
    matched_rule["resolved_version"] = resolved_version
    matched_rule["applied"] = matched_rule["policy"] == "install_with_pkg_before_pip"
    return matched_rule


def add_match(matched_packages, termux_packages, matched_rule):
    if any(
        existing["normalized_name"] == matched_rule["normalized_name"]
        for existing in matched_packages
    ):
        return

    matched_packages.append(matched_rule)
    if matched_rule["applied"]:
        append_unique(termux_packages, matched_rule["termux_packages"])


def resolve_manifest_packages(package_names, rules, matched_packages, termux_packages):
    for package_name in package_names:
        normalized_name = normalize_package_name(package_name)
        rule = rules.get(normalized_name)
        if not rule:
            raise KeyError(package_name)

        add_match(
            matched_packages,
            termux_packages,
            make_match(rule, "explicit_manifest_package"),
        )


def resolve_from_report(report, rules, matched_packages, termux_packages):
    resolved_packages = []

    if not report:
        return resolved_packages

    for install_item in report.get("install", []):
        package = package_from_install_item(install_item)
        if not package:
            continue
        resolved_packages.append(package)

        rule = rules.get(package["normalized_name"])
        if not rule:
            continue

        add_match(
            matched_packages,
            termux_packages,
            make_match(rule, "pip_report", package["version"]),
        )

    return resolved_packages


def resolve_native_deps(report, manifest, manifest_packages=None):
    rules = build_rule_index(manifest)
    matched_packages = []
    termux_packages = []
    resolved_packages = resolve_from_report(report, rules, matched_packages, termux_packages)
    resolve_manifest_packages(manifest_packages or [], rules, matched_packages, termux_packages)

    return {
        "resolved_python_packages": resolved_packages,
        "matched_packages": matched_packages,
        "termux_packages": termux_packages,
    }


def write_package_list(package_list_path, termux_packages):
    package_list_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(termux_packages)
    if content:
        content += "\n"
    package_list_path.write_text(content, encoding="utf-8")


def write_summary(summary_path, summary):
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def parse_args():
    repo_root = Path(__file__).resolve().parents[1]
    artifact_dir = default_artifact_dir(repo_root)

    parser = argparse.ArgumentParser(
        description="Resolve Termux-native package replacements from a pip report.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path(os.environ.get("PIP_REPORT_PATH", artifact_dir / "pip-resolve-report.json")),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=repo_root / "compat" / "termux_native_packages.toml",
    )
    parser.add_argument(
        "--manifest-package",
        action="append",
        default=[],
        help="Resolve one named manifest package explicitly.",
    )
    parser.add_argument(
        "--package-list",
        type=Path,
        default=Path(
            os.environ.get(
                "TERMUX_NATIVE_PACKAGES_PATH",
                artifact_dir / "termux-native-packages.txt",
            )
        ),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path(
            os.environ.get(
                "TERMUX_NATIVE_SUMMARY_PATH",
                artifact_dir / "termux-native-summary.json",
            )
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()
    report_available = args.report.exists()
    if report_available:
        report = load_json(args.report)
    elif args.manifest_package:
        report = None
    else:
        raise FileNotFoundError(args.report)

    manifest = load_manifest(args.manifest)
    resolved = resolve_native_deps(report, manifest, args.manifest_package)
    summary = {
        "report_path": str(args.report),
        "report_available": report_available,
        "manifest_path": str(args.manifest),
        "explicit_manifest_packages": args.manifest_package,
        **resolved,
    }

    write_package_list(args.package_list, resolved["termux_packages"])
    write_summary(args.summary, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as exc:
        print(f"Required file was not found: {exc.filename}", file=sys.stderr)
        sys.exit(1)
    except KeyError as exc:
        print(f"Manifest package was not found: {exc.args[0]}", file=sys.stderr)
        sys.exit(1)
