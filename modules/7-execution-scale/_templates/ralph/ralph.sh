#!/usr/bin/env bash
# Ralph loop - канонічний патерн Geoffrey Huntley з трьома запобіжниками.
# Шаблон стек-агностик: він НЕ знає твоєї мови чи тестової команди.
# Усе, що стосується стека, живе у PROMPT.md (його цей скрипт читає як вхід)
# і в CLAUDE.md. Скрипт лишається без змін на будь-якому стеку.
#
# Цикл навмисно тупий: він повторно проганяє ОДИН промпт через `claude -p`
# (headless - без інтерактивної сесії; свіжий контекст щоходу), доки модель
# не створить файл `DONE`. Усе, що має пережити між ходами, лежить на диску
# (git, трекер задач), а не в памʼяті моделі.

set -euo pipefail

# --- Ручки (перевизначай через змінні оточення) ---------------------------
MAX_ITER="${MAX_ITER:-10}"          # Запобіжник 1: тверда стеля кількості ітерацій
PROMPT_FILE="${PROMPT_FILE:-PROMPT.md}"
COST_LOG="${COST_LOG:-cost.log}"    # Запобіжник 2: аудит-лог по кожному ходу
PERMISSION_MODE="${PERMISSION_MODE:-acceptEdits}"

ITER=0

if [ ! -f "$PROMPT_FILE" ]; then
  echo "No $PROMPT_FILE found. Скопіюй PROMPT.template.md у PROMPT.md і заповни плейсхолдери." >&2
  exit 2
fi

echo "=== Ralph run started: $(date -Iseconds) (prompt=$PROMPT_FILE, max_iter=$MAX_ITER) ===" >> "$COST_LOG"

# --- Запобіжник 3: акуратний Ctrl-C ---------------------------------------
trap 'echo "Interrupted at iteration $ITER. State preserved - check git status."' INT

# --- Цикл -----------------------------------------------------------------
while [ ! -f DONE ]; do
  ITER=$((ITER + 1))

  if [ "$ITER" -gt "$MAX_ITER" ]; then
    echo "Iteration limit ($MAX_ITER) reached. Exiting without DONE."
    echo "=== Hit MAX_ITER at $(date -Iseconds) ===" >> "$COST_LOG"
    exit 1
  fi

  echo "--- Iteration $ITER ---"
  echo "$(date -Iseconds) iter=$ITER" >> "$COST_LOG"

  # Холодний старт щоходу: свіжий виклик `claude -p` без накопиченого контексту.
  # Модель наново перечитує PROMPT.md і поточний стан файлів з нуля - саме це
  # рятує від context rot (поступове псування контексту) на довгих прогонах.
  claude -p "$(cat "$PROMPT_FILE")" --permission-mode "$PERMISSION_MODE"

  sleep 1   # щоб Ctrl-C між ходами спрацьовував надійно
done

echo "=== DONE found at $(date -Iseconds), total iterations: $ITER ===" >> "$COST_LOG"
echo "Ralph completed in $ITER iterations. Check 'git log' for results."
