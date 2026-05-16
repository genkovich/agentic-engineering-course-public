#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Slide 6.3 — Secrets-scan / security-guidance pattern.
Event: PreToolUse, matcher: Edit|Write|MultiEdit.
Скрипт читає stdin JSON (Claude Code hook payload), перевіряє content на:
  - hardcoded API keys (sk-, ghp_, xox[baprs]-, AIza, AKIA, eyJhbGciOi)
  - небезпечні патерни: eval(, innerHTML, dangerouslySetInnerHTML,
    child_process.exec, os.system, subprocess.Popen(shell=True), pickle.loads
  - GitHub Actions command injection (${{ github.event.* }} в run:)
exit 2 + stderr → Claude Code блокує запис і показує warning.
exit 0 → дозвіл.
"""
import json
import re
import sys

PATTERNS = [
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI/Anthropic-style API key"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub personal access token"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"AIza[0-9A-Za-z\-_]{35}", "Google API key"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"-----BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----", "Private key block"),
    (r"\beval\s*\(", "eval() — code injection risk"),
    (r"\binnerHTML\s*=", "innerHTML assignment — XSS risk"),
    (r"dangerouslySetInnerHTML", "React dangerouslySetInnerHTML — XSS risk"),
    (r"child_process\.(exec|execSync)\s*\(", "child_process.exec — command injection"),
    (r"\bos\.system\s*\(", "os.system — command injection"),
    (r"subprocess\.[A-Za-z_]+\([^)]*shell\s*=\s*True", "subprocess shell=True — injection"),
    (r"pickle\.loads?\s*\(", "pickle deserialization — RCE risk"),
    (r"\$\{\{\s*github\.(event|head_ref|pull_request)\.[^}]+\}\}", "GHA command injection vector"),
]


def extract_content(payload: dict) -> str:
    ti = payload.get("tool_input", {})
    parts = [
        ti.get("content", ""),
        ti.get("new_string", ""),
        ti.get("old_string", ""),
    ]
    for edit in ti.get("edits", []) or []:
        parts.append(edit.get("new_string", ""))
        parts.append(edit.get("old_string", ""))
    return "\n".join(p for p in parts if isinstance(p, str))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    content = extract_content(payload)
    if not content:
        return 0

    findings = []
    for pat, label in PATTERNS:
        m = re.search(pat, content)
        if m:
            findings.append(f"  · {label}: matched /{pat}/")

    if findings:
        print("SECURITY WARNING (recipe-3-secrets-scan):", file=sys.stderr)
        print("\n".join(findings), file=sys.stderr)
        print(
            "\nReview the diff and either rewrite the unsafe construct or move "
            "secrets to environment variables / a secret manager.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
