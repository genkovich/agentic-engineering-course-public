#!/usr/bin/env bash
# redteam-scan.sh — run YOUR OWN .claude/ config through the "how could this be
# broken?" checklist. This is the practice from the lecture: stop reading your
# config as an author and start reading it as an attacker.
#
# Usage: bash scripts/redteam-scan.sh [target-dir]   (default: current dir)
# Prints one line per check: FAIL (attackable) / PASS / WARN. Nothing is fixed.
set -uo pipefail

TARGET="${1:-.}"
SETTINGS="$TARGET/.claude/settings.json"
GITIGNORE="$TARGET/.gitignore"
fail=0

hr() { printf '%s\n' "----------------------------------------------------------------"; }
check() { # <verdict> <label> <detail>
  printf '  %-6s %s\n' "$1" "$2"
  [ -n "${3:-}" ] && printf '         %s\n' "$3"
  [ "$1" = "FAIL" ] && fail=$((fail+1))
}

echo "red-team scan of $TARGET/.claude/"
hr

if [ ! -f "$SETTINGS" ]; then
  check "WARN" "no .claude/settings.json found" "config lives in defaults — inspect the effective policy with /permissions"
else
  # 1. unscoped Bash — the single widest hole (bash bypasses tool-level deny)
  if grep -qE '"Bash"|"Bash\(\*\)"|"Bash\(:\*\)"' "$SETTINGS"; then
    check "FAIL" "Bash allowed unscoped" "any command runs, incl. curl/cat .env — scope to Bash(git status:*) etc."
  else
    check "PASS" "Bash is command-scoped"
  fi

  # 2. WebFetch with no domain restriction = an open egress channel
  if grep -qE '"WebFetch"([^(]|$)' "$SETTINGS"; then
    check "FAIL" "WebFetch allowed without a domain" "open exfil channel — pin WebFetch(domain:docs.example.com)"
  else
    check "PASS" "WebFetch domain-scoped or off"
  fi

  # 3. MCP wildcard trust
  if grep -qE '"mcp__\*"|"mcp__[a-z_-]+"([^_]|$)' "$SETTINGS"; then
    check "FAIL" "MCP server trusted by wildcard" "name each tool: mcp__server__specific_tool, not mcp__server"
  else
    check "PASS" "no MCP wildcard allow"
  fi

  # 4. dangerous default mode
  if grep -qE '"defaultMode"\s*:\s*"(bypassPermissions|acceptEdits)"' "$SETTINGS"; then
    m="$(grep -oE '"defaultMode"\s*:\s*"[a-zA-Z]+"' "$SETTINGS")"
    check "FAIL" "risky defaultMode" "$m — unattended prod agents should not auto-accept"
  else
    check "PASS" "defaultMode is manual/plan"
  fi

  # 5. no deny list for secrets
  if grep -qE 'Read\(\*\*/\.env\)|Read\(\.env\)|Read\(~/\.ssh' "$SETTINGS"; then
    check "PASS" "secret paths denied for built-in reads"
  else
    check "FAIL" "no Read-deny for secret paths" "add Read(.env), Read(**/*.pem), Read(~/.ssh/**)"
  fi

  # 6. no egress guard hook
  if grep -qE '"PreToolUse"' "$SETTINGS"; then
    check "PASS" "a PreToolUse hook is wired"
  else
    check "FAIL" "no PreToolUse egress guard" "read-deny is theatre without an egress hook — see hardened fixture"
  fi
fi

# 7. secrets not gitignored
if [ -f "$GITIGNORE" ] && grep -qE '(^|/)\.env' "$GITIGNORE"; then
  check "PASS" ".env is gitignored"
else
  check "FAIL" ".env not in .gitignore" "one git add -A away from committing the key"
fi

hr
if [ "$fail" -gt 0 ]; then
  echo "  $fail attackable finding(s). This config would leak under one injected ticket."
else
  echo "  no attackable findings on this checklist."
fi
# informational, not a CI gate in the demo
exit 0
