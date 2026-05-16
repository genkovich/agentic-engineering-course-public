#!/usr/bin/env bash
# Idempotent setup — re-runnable. Initializes git repos for each demo
# and installs dependencies. File contents are managed separately
# (already committed alongside this script).
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

init_repo() {
  local dir="$1"
  cd "$ROOT/$dir"
  if [ ! -d .git ]; then
    git init -q
    git add -A
    git commit -q -m "initial: $dir demo scaffold" || true
  fi
}

# 01-refactor — TS + Vitest
init_repo "01-refactor"
cd "$ROOT/01-refactor"
[ -d node_modules ] || npm install --silent

# 02-few-shot — empty repo, just cwd for claude
init_repo "02-few-shot"

# 03-race-condition — Go
init_repo "03-race-condition"

# 04-verification — Node + Express + Vitest
init_repo "04-verification"
cd "$ROOT/04-verification"
[ -d node_modules ] || npm install --silent

echo ""
echo "✅ Demo structure ready at $ROOT"
echo ""
echo "Next steps:"
echo "  1. cd into one of the demo dirs"
echo "  2. Start screen recorder (1920x1080 @ 30fps, mic OFF)"
echo "  3. Run: claude"
echo "  4. Paste the matching prompt from PROMPTS.md"
echo ""
echo "Between takes: git reset --hard HEAD"
