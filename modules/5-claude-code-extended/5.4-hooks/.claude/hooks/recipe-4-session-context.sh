#!/usr/bin/env bash
# Slide 6.4 — Session context re-injection
# Event: SessionStart, matcher: compact
# Все, що цей скрипт виводить у stdout, додається в контекст Claude.
# Дія: повернути критичний контекст після compaction (active feature, recent commits, conventions).
set -euo pipefail

cat <<'EOF'
[session-context reminder — re-injected after compact]

Active demo: hooks-toolkit (lecture 5.4 — Claude Code Hooks).
Conventions:
  - всі hook scripts у .claude/hooks/, executable, читають stdin JSON
  - блокуючі hooks → exit 2 + stderr; observability → "async": true
  - secrets-strip.py застосовуй ПЕРЕД будь-яким зовнішнім POST/append до trace
  - не редагуй .env/.git — recipe-2 заблокує
EOF

if command -v git >/dev/null 2>&1 && [ -d "${CLAUDE_PROJECT_DIR:-.}/.git" ]; then
  echo
  echo "Recent commits:"
  git -C "${CLAUDE_PROJECT_DIR:-.}" log --oneline -5 2>/dev/null || true
fi

exit 0
