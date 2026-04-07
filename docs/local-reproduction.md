# Local reproduction

This document describes how to run the Termux SeleniumBase compatibility check
locally with Docker.

The examples below use `termux/termux-docker:x86_64`. If your local machine or
Docker environment uses a different CPU architecture, replace that tag with the
matching Termux Docker image tag for your system, such as
`termux/termux-docker:aarch64`.

## Direct bind mount

This is the simpler local flow. It mounts the current project into `/app` and
runs the verification directly from that path.

```bash
docker run --rm \
  -v "$PWD:/app" \
  -w /app \
  -e CHROMIUM_PACKAGE_SPEC="chromium" \
  -e SELENIUMBASE_SPEC="seleniumbase" \
  termux/termux-docker:x86_64 \
  bash -lc "bash scripts/init_termux.sh && python scripts/verify_version.py"
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
  termux/termux-docker:x86_64 \
  bash -lc "rm -rf /tmp/termux-seleniumbase-compat-verify && mkdir -p /tmp/termux-seleniumbase-compat-verify && cp -a /app/. /tmp/termux-seleniumbase-compat-verify && chown -R system:system /tmp/termux-seleniumbase-compat-verify && su system -c 'cd /tmp/termux-seleniumbase-compat-verify && bash scripts/init_termux.sh && python scripts/verify_version.py'"
```
