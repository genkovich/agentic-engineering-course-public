#!/usr/bin/env bash
# lint.sh — ДЕТЕРМІНОВАНИЙ драй-ран без токенів (`make check`).
#
# Це CI-/pre-commit-безпечний шар: він НЕ запускає агента і має бути зеленим на
# чистому checkout. Перевіряє три речі:
#   1. `bash -n` (синтаксис) усіх скриптів harness-а й кейсів.
#   2. Структура: кожен cases/<case>/ має prompt.md + setup.sh + check.sh.
#   3. Структурний lint: setup.sh/check.sh мають shebang; check.sh згадує exit-вердикт.
#
# Контраст із run.sh: run.sh ловить РЕГРЕСІЇ конфігурації (коштує токени), lint.sh
# ловить ПОЛАМАНИЙ harness (безкоштовно, у CI на кожен PR).

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/lib/common.sh"

CASES_DIR="$SCRIPT_DIR/cases"
declare -i FAILS=0

ok()   { printf "  ${C_GREEN}✓${C_RESET} %s\n" "$1"; }
bad()  { printf "  ${C_RED}✗${C_RESET} %s\n" "$1"; FAILS=$((FAILS + 1)); }

printf "${C_BOLD}🔎 make check — детермінований драй-ран (без токенів)${C_RESET}\n\n"

# --- 1. bash -n на ядрі ------------------------------------------------------
printf "${C_BOLD}1. Синтаксис harness-скриптів${C_RESET}\n"
for f in "$SCRIPT_DIR/run.sh" "$SCRIPT_DIR/lint.sh" "$SCRIPT_DIR/lib/common.sh"; do
  if bash -n "$f" 2>/dev/null; then ok "bash -n $(basename "$f")"; else bad "bash -n $(basename "$f")"; fi
done

# --- 2 & 3. Кейси ------------------------------------------------------------
printf "\n${C_BOLD}2. Повнота й синтаксис кейсів${C_RESET}\n"
shopt -s nullglob 2>/dev/null || true
found_case=0
for d in "$CASES_DIR"/*/; do
  [ -d "$d" ] || continue
  found_case=1
  name="$(basename "$d")"
  for req in prompt.md setup.sh check.sh; do
    if [ -f "$d/$req" ]; then ok "$name/$req є"; else bad "$name/$req ВІДСУТНІЙ"; fi
  done
  for s in setup.sh check.sh; do
    [ -f "$d/$s" ] || continue
    if bash -n "$d/$s" 2>/dev/null; then ok "$name/$s — синтаксис ок"; else bad "$name/$s — синтаксична помилка"; fi
    if head -n1 "$d/$s" | grep -q '^#!'; then :; else bad "$name/$s — без shebang"; fi
  done
  # check.sh має нести явний вердикт-вихід.
  if [ -f "$d/check.sh" ]; then
    if grep -qE 'exit[[:space:]]+\$?\{?FAILED' "$d/check.sh" || grep -qE 'exit[[:space:]]+[01]' "$d/check.sh"; then
      ok "$name/check.sh — має exit-вердикт"
    else
      bad "$name/check.sh — немає явного exit 0/1"
    fi
  fi
done

if [ "$found_case" -eq 0 ]; then
  bad "у $CASES_DIR немає жодного кейса"
fi

# --- 4. Fixtures, на які посилаються setup.sh, існують -----------------------
printf "\n${C_BOLD}3. Fixtures на місці${C_RESET}\n"
if [ -d "$FIXTURES_DIR" ]; then
  for d in "$CASES_DIR"/*/; do
    [ -f "$d/setup.sh" ] || continue
    name="$(basename "$d")"
    # Витягуємо аргументи copy_fixture <name> зі setup.sh.
    grep -oE 'copy_fixture[[:space:]]+[A-Za-z0-9_./-]+' "$d/setup.sh" 2>/dev/null \
      | awk '{print $2}' | while read -r fx; do
        [ -z "$fx" ] && continue
        if [ -d "$FIXTURES_DIR/$fx" ]; then ok "$name → fixtures/$fx"; else bad "$name → fixtures/$fx ВІДСУТНІЙ"; fi
      done
  done
else
  bad "директорія fixtures/ відсутня"
fi

printf "\n"
if [ "$FAILS" -eq 0 ]; then
  printf "${C_GREEN}${C_BOLD}make check OK — harness структурно цілий.${C_RESET}\n"
  exit 0
fi
printf "${C_RED}${C_BOLD}make check FAIL — %s проблем.${C_RESET}\n" "$FAILS"
exit 1
