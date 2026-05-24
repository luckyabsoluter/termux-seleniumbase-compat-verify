# Local reproduction

This document describes how to run the Termux SeleniumBase compatibility check
locally with Docker.

The examples below use `termux/termux-docker:x86_64`. If your local machine or
Docker environment uses a different CPU architecture, replace that tag with the
matching Termux Docker image tag for your system, such as
`termux/termux-docker:aarch64`.

For an interactive local workflow that keeps the container running and lets you
inspect or modify the Termux environment interactively, see
[`docs/local-interactive-workflow.md`](local-interactive-workflow.md).

## Direct bind mount

This is the simpler local flow. It mounts the current project into `/app` and
runs the verification directly from that path. Diagnostics are written to the
local `artifacts` directory.

```bash
docker run --rm \
  -v "$PWD:/app" \
  -w /app \
  -e CHROMIUM_PACKAGE_SPEC="chromium" \
  -e SELENIUMBASE_SPEC="seleniumbase" \
  -e TERMUX_COMPAT_MODE="seleniumbase-with-termux-python-psutil" \
  -e TERMUX_ARTIFACT_DIR="/app/artifacts" \
  termux/termux-docker:x86_64 \
  bash -lc 'mkdir -p "$TERMUX_ARTIFACT_DIR"; bash scripts/init_termux.sh && python scripts/verify_version.py; status=$?; python scripts/collect_env_snapshot.py --output "$TERMUX_ARTIFACT_DIR/env-snapshot.json" || true; exit $status'
```

## Writable project copy

This matches the CI flow more closely. It mounts the repository at `/app`,
copies it into a writable directory inside the container, and runs the scripts
from that copied project tree so SeleniumBase can create `downloaded_files`
inside the project.

```bash
docker run --rm \
  -v "$PWD:/app" \
  -w /app \
  -e CHROMIUM_PACKAGE_SPEC="chromium" \
  -e SELENIUMBASE_SPEC="seleniumbase" \
  -e TERMUX_COMPAT_MODE="seleniumbase-with-termux-python-psutil" \
  termux/termux-docker:x86_64 \
  bash -lc 'project_dir="/data/termux-seleniumbase-compat-verify"; artifact_dir="$project_dir/artifacts"; rm -rf "$project_dir"; mkdir -p "$project_dir"; cp -a /app/. "$project_dir"; chown -R system:system "$project_dir"; /entrypoint.sh bash -lc "cd /data/termux-seleniumbase-compat-verify && export TERMUX_COMPAT_MODE=seleniumbase-with-termux-python-psutil && export TERMUX_ARTIFACT_DIR=/data/termux-seleniumbase-compat-verify/artifacts && mkdir -p \"\$TERMUX_ARTIFACT_DIR\"; bash scripts/init_termux.sh && python scripts/verify_version.py"; status=$?; /entrypoint.sh bash -lc "cd /data/termux-seleniumbase-compat-verify && export TERMUX_COMPAT_MODE=seleniumbase-with-termux-python-psutil && export TERMUX_ARTIFACT_DIR=/data/termux-seleniumbase-compat-verify/artifacts && python scripts/collect_env_snapshot.py --output \"\$TERMUX_ARTIFACT_DIR/env-snapshot.json\" || true"; cp -a "$artifact_dir" /app/artifacts || true; exit $status'
```

Set `TERMUX_COMPAT_MODE=unmodified-seleniumbase` and
`TERMUX_DISABLE_SELENIUMBASE_PLATFORM_SHIM=1` to reproduce the
`unmodified-seleniumbase` matrix target without Termux-native dependency
replacement or the SeleniumBase platform shim.

## Artifact inspection

After either flow, inspect the generated artifacts from the local repository:

```bash
ls -la artifacts
cat artifacts/env-snapshot.json
test -f artifacts/termux-native-summary.json && cat artifacts/termux-native-summary.json
```

The most useful dependency files are:

- `artifacts/pip-resolve-report.json`
- `artifacts/termux-native-packages.txt`
- `artifacts/termux-native-summary.json`

The most useful runtime files are:

- `artifacts/env-snapshot.json`
