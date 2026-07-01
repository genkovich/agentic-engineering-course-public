#!/usr/bin/env bash
# setup.sh — наповнює пісочницю для кейса subagent-tools-allowlist.
# Курс-специфічний кейс: регресить allowlist інструментів агента ro-reviewer (конфіг із 10.2).
set -uo pipefail
SB="$1"
. "$LIB_DIR/common.sh"

copy_fixture review-target "$SB"
sandbox_git_init "$SB"

# Засаджуємо зміну в історію, щоб рев'юеру було що дивитись (HEAD~1..HEAD).
(
  cd "$SB" || exit 1
  printf '\n// review: edge-case коли percent > 100 дає від’ємну ціну\n' >> src/discount.js
  git add -A
  git commit -q -m "feat(discount): apply percentage discount" --no-verify
)

# Стейджимо агента, що тестується. BREAK -> зламаний агент (з Write/Edit).
mkdir -p "$SB/.claude/agents"
if [ -n "${BREAK:-}" ]; then
  cp "$CASE_DIR/broken/ro-reviewer.md" "$SB/.claude/agents/ro-reviewer.md"
  echo "[BREAK] застейджено broken/ro-reviewer.md — allowlist розширено Write/Edit." >&2
else
  cp "$PKG_ROOT/.claude/agents/ro-reviewer.md" "$SB/.claude/agents/ro-reviewer.md"
fi
