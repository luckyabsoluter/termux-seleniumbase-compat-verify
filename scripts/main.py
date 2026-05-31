import importlib
import sys

COMMANDS = {
    "classify-failure": "termux_compat.classify_failure",
    "collect-env-snapshot": "termux_compat.collect_env_snapshot",
    "resolve-deps": "termux_compat.resolve_termux_native_deps",
    "verify-deps": "termux_compat.verify_termux_native_deps",
    "verify-version": "termux_compat.verify_version",
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: {sys.argv[0]} <subcommand> [args...]", file=sys.stderr)
        print("Available subcommands:", file=sys.stderr)
        for cmd in COMMANDS:
            print(f"  {cmd}", file=sys.stderr)
        sys.exit(1)

    subcommand = sys.argv[1]
    
    # Rewrite sys.argv so subcommands parse arguments correctly
    sys.argv = [f"{sys.argv[0]} {subcommand}"] + sys.argv[2:]
    
    module = importlib.import_module(COMMANDS[subcommand])
    module.main()

if __name__ == "__main__":
    main()
