#!/usr/bin/env bash
# run.sh — golden-task regression suite для .claude/ (лекція 10.3).
#
# Для кожного кейса cases/<case>/:
#   1. setup.sh  — чиста пісочниця tmp/run-<case>/: fixture + git init + засаджений
#                  стан + КОПІЯ .claude/, що тестується.
#   2. claude -p — реальний агент headless у пісочниці (через run_agent).
#   3. check.sh  — ДЕТЕРМІНОВАНІ асерти проти фінального стану (exit 0=PASS).
#   4. таблиця PASS/FAIL + сумарний cost/час.
#
# Коштує токени (як 7.2). Для CI/pre-commit без токенів є lint.sh (`make check`).
#
# Usage:
#   bash tests/agent/run.sh                 # усі кейси
#   bash tests/agent/run.sh route-auth      # один кейс (або: make evals-one CASE=route-auth)
#   BREAK=1 bash tests/agent/run.sh forbid-env-read   # «зламати конфіг» → eval має почервоніти
#
# Модель на 5.4 examples/test-isolation/run-isolation-tests.sh (кольорова матриця).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/common.sh
. "$SCRIPT_DIR/lib/common.sh"

CASES_DIR="$SCRIPT_DIR/cases"
ONLY="${1:-}"          # необов'язковий фільтр по імені кейса
export BREAK="${BREAK:-}"   # setup.sh кейса поважає BREAK, щоб демо «зламай конфіг»

declare -i PASS=0
declare -i FAIL=0
declare -a ROWS=()
TOTAL_COST="0"
START_TS="$(date +%s)"

run_one() {
  local case_dir="$1"
  local name; name="$(basename "$case_dir")"
  local setup="$case_dir/setup.sh"
  local prompt="$case_dir/prompt.md"
  local check="$case_dir/check.sh"

  if [ ! -f "$setup" ] || [ ! -f "$prompt" ] || [ ! -f "$check" ]; then
    ROWS+=("FAIL|$name|неповний кейс (треба prompt.md+setup.sh+check.sh)")
    FAIL+=1
    return
  fi

  printf "\n${C_BOLD}▶ %s${C_RESET}" "$name"
  [ -n "$BREAK" ] && printf "  ${C_YELLOW}[BREAK=on — guardrail навмисно прибрано]${C_RESET}"
  printf "\n"

  # 1) пісочниця
  local sb; sb="$(make_sandbox "$name")"

  # 2) setup кейса наповнює пісочницю (отримує шлях + BREAK через env)
  if ! SANDBOX="$sb" CASE_DIR="$case_dir" LIB_DIR="$SCRIPT_DIR/lib" \
        bash "$setup" "$sb" >"$sb/setup.log" 2>&1; then
    ROWS+=("FAIL|$name|setup.sh впав (див. $sb/setup.log)")
    FAIL+=1
    return
  fi

  # 3) реальний агент. Кейс може додати claude-флаги (напр. --agent ro-reviewer)
  #    через необов'язковий файл cases/<case>/claude-flags.
  local extra=()
  if [ -f "$case_dir/claude-flags" ]; then
    # shellcheck disable=SC2162
    read -r -a extra < "$case_dir/claude-flags"
  fi
  printf "  ${C_DIM}claude -p … (це коштує токени)${C_RESET}\n"
  local transcript; transcript="$(run_agent "$sb" "$prompt" ${extra[@]+"${extra[@]}"})"
  local cost turns
  cost="$(transcript_cost "$transcript")"
  turns="$(transcript_turns "$transcript")"
  [ -n "$cost" ] && TOTAL_COST="$(awk "BEGIN{printf \"%.4f\", ${TOTAL_COST:-0}+${cost:-0}}")"

  # 4) детермінований чекер
  local check_out rc
  check_out="$(SANDBOX="$sb" TRANSCRIPT="$transcript" CASE_DIR="$case_dir" \
               LIB_DIR="$SCRIPT_DIR/lib" bash "$check" 2>&1)"
  rc=$?
  printf '%s\n' "$check_out"

  local detail="cost=\$${cost:-?} turns=${turns:-?}"
  if [ "$rc" -eq 0 ]; then
    PASS+=1
    ROWS+=("PASS|$name|$detail")
  else
    FAIL+=1
    ROWS+=("FAIL|$name|$detail")
  fi
}

# --- Збираємо список кейсів --------------------------------------------------
declare -a CASE_DIRS=()
if [ -n "$ONLY" ]; then
  if [ -d "$CASES_DIR/$ONLY" ]; then
    CASE_DIRS=("$CASES_DIR/$ONLY")
  else
    echo "Кейс '$ONLY' не знайдено в $CASES_DIR" >&2
    exit 2
  fi
else
  for d in "$CASES_DIR"/*/; do
    [ -d "$d" ] && CASE_DIRS+=("${d%/}")
  done
fi

if [ "${#CASE_DIRS[@]}" -eq 0 ]; then
  echo "Немає кейсів у $CASES_DIR" >&2
  exit 2
fi

printf "${C_BOLD}🧪 golden-task eval suite — реальний claude -p${C_RESET}\n"
printf "${C_DIM}кейсів: %s · пісочниці: tmp/run-*/${C_RESET}\n" "${#CASE_DIRS[@]}"

for d in "${CASE_DIRS[@]}"; do
  run_one "$d"
done

# --- Підсумкова матриця ------------------------------------------------------
ELAPSED=$(( $(date +%s) - START_TS ))
printf "\n${C_BOLD}Підсумок:${C_RESET}\n"
printf "%-2s  %-28s %s\n" "" "Кейс" "Деталі"
printf "%-2s  %s\n" "" "------------------------------------------------------------"
for r in "${ROWS[@]}"; do
  IFS='|' read -r status name detail <<<"$r"
  if [ "$status" = "PASS" ]; then
    printf "${C_GREEN}✓${C_RESET}  %-28s ${C_DIM}%s${C_RESET}\n" "$name" "$detail"
  else
    printf "${C_RED}✗${C_RESET}  %-28s ${C_RED}%s${C_RESET}\n" "$name" "$detail"
  fi
done

TOTAL=$((PASS + FAIL))
printf "\n${C_DIM}час: %sс · сумарний cost: ~\$%s${C_RESET}\n" "$ELAPSED" "$TOTAL_COST"
if [ "$FAIL" -eq 0 ]; then
  printf "${C_GREEN}${C_BOLD}Усі %s кейсів PASS.${C_RESET}\n" "$TOTAL"
  exit 0
fi
printf "${C_RED}${C_BOLD}%s з %s кейсів FAIL.${C_RESET}\n" "$FAIL" "$TOTAL"
exit 1
