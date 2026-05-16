#!/usr/bin/env bash
# Slide 6 — end-to-end тур по 4 рецептах за один прогін.
# Кожен рецепт виконується на своєму fixture з examples/test-isolation/payloads/.
# Друкуємо заголовок Recipe N/4, потім результат, у кінці — підсумкова таблиця.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PAYLOADS="$ROOT/examples/test-isolation/payloads"
HOOKS="$ROOT/.claude/hooks"

GREEN="\033[32m"
RED="\033[31m"
DIM="\033[2m"
BOLD="\033[1m"
CYAN="\033[36m"
RESET="\033[0m"

declare -i PASS=0
declare -i FAIL=0
declare -a SUMMARY=()

section() {
  echo
  echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${CYAN}${BOLD}  Recipe $1/4 — $2${RESET}"
  echo -e "${CYAN}${BOLD}  $3${RESET}"
  echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
}

# Args: 1=recipe-name 2=hook-script 3=payload 4=expected-exit
run_step() {
  local name="$1" hook="$2" payload="$3" expect_exit="$4"
  local actual_exit=0
  local stderr_file
  stderr_file="$(mktemp)"

  if [[ "$hook" == *.py ]]; then
    cat "$payload" | python3 "$hook" 2>"$stderr_file" >/dev/null || actual_exit=$?
  else
    cat "$payload" | bash "$hook" 2>"$stderr_file" >/dev/null || actual_exit=$?
  fi

  echo -e "${DIM}payload:${RESET} $(basename "$payload")"
  echo -e "${DIM}hook:   ${RESET} $(basename "$hook")"
  echo -e "${DIM}stderr: ${RESET}"
  if [ -s "$stderr_file" ]; then
    sed 's/^/    /' "$stderr_file"
  else
    echo "    (empty)"
  fi
  echo -e "${DIM}exit:   ${RESET} $actual_exit (expected $expect_exit)"
  rm -f "$stderr_file"

  if [ "$actual_exit" -eq "$expect_exit" ]; then
    echo -e "${GREEN}  ✓ PASS${RESET}"
    PASS+=1
    SUMMARY+=("PASS|$name")
  else
    echo -e "${RED}  ✗ FAIL${RESET}"
    FAIL+=1
    SUMMARY+=("FAIL|$name")
  fi
}

echo
echo -e "${BOLD}🎬 Recipes tour — 4 рецепти за один прогін${RESET}"
echo -e "${DIM}see also: examples/trigger-scenarios/ for live Claude Code prompts${RESET}"

# Recipe 1: Auto-format. Hook is non-blocking (PostToolUse) — recipe-1 itself doesn't format
# in isolation (no real file on disk). We assert the script runs cleanly with exit 0 on a
# clean payload that has no file to format.
section 1 "Auto-format" "PostToolUse + Edit|Write — formatter за розширенням"
run_step "auto-format runs cleanly" \
  "$HOOKS/recipe-1-auto-format.sh" \
  "$PAYLOADS/protect-clean.json" \
  0

# Recipe 2: File protection
section 2 "File protection" "PreToolUse + exit 2 — блокує до виконання"
run_step "blocks .env writes" \
  "$HOOKS/recipe-2-protect-files.sh" \
  "$PAYLOADS/protect-env.json" \
  2

# Recipe 3: Secrets-scan
section 3 "Secrets-scan" "PreToolUse + Python regex — еквівалент security-guidance"
run_step "blocks eval()" \
  "$HOOKS/recipe-3-secrets-scan.py" \
  "$PAYLOADS/secrets-eval.json" \
  2

# Recipe 4: Session re-inject
# In isolation we just verify the script runs and prints content (exit 0). Live demo: /compact in Claude.
section 4 "Session re-inject" "SessionStart matcher=compact — stdout → context"
echo -e "${DIM}simulating /compact event (stdin payload — minimal)${RESET}"
echo -e "${DIM}stdout (this is what gets injected back into Claude context):${RESET}"
echo "    ───────────────────────────────────────────────────"
echo '{"matcher":"compact"}' | bash "$HOOKS/recipe-4-session-context.sh" 2>/dev/null | sed 's/^/    /' || true
echo "    ───────────────────────────────────────────────────"
echo '{"matcher":"compact"}' | bash "$HOOKS/recipe-4-session-context.sh" >/dev/null 2>&1
recipe4_exit=$?
echo -e "${DIM}exit:   ${RESET} $recipe4_exit (expected 0)"
if [ "$recipe4_exit" -eq 0 ]; then
  echo -e "${GREEN}  ✓ PASS${RESET}"
  PASS+=1
  SUMMARY+=("PASS|session re-inject prints content")
else
  echo -e "${RED}  ✗ FAIL${RESET}"
  FAIL+=1
  SUMMARY+=("FAIL|session re-inject prints content")
fi

# Final summary
echo
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}  Tour summary${RESET}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
for r in "${SUMMARY[@]}"; do
  IFS='|' read -r status label <<<"$r"
  if [ "$status" = "PASS" ]; then
    echo -e "  ${GREEN}✓${RESET} $label"
  else
    echo -e "  ${RED}✗${RESET} $label"
  fi
done

echo
TOTAL=$((PASS + FAIL))
if [ "$FAIL" -eq 0 ]; then
  echo -e "${GREEN}${BOLD}Tour complete: $TOTAL/$TOTAL recipes pass.${RESET}"
  echo -e "${DIM}Next step: try the live versions via examples/trigger-scenarios/trigger-*.md inside Claude Code.${RESET}"
  exit 0
else
  echo -e "${RED}${BOLD}Tour failed: $FAIL of $TOTAL recipes failed.${RESET}"
  exit 1
fi
