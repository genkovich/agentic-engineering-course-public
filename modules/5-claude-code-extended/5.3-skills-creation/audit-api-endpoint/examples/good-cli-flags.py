#!/usr/bin/env python3
"""Good pattern: every input is a flag, defaults are explicit, --yes
suppresses any optional confirmation. Runs to completion in non-TTY
context, returns a JSON line on stdout, exits 0.
"""
import argparse
import json


def main() -> int:
    p = argparse.ArgumentParser(description="Pretend to audit an endpoint.")
    p.add_argument("--target", required=True, help="path to project root")
    p.add_argument("--endpoint", required=True, help="endpoint to audit, e.g. /health")
    p.add_argument("--yes", action="store_true", help="skip any confirmation prompts")
    args = p.parse_args()

    print(json.dumps({
        "endpoint": args.endpoint,
        "target": args.target,
        "would_run": True,
        "confirmed": args.yes,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
