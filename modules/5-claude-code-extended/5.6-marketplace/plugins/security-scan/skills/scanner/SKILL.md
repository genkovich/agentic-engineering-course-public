---
name: scanner
description: >
  Use when auditing a branch for security issues before push or release.
  Triggers on "security scan", "secret scan", "pre-push check",
  "audit this diff", "check for leaked credentials".
allowed-tools: Read, Bash, Grep
---

# Security Scanner

Audit the staged diff and dependencies for the five red flags the team has agreed never ship.

## Red flags

1. **Hardcoded secrets** — API keys, tokens, private keys, `.env` values committed inline. Patterns: `sk-`, `AKIA`, `xoxb-`, `ghp_`, `-----BEGIN`, `password=`, `api_key=`
2. **Dynamic code execution** — `eval(`, `exec(`, `Function(...)` from string input, `os.system`, `subprocess.run(..., shell=True)`, `child_process.exec` with interpolation
3. **Unvetted network destinations** — new outbound URLs not in `allowlist.txt`; `curl | sh` patterns; webhook endpoints without TLS
4. **Privilege escalation** — `sudo` invocations, writes to `~/.bashrc` or `~/.zshrc`, hooks that touch system paths, plugin code that reads files outside the project root
5. **Vulnerable dependencies** — high or critical advisories from `npm audit` or `pip-audit` on packages touched in this branch

## Workflow

1. Run `git diff --staged` and grep for each pattern above
2. Run the dependency audit on whichever manifest changed (`package.json`, `requirements.txt`, `go.mod`)
3. Summarize findings as a green/yellow/red gate and list every hit with file path and line number
4. If anything is red, refuse to approve push and list exact remediation steps

A passing scan is one where every grep returns empty and every audit reports zero high or critical issues.
