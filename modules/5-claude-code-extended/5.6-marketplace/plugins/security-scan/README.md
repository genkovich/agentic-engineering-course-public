# security-scan

## Purpose

Catch the five classes of security mistakes that cost teams time post-incident: leaked secrets, dynamic code execution, unvetted network destinations, privilege escalation, and vulnerable dependencies. One command, one skill, run before every push.

## Install

```
/plugin install security-scan@team-marketplace
```

## Commands

- `/security-scan:scan` — runs the full pre-push security audit over the staged diff and dependency manifests, returns a green/yellow/red gate.

## Skills

- `scanner` — auto-triggers when the user asks to "scan", "audit this diff", "check for leaked credentials", "security review". Greps for known secret patterns, scans for dangerous calls (`eval`, `shell=True`), audits dependencies, and lists every red flag with file path and line number.

## Hooks

—
