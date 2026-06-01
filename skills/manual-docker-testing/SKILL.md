# MANUAL-DOCKER-TESTING

This skill provides instructions for the agent to manually and rapidly test and debug the Termux SeleniumBase compatibility scripts in a local Docker (Termux-Docker) environment.

## Trigger
Activate this skill when the user makes requests such as:
- "Test it locally"
- "Test the script in docker"
- "Skip package installation and just quickly test the script"
- "Test it again in docker"

## Instructions

Standard GitHub Actions (`act`) execution is very slow because it destroys the container and reruns `pkg install` from scratch on every run. To solve this, this skill utilizes a **persistent background container** to overwrite only the script files and rapidly test the code.
The agent must dynamically combine the raw Docker commands below without relying on any external wrapper shell scripts.

### Common Environment Variables
- Container Name: `termux-seleniumbase-dev`
- Base Image: `termux/termux-docker:x86_64`
- Patches (for testing): `'["seleniumbase-with-termux-python-psutil", "seleniumbase_platform_shim"]'`

---

### 1. Container Initialization & Package Installation (Initial Setup or Full Reset)
If the container does not exist, package dependencies are completely broken, or the `init_termux.sh` step itself needs to be verified, create the container and perform initialization.

```bash
# 1. Force remove existing container (if any)
docker rm -f termux-seleniumbase-dev || true

# 2. Run container in background
docker run -d --name termux-seleniumbase-dev termux/termux-docker:x86_64 bash -lc "while true; do sleep 3600; done"

# 3. Copy local code and set permissions
docker exec termux-seleniumbase-dev bash -lc "mkdir -p /data/termux-seleniumbase-compat-verify"
docker cp . termux-seleniumbase-dev:/data/termux-seleniumbase-compat-verify/
docker exec termux-seleniumbase-dev bash -lc "chown -R system:system /data/termux-seleniumbase-compat-verify"

# 4. Run initialization script (includes pkg install)
docker exec -w /data/termux-seleniumbase-compat-verify termux-seleniumbase-dev /entrypoint.sh bash -lc "PATCHES_JSON='[\"seleniumbase-with-termux-python-psutil\", \"seleniumbase_platform_shim\"]' bash scripts/init_termux.sh"
```

---

### 2. Rapid Script Verification (Primary Task)
If the Docker container is already running and `pkg install` has been completed, skip the heavy environment setup and simply overwrite the modified script files for a rapid check. This is highly useful for iterative verification when modifying script logic.

```bash
# 1. Overwrite with modified local code and set permissions
docker cp . termux-seleniumbase-dev:/data/termux-seleniumbase-compat-verify/
docker exec termux-seleniumbase-dev bash -lc "chown -R system:system /data/termux-seleniumbase-compat-verify"

# 2. Run only the Python verification script
docker exec -w /data/termux-seleniumbase-compat-verify termux-seleniumbase-dev /entrypoint.sh bash -lc "PATCHES_JSON='[\"seleniumbase-with-termux-python-psutil\", \"seleniumbase_platform_shim\"]' python scripts/main.py verify-version"
```

---

### 3. Handling Mirror Update Failures (Important Edge Case)
During the execution of `pkg install` (e.g., within `init_termux.sh`), package installation may fail due to mirror errors or network issues such as:
- `404 Not Found`
- `Repository Under Maintenance`
- `Unable to locate package` (temporary repository errors)

These errors are **NOT bugs or breaks in the written code**, but rather temporary issues with the official Termux mirror servers.
- When the agent encounters a mirror error, DO NOT attempt to modify the code or alter the logic.
- Simply inform the user by clearly separating the context: "The package installation failed due to a Termux mirror server issue, not a code defect. We should try again later or change the mirror."

---

### 4. Running Full CI Pipeline with act
If a full CI simulation is required from scratch using GitHub Actions, use the `act` CLI. When doing so, you must specify the custom runner image to ensure compatibility:
```bash
act -P ubuntu-latest=catthehacker/ubuntu:act-latest
```
