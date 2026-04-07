# Local interactive workflow

This document collects local commands for starting a Termux Docker container
and inspecting or modifying the environment interactively.

The examples below use `termux/termux-docker:x86_64`. If your local machine or
Docker environment uses a different CPU architecture, replace that tag with the
matching Termux Docker image tag for your system, such as
`termux/termux-docker:aarch64`.

## Start a reusable container

<details open>
<summary>bash</summary>

```bash
container="termux-seleniumbase-ci"

docker run -d \
  --name "$container" \
  -v "$PWD:/app" \
  -w /app \
  termux/termux-docker:x86_64 \
  bash -lc "while true; do sleep 3600; done"
```

</details>

<details>
<summary>PowerShell</summary>

```powershell
$container = "termux-seleniumbase-ci"
$workspace = (Get-Location).Path

docker run -d `
  --name $container `
  -v "${workspace}:/app" `
  -w /app `
  termux/termux-docker:x86_64 `
  bash -lc "while true; do sleep 3600; done"
```

</details>

## Initialize project dependencies

<details open>
<summary>bash</summary>

```bash
docker exec \
  -e CHROMIUM_PACKAGE_SPEC="chromium" \
  -e SELENIUMBASE_SPEC="seleniumbase" \
  "$container" \
  /entrypoint.sh bash -lc "bash scripts/init_termux.sh"
```

</details>

<details>
<summary>PowerShell</summary>

```powershell
docker exec `
  -e CHROMIUM_PACKAGE_SPEC="chromium" `
  -e SELENIUMBASE_SPEC="seleniumbase" `
  $container `
  /entrypoint.sh bash -lc "bash scripts/init_termux.sh"
```

</details>

## Run the verification script

<details open>
<summary>bash</summary>

```bash
docker exec \
  "$container" \
  /entrypoint.sh bash -lc "python scripts/verify_version.py"
```

</details>

<details>
<summary>PowerShell</summary>

```powershell
docker exec `
  $container `
  /entrypoint.sh bash -lc "python scripts/verify_version.py"
```

</details>

## Open an interactive shell

Use the Termux entrypoint when attaching interactively:

<details open>
<summary>bash</summary>

```bash
docker exec -it "$container" /entrypoint.sh bash
```

</details>

<details>
<summary>PowerShell</summary>

```powershell
docker exec -it $container /entrypoint.sh bash
```

</details>

## Set the terminal type

Inside the interactive shell, set a terminal type first. Without `TERM`, many
interactive tools and terminal features will not work:

```bash
export TERM=xterm-256color
```

## Inspect Chromium-related binaries

Inside the interactive shell, inspect the available Chromium-related commands:

```bash
find $PREFIX/bin -name "*chromium*"
```

## Create a Chromium compatibility symlink

If you need a `chromium` command that points to `chromium-browser`, run this
inside the interactive shell:

```bash
ln -s $PREFIX/bin/chromium-browser $PREFIX/bin/chromium
```

## Clean up the container

<details open>
<summary>bash</summary>

```bash
docker rm -f "$container"
```

</details>

<details>
<summary>PowerShell</summary>

```powershell
docker rm -f $container
```

</details>
