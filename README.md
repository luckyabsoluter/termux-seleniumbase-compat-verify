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
2. Uses a job matrix so additional verification targets can be added later
   while the current workflow still runs a single `latest` target.
3. Starts the official `termux/termux-docker:x86_64` image as a reusable
   container so the Termux state can persist across separate CI steps.
4. Runs the init and verify steps as the Termux `system` user so `pkg` and the
   packaged Python environment behave like they do inside Termux.
5. Installs `python` and the matrix-selected Chromium package spec through
   `pkg`. The current target uses the latest `chromium`.
6. Installs shared Python dependencies from `requirements.txt` and then
   installs the matrix-selected SeleniumBase spec. The current target uses the
   latest `seleniumbase`.
7. Runs the verification step separately to print detected Chromium and
   ChromeDriver version details.
8. Launches Chromium through SeleniumBase in headless mode and exits non-zero if
   startup or navigation fails.

## Local reproduction

Run the same checks locally with Docker:

```bash
docker run --rm \
  -v "$PWD:/app" \
  -w /app \
  -e CHROMIUM_PACKAGE_SPEC="chromium" \
  -e SELENIUMBASE_SPEC="seleniumbase" \
  termux/termux-docker:x86_64 \
  bash -lc "bash scripts/init_termux.sh && python scripts/verify_version.py"
```

## Notes

- The workflow uses the `x86_64` Termux image because GitHub-hosted Ubuntu
  runners are x86_64. The upstream `latest` tag currently maps to `i686`.
- The matrix currently contains one `latest` target with `chromium` and
  `seleniumbase` package specs, ready to be extended with pinned versions later.
- The scheduled workflow currently runs daily at `00:00` UTC.
