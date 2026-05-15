#!/usr/bin/env bash
# Slide 5.5 — Test your hook in isolation.
# Прокидає sample JSON payloads через кожен з 5 хуків і перевіряє exit codes.
# Друкує кольорову PASS/FAIL матрицю — без живої сесії Claude.
#
# Usage: bash examples/test-isolation/run-isolation-tests.sh
#        або: make test-hooks (з hooks-toolkit/)
set -uo pipefail

# Resolve project root (works whether called via make or direct path)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PAYLOADS="$SCRIPT_DIR/payloads"
HOOKS="$ROOT/.claude/hooks"

# ANSI colors (no fancy CI detection — keep it simple)
GREEN="\033[32m"
RED="\033[31m"
DIM="\033[2m"
BOLD="\033[1m"
RESET="\033[0m"

declare -i PASS=0
declare -i FAIL=0
declare -a RESULTS=()

# Run a single test case.
# Args: 1=label  2=hook-script  3=payload-file  4=expected-exit  5=expected-stderr-substring (or -)
run_case() {
  local label="$1" hook="$2" payload="$3" expect_exit="$4" expect_stderr="$5"
  local stderr_file
  stderr_file="$(mktemp)"
  local actual_exit=0

  if [ ! -f "$hook" ]; then
    RESULTS+=("FAIL|$label|hook not found: $hook")
    FAIL+=1
    rm -f "$stderr_file"
    return
  fi
  if [ ! -f "$payload" ]; then
    RESULTS+=("FAIL|$label|payload not found: $payload")
    FAIL+=1
    rm -f "$stderr_file"
    return
  fi

  # Execute hook with payload
  if [[ "$hook" == *.py ]]; then
    cat "$payload" | python3 "$hook" 2>"$stderr_file" >/dev/null || actual_exit=$?
  else
    cat "$payload" | bash "$hook" 2>"$stderr_file" >/dev/null || actual_exit=$?
  fi

  local stderr_content
  stderr_content="$(cat "$stderr_file")"
  rm -f "$stderr_file"

  local pass_exit="no"
  if [ "$actual_exit" -eq "$expect_exit" ]; then
    pass_exit="yes"
  fi

  local pass_stderr="yes"
  if [ "$expect_stderr" != "-" ]; then
    if echo "$stderr_content" | grep -qF "$expect_stderr"; then
      pass_stderr="yes"
    else
      pass_stderr="no"
    fi
  fi

  if [ "$pass_exit" = "yes" ] && [ "$pass_stderr" = "yes" ]; then
    PASS+=1
    RESULTS+=("PASS|$label|exit=$actual_exit (expected $expect_exit)")
  else
    FAIL+=1
    local why="exit=$actual_exit (expected $expect_exit)"
    [ "$pass_stderr" = "no" ] && why="$why; stderr missing '$expect_stderr'"
    RESULTS+=("FAIL|$label|$why")
  fi
}

echo
echo -e "${BOLD}🧪 Hooks isolation test suite${RESET}"
echo -e "${DIM}runner: examples/test-isolation/run-isolation-tests.sh${RESET}"
echo

# === recipe-2: protect-files ===
run_case "protect-files: blocks .env"           "$HOOKS/recipe-2-protect-files.sh"  "$PAYLOADS/protect-env.json"   2 "BLOCKED"
run_case "protect-files: passes src/api.ts"     "$HOOKS/recipe-2-protect-files.sh"  "$PAYLOADS/protect-clean.json" 0 "-"

# === recipe-3: secrets-scan ===
run_case "secrets-scan: blocks eval()"          "$HOOKS/recipe-3-secrets-scan.py"   "$PAYLOADS/secrets-eval.json"  2 "SECURITY"
run_case "secrets-scan: passes JSON.parse"      "$HOOKS/recipe-3-secrets-scan.py"   "$PAYLOADS/secrets-clean.json" 0 "-"

# === recipe-5: git-policy (if-field demo) ===
run_case "git-policy: blocks force-push main"   "$HOOKS/recipe-5-git-policy.sh"     "$PAYLOADS/git-force-main.json" 2 "BLOCKED"
run_case "git-policy: passes ls -la"            "$HOOKS/recipe-5-git-policy.sh"     "$PAYLOADS/git-ls.json"        0 "-"

# === mcp-allowlist ===
run_case "mcp-allowlist: passes filesystem"     "$HOOKS/mcp-allowlist.sh"           "$PAYLOADS/mcp-allowed.json"   0 "-"
run_case "mcp-allowlist: denies github"         "$HOOKS/mcp-allowlist.sh"           "$PAYLOADS/mcp-denied.json"    0 "-"

# Print result table
echo -e "${BOLD}Results:${RESET}"
printf "%-2s  %-44s %s\n" "" "Test case" "Detail"
printf "%-2s  %s\n" "" "----------------------------------------------------------------------"
for r in "${RESULTS[@]}"; do
  IFS='|' read -r status label detail <<<"$r"
  if [ "$status" = "PASS" ]; then
    printf "${GREEN}✓${RESET}  %-44s ${DIM}%s${RESET}\n" "$label" "$detail"
  else
    printf "${RED}✗${RESET}  %-44s ${RED}%s${RESET}\n" "$label" "$detail"
  fi
done

echo
TOTAL=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
  echo -e "${GREEN}${BOLD}All $TOTAL tests passed.${RESET}"
  exit 0
else
  echo -e "${RED}${BOLD}$FAIL of $TOTAL tests failed.${RESET}"
  exit 1
fi
