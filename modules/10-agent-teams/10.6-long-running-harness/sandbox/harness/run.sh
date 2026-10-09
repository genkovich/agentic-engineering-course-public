#!/usr/bin/env bash
# Закадровий прогін довгограючого harness-а на грі hopper.
#
# ⚠️  ЦЕ ПЛАТНИЙ ПРОГІН: ~1-2 години роботи агента, орієнтовно $20-50 токенів.
#    Запускається СВІДОМО, з прапорцем --yes, зсередини sandbox/:
#        cd sandbox && bash harness/run.sh --yes
#
# Механіка: послідовні headless-сесії `claude -p`. Кожна сесія = свіже
# контекстне вікно (природний context reset); пам'ять між сесіями - лише
# диск: feature-list.json, claude-progress.txt, handoff.md, git.
# Після кожної пари coder→evaluator знімається зріз у ../run-artifacts/.
#
# Permissions - least privilege: режим acceptEdits + вузький allowlist
# у .claude/settings.json пісочниці (git, node, bash init.sh, Playwright MCP).
# Жодного глобального вимикання permission-воріт.
set -euo pipefail

[[ "${1:-}" == "--yes" ]] || {
  echo "Це платний прогін ~1-2 год (\$20-50 токенів)."
  echo "Запусти свідомо: bash harness/run.sh --yes (зсередини sandbox/)"
  exit 1
}

[[ -f CLAUDE.md && -d harness ]] || {
  echo "Схоже, ти не в sandbox/. Спершу: make sandbox && cd sandbox"; exit 1
}

MAX_SESSIONS="${MAX_SESSIONS:-14}"
ART="../run-artifacts"
mkdir -p "$ART"
CLAUDE_FLAGS=(--permission-mode acceptEdits)

remaining() {
  node -e "const f=require('./feature-list.json');process.stdout.write(String(f.features.filter(x=>!x.passes).length))" 2>/dev/null || echo "?"
}

snapshot() { # $1 = label
  local dir="$ART/$1"
  mkdir -p "$dir"
  cp -f feature-list.json "$dir/" 2>/dev/null || true
  cp -f handoff.md "$dir/" 2>/dev/null || true
  git log --oneline >"$dir/git-log.txt" 2>/dev/null || true
  echo "$(date '+%H:%M:%S')  залишилось фіч: $(remaining)" | tee -a "$ART/timeline.txt"
}

echo "=== Прогін старт: $(date) ===" | tee -a "$ART/timeline.txt"

# Сесія 0 - Initializer (лише якщо оточення ще не готове)
if [[ ! -f feature-list.json ]]; then
  echo "--- Initializer ---"
  claude -p "Прочитай harness/initializer.md і виконай цю роль для задачі з CLAUDE.md." "${CLAUDE_FLAGS[@]}"
  snapshot "00-init"
fi

for i in $(seq 1 "$MAX_SESSIONS"); do
  left="$(remaining)"
  echo "--- Сесія $i (залишилось фіч: $left) ---"
  [[ "$left" == "0" ]] && { echo "Усі фічі passes:true - фініш."; break; }

  claude -p "Прочитай harness/coder.md і виконай цю роль. Одна фіча за сесію." "${CLAUDE_FLAGS[@]}"
  claude -p "Прочитай harness/evaluator.md і виконай цю роль для поточного sprint-contract.md." "${CLAUDE_FLAGS[@]}"

  snapshot "$(printf '%02d' "$i")-session"
done

snapshot "99-final"
echo "=== Прогін фініш: $(date) ===" | tee -a "$ART/timeline.txt"
echo "Зрізи для таймлапсу - у $ART/"
