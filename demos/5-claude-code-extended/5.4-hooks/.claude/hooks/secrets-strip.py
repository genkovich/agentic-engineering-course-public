#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Spільний sanitizer для всіх debug/analytics hooks.
Stdin: JSON (hook payload АБО будь-який JSON).
Stdout: той самий JSON, але з замаскованими секретами/токенами/паролями.

Стратегія:
  1) Регекси на string-значеннях у будь-якій глибині — заміна збігу на ***REDACTED***.
  2) Імена ключів, що матчать r"(?i)(password|secret|token|api[_-]?key|authorization|bearer)"
     → значення повністю замінити на ***REDACTED***.
  3) Рядки виду KEY=VALUE з .env-патерну — замінити VALUE.

Викликається через pipe:
    cat payload.json | python3 secrets-strip.py
або як standalone з examples/secrets-strip-demo/.
"""
import json
import re
import sys
from typing import Any

REDACT = "***REDACTED***"

VALUE_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{40,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    re.compile(r"-----BEGIN[^-]+PRIVATE KEY-----[\s\S]+?-----END[^-]+PRIVATE KEY-----"),
]

ENV_LINE = re.compile(r"^([A-Z][A-Z0-9_]+)\s*=\s*(.+)$", re.MULTILINE)
SENSITIVE_KEY = re.compile(
    r"(?i)(password|secret|token|api[_-]?key|apikey|authorization|bearer|client[_-]?secret)"
)


def scrub_string(s: str) -> str:
    out = s
    for p in VALUE_PATTERNS:
        out = p.sub(REDACT, out)
    out = ENV_LINE.sub(lambda m: f"{m.group(1)}={REDACT}", out)
    return out


def scrub(node: Any) -> Any:
    if isinstance(node, dict):
        clean = {}
        for k, v in node.items():
            if isinstance(k, str) and SENSITIVE_KEY.search(k):
                clean[k] = REDACT
            else:
                clean[k] = scrub(v)
        return clean
    if isinstance(node, list):
        return [scrub(x) for x in node]
    if isinstance(node, str):
        return scrub_string(node)
    return node


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        sys.stdout.write(scrub_string(raw))
        return 0
    json.dump(scrub(data), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
