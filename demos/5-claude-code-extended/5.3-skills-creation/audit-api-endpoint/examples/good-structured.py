#!/usr/bin/env python3
"""Good pattern: stdout is machine-readable JSON only. Diagnostics,
progress, warnings go to stderr where the agent expects them. Tools
like jq, grep, and pipelines compose cleanly.
"""
import json
import sys


def log(msg: str) -> None:
    print(f"[audit] {msg}", file=sys.stderr)


def main() -> int:
    log("server not responding, using static analysis only")
    log("scanned 12 Go files")
    payload = {
        "endpoint": "/health",
        "findings": [
            {"category": "observability", "severity": "warning", "file": "api/server.go", "line": 32,
             "message": "no log call in handler"},
            {"category": "health", "severity": "warning", "file": "api/server.go", "line": 35,
             "message": "uptime-only health check"},
        ],
    }
    print(json.dumps(payload, indent=2))
    return 1 if payload["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
