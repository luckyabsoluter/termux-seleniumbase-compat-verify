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

For AI Agents or rapid manual iterative testing without rebuilding the container, see
[`skills/manual-docker-testing/SKILL.md`](../skills/manual-docker-testing/SKILL.md).

## Direct bind mount

This is the simpler local flow. It mounts the current project into `/app` and
runs the verification directly from that path. Diagnostics are written to the
local `artifacts` directory.

```bash
docker run --rm \
  -v "$PWD:/app" \
  -w /app \
  -e PATCHES_JSON='["seleniumbase-with-termux-python-psutil"]' \
  -e TERMUX_ARTIFACT_DIR="/app/artifacts" \
  termux/termux-docker:x86_64 \
  bash -lc 'mkdir -p "$TERMUX_ARTIFACT_DIR"; bash scripts/init_termux.sh && python scripts/main.py verify-version; status=$?; python scripts/main.py collect-env-snapshot --output "$TERMUX_ARTIFACT_DIR/env-snapshot.json" || true; exit $status'
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
  -e PATCHES_JSON='["seleniumbase-with-termux-python-psutil", "seleniumbase_platform_shim"]' \
  termux/termux-docker:x86_64 \
  bash -lc 'project_dir="/data/termux-seleniumbase-compat-verify"; artifact_dir="$project_dir/artifacts"; rm -rf "$project_dir"; mkdir -p "$project_dir"; cp -a /app/. "$project_dir"; chown -R system:system "$project_dir"; /entrypoint.sh bash -lc "cd /data/termux-seleniumbase-compat-verify && export PATCHES_JSON='\''[\"seleniumbase-with-termux-python-psutil\", \"seleniumbase_platform_shim\"]'\'' && export TERMUX_ARTIFACT_DIR=/data/termux-seleniumbase-compat-verify/artifacts && mkdir -p \"\$TERMUX_ARTIFACT_DIR\"; bash scripts/init_termux.sh && python scripts/main.py verify-version"; status=$?; /entrypoint.sh bash -lc "cd /data/termux-seleniumbase-compat-verify && export PATCHES_JSON='\''[\"seleniumbase-with-termux-python-psutil\", \"seleniumbase_platform_shim\"]'\'' && export TERMUX_ARTIFACT_DIR=/data/termux-seleniumbase-compat-verify/artifacts && python scripts/main.py collect-env-snapshot --output \"\$TERMUX_ARTIFACT_DIR/env-snapshot.json\" || true"; cp -a "$artifact_dir" /app/artifacts || true; exit $status'
```

To run the baseline unmodified verification, leave `PATCHES_JSON` unset or set it to `'[]'`. This reproduces the `unmodified-seleniumbase` target without Termux-native dependency replacement or the SeleniumBase platform shim.

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
