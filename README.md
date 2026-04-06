# termux-seleniumbase-compat-verify

This repository continuously verifies whether the current Termux `chromium`
package remains compatible with the latest installed `seleniumbase` version.

## Layout

```text
.
├── .github/workflows/termux_ci.yml
├── requirements.txt
├── scripts/init_termux.sh
└── scripts/verify_version.py
```

## What the workflow does

1. Starts a GitHub Actions job on pushes, pull requests, and the configured
   schedule.
2. Starts the official `termux/termux-docker:x86_64` image as a reusable
   container so the Termux state can persist across separate CI steps.
3. Installs the latest `python` and `chromium` packages through `pkg`.
4. Installs Python dependencies from `requirements.txt`.
5. Runs the verification step separately to print detected Chromium and
   ChromeDriver version details.
6. Launches Chromium through SeleniumBase in headless mode and exits non-zero if
   startup or navigation fails.

## Local reproduction

Run the same checks locally with Docker:

```bash
docker run --rm \
  -v "$PWD:/app" \
  -w /app \
  termux/termux-docker:x86_64 \
  bash -lc "chmod +x scripts/init_termux.sh && ./scripts/init_termux.sh && python scripts/verify_version.py"
```

## Notes

- The workflow uses the `x86_64` Termux image because GitHub-hosted Ubuntu
  runners are x86_64. The upstream `latest` tag currently maps to `i686`.
- The scheduled workflow currently runs daily at `00:00` UTC.
