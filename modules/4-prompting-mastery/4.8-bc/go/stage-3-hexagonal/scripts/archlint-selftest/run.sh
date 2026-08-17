#!/usr/bin/env bash
# Негативний контроль для arch-lint.
#
# `make arch-test` на чистому коді друкує "порушень немає" — і рівно те саме
# по суті друкував зламаний лінтер, який взагалі нічого не аналізував.
# Відрізнити ці два стани можна лише одним способом: дати лінтеру код,
# де порушення Є, і переконатися, що він його бачить.
#
# Тут поруч лежить крихітний окремий Go-модуль: пакет `a` імпортує `b`,
# а конфіг це забороняє. Успіх цього скрипта = НЕНУЛЬОВИЙ код від лінтера.

set -uo pipefail

cd "$(dirname "$0")" || exit 1

VERSION="${ARCH_LINT_VERSION:-v1.17.0}"

echo "Негативний контроль: лінтер має знайти навмисне порушення a → b"
OUTPUT="$(GOFLAGS= go run "github.com/fe3dback/go-arch-lint@${VERSION}" check 2>&1)"
CODE=$?

if printf '%s' "$OUTPUT" | grep -qE 'internal error|panic:|without types was imported|failed to load packages'; then
	printf '%s\n' "$OUTPUT"
	echo ""
	echo "✗ Лінтер впав сам. Дивись розділ про arch-lint у ../../../../TROUBLESHOOTING.md"
	exit 1
fi

if [ "$CODE" -eq 0 ]; then
	printf '%s\n' "$OUTPUT"
	cat <<'EOF'

✗ Лінтер НЕ побачив навмисного порушення і повернув нуль.
  Це означає, що арх-тести в цьому проєкті зараз нічого не захищають:
  зелений `make arch-test` більше не є доказом чистих меж.
  Не довіряй результатам arch-test, поки цей контроль не стане зеленим.
EOF
	exit 1
fi

echo "✓ Лінтер коректно ловить порушення."
