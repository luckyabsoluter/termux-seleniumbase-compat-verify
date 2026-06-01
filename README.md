# termux-seleniumbase-compat-verify

This repository maintains Termux compatibility for running the latest
`seleniumbase` package with Termux Chromium.

The default target is the current upstream SeleniumBase release. When an
upstream dependency does not install or run correctly on Android, this project
adds a documented Termux-native compatibility rule instead of pinning
SeleniumBase to an older version.


## Maintenance Policy

- Track the latest `seleniumbase` package by default.
- Do not pin SeleniumBase to an older version as the default response to a
  Termux/Android dependency failure.
- Do not use `pip install --no-deps` as the normal installation path.
- Add Termux-native dependency replacements to
  `compat/termux_native_packages.toml`.
- Include issue numbers as comments next to each compatibility rule.
- Keep install-time dependency compatibility separate from runtime platform
  shims.
- Preserve structured diagnostics artifacts for every CI run so failures can be
  compared across runs.

## Termux-Native Replacements

`compat/termux_native_packages.toml` maps Python package names from explicit
compatibility targets or the pip resolver report to Termux packages that should
be installed before the final SeleniumBase install.

For example, SeleniumBase may depend on `psutil`. PyPI `psutil` source builds
can reject Android, while Termux provides a maintained `python-psutil` package.
The manifest rule maps `psutil` to `python-psutil` and declares the Python
imports that must be verified after `pkg install`.

The `seleniumbase-with-termux-python-psutil` patch explicitly applies the
`psutil` manifest rule, installs `python-psutil`, and then generates an
installed-aware pip dry-run resolver report. Other native replacements should
be added as explicit compatibility targets instead of applying every manifest
rule when report generation fails.

When a future dependency fails only on Termux/Android, add a rule to the
manifest with:

- the PyPI package name under `[packages.<name>]`
- `termux_packages`
- `verify_imports`
- `policy`
- a short `reason`
- structured `references`
- nearby comments with relevant issue numbers

## What the Workflow Does

1. Starts a GitHub Actions job on pushes, pull requests, and the configured
   schedule.
2. Uses a matrix of test targets (e.g., unmodified `seleniumbase` vs versions with `python-psutil`).
3. Uses the matrix-selected Termux Docker image, Chromium package spec,
   SeleniumBase package spec, and a JSON array of active patches (`PATCHES_JSON`).
4. Copies the checked-out project into a writable `/data` directory inside
   the container.
5. Runs Termux commands through the image entrypoint.
6. Installs Termux `python`, `x11-repo`, and the matrix-selected Chromium
   package through `pkg`.
7. Subcommands of `scripts/main.py` handle all package resolutions and runtime checks.
8. If the `"seleniumbase-with-termux-python-psutil"` patch is active, it resolves the `psutil`
   replacement from `compat/termux_native_packages.toml`.
9. If applicable, it installs `python-psutil` through Termux and verifies the `psutil` Python import.
10. Generates an installed-aware pip dry-run resolver report for the selected SeleniumBase spec.
11. Installs shared Python dependencies from `requirements.txt`.
12. Installs the selected SeleniumBase spec with pip dependency resolution still enabled.
13. Runs `python -m pip check`.
14. Prints Chromium, ChromeDriver, SeleniumBase, Selenium, and psutil version details.
15. Launches Chromium through SeleniumBase and through direct Selenium WebDriver paths using `python scripts/main.py verify-version`.
16. Collects diagnostics artifacts even when initialization or verification fails.

## Diagnostics Artifacts

CI uploads the `artifacts` directory after each run. Important files include:

- `pip-resolve-report.json`
- `termux-native-packages.txt`
- `termux-native-summary.json`
- `env-snapshot.json`

The resolver and Termux-native package artifacts are produced by the patches like
`seleniumbase-with-termux-python-psutil`. The `unmodified-seleniumbase` target is
intentionally unmodified and may only contain environment diagnostics if installation fails first.

## Runtime Platform Shim

`scripts/termux_compat/termux_platform_shim.py` contains the SeleniumBase import-time Android
platform shim. It reports Android as Linux only for SeleniumBase import
compatibility and is disabled by default. 

To enable it, ensure `"seleniumbase_platform_shim"` is included in the `PATCHES_JSON` array when running tests, or export it in your shell if running manually:

```bash
export PATCHES_JSON='["seleniumbase_platform_shim"]'
```

## Local Reproduction

Local Docker reproduction commands are documented in
[`docs/local-reproduction.md`](docs/local-reproduction.md), including artifact
inspection steps for dependency resolution and environment diagnostics.

For **AI Agents** or rapid manual testing that bypasses the long `pkg install` process, refer to the skill documentation at [`skills/manual-docker-testing/SKILL.md`](skills/manual-docker-testing/SKILL.md).

## Notes

- The workflow uses the `x86_64` Termux image because GitHub-hosted Ubuntu
  runners are x86_64. The upstream `latest` tag currently maps to `i686`.
- The scheduled workflow currently runs daily at `00:00` UTC.
