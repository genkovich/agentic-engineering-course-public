#!/usr/bin/env bash
# Slide 11 — Stop hook як quality gate (ілюстрація).
# Event: Stop. За замовчуванням ВИМКНЕНО у settings.json (порожній hooks: []).
# Щоб увімкнути — перенеси команду з "_disabled_command" у hooks: [{type, command}].
#
# Демо-логіка: якщо у проєкті є package.json з npm test — запустити; якщо тести впали → decision:block,
# Claude Code не дасть зупинитись і повідомить чому. Це anti-pattern для більшості реальних проєктів
# (краще pre-commit, slide 9), але добре ілюструє structured JSON output.
set -euo pipefail

# stdin не використовуємо для ілюстрації — лише сигналізуємо рішення
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

if [ -f "$PROJECT_DIR/package.json" ] && command -v npm >/dev/null 2>&1; then
  if ! (cd "$PROJECT_DIR" && npm test --silent >/dev/null 2>&1); then
    cat <<'EOF'
{
  "decision": "block",
  "reason": "Stop hook quality gate: npm test failed. Fix tests before stopping."
}
EOF
    exit 0
  fi
fi

# all good → дозволити Stop
exit 0
