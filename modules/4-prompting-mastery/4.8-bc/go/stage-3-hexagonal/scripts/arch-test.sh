#!/usr/bin/env bash
# Обгортка над go-arch-lint, яка розрізняє два зовсім різні наслідки:
#   1) лінтер знайшов порушення меж   → показати список, віддати його код виходу
#   2) лінтер впав сам                → сказати про це прямо і теж вийти з 1
#
# Пункт 2 — не теорія. go-arch-lint v1.11.5 зібраний зі старим
# golang.org/x/tools, який не читає export-дані сучасного Go: він друкував
#   internal error: package "net/http" without types was imported from ...
# і повертав НУЛЬ. Тобто мовчки вдавав успіх — найгірший можливий режим
# для тесту, який має захищати архітектуру.

set -uo pipefail

VERSION="${ARCH_LINT_VERSION:-v1.17.0}"

echo "go-arch-lint ${VERSION}"
OUTPUT="$(GOFLAGS= go run "github.com/fe3dback/go-arch-lint@${VERSION}" check 2>&1)"
CODE=$?

# Підписи того, що лінтер зламався, а не знайшов проблему в коді.
if printf '%s' "$OUTPUT" | grep -qE 'internal error|panic:|without types was imported|failed to load packages|no required module provides'; then
	printf '%s\n' "$OUTPUT"
	cat <<'EOF'

✗ Лінтер ВПАВ САМ — це не архітектурне порушення.
  Найчастіша причина: версія лінтера зібрана зі старим golang.org/x/tools,
  який не вміє читати export-дані сучасного Go. Підпис саме такий:
  "without types was imported".

  Що перевірити:
    1. go version            — потрібен Go 1.25+
                               (або GOTOOLCHAIN=auto, щоб потрібний доїхав сам)
    2. ARCH_LINT_VERSION     — робоча версія v1.17.0; нижчі можуть бути зламані
    3. мережа / проксі       — перший запуск тягне лінтер з proxy.golang.org

  Немає локального Go взагалі? Запасний шлях: make arch-test-docker
  Детально: ../../TROUBLESHOOTING.md
EOF
	exit 1
fi

if [ "$CODE" -ne 0 ]; then
	printf '%s\n' "$OUTPUT"
	echo ""
	echo "✗ go-arch-lint знайшов порушення меж (список вище)."
	exit "$CODE"
fi

printf '%s\n' "$OUTPUT"
echo "✓ No violations found"
