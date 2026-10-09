#!/usr/bin/env bash
# pre-commit hook - тверда точка контролю перед кожним комітом.
# Спершу лінтер, потім тести. Якщо будь-що падає - коміт блокується (exit 1),
# а вивід падіння друкується як сигнал зворотного звʼязку (feedback signal):
# модель або людина бачить рівно ту команду й той вивід, що зупинили коміт.
#
# Як поставити:
#   1. Скопіюй у `.git/hooks/pre-commit` свого репозиторію.
#   2. Зроби виконуваним: `chmod +x .git/hooks/pre-commit`.
#   3. Заміни значення двох змінних нижче під свій стек.
#
# Плейсхолдери (заміни рядок-значення, лапки лишаються):
#   <LINT_CMD>  - команда лінтера (наприклад `ruff check .` / `golangci-lint run` / `npm run lint`)
#   <TEST_CMD>  - команда тестів (наприклад `pytest -q` / `go test ./...` / `npm test`)

set -uo pipefail

LINT_CMD="<LINT_CMD>"   # напр. "ruff check ." / "golangci-lint run" / "npm run lint"
TEST_CMD="<TEST_CMD>"   # напр. "pytest -q" / "go test ./..." / "npm test"

echo "pre-commit: lint → tests"

# --- 1. Лінт -------------------------------------------------------------------
if ! eval "$LINT_CMD"; then
  echo "" >&2
  echo "pre-commit BLOCKED: лінтер впав ($LINT_CMD)." >&2
  echo "Це сигнал зворотного звʼязку: виправ зауваження вище і спробуй коміт знову." >&2
  exit 1
fi

# --- 2. Тести ------------------------------------------------------------------
if ! eval "$TEST_CMD"; then
  echo "" >&2
  echo "pre-commit BLOCKED: тести впали ($TEST_CMD)." >&2
  echo "Це сигнал зворотного звʼязку: доведи тести до зеленого перед комітом." >&2
  exit 1
fi

echo "pre-commit OK: лінт і тести зелені - коміт дозволено."
exit 0
