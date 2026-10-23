#!/usr/bin/env bash
# Ставить залежності для демо уроку «Як писати промпти». Можна запускати повторно.
# Окремі git-репозиторії не створює: між прогонами повертайте теку в початковий
# стан командами з README.md (node_modules ігнорує .gitignore курсу).
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

for dir in 01-refactor 04-verification; do
  echo "npm install: $dir"
  (cd "$ROOT/$dir" && npm install --silent)
done

if command -v go >/dev/null 2>&1; then
  echo "go: $(go version)"
else
  echo "Go не знайдено: для 03-race-condition поставте Go 1.22+."
fi

echo ""
echo "Готово. Промпти лежать у PROMPTS.md, порядок роботи в README.md."
