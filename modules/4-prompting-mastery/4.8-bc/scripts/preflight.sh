#!/usr/bin/env bash
# Самодіагностика демо 4.8-bc.
#
# Викликається з теки стейджа: bash ../../scripts/preflight.sh <go|ts|py> <1|2|3>
# Її запускає `make doctor`, і вона ж стоїть перед `make install` —
# щоб діагностика працювала завжди, а не тоді, коли студент про неї згадає.
#
# Три рівні:
#   ✓  все гаразд
#   !  попередження — працювати можна, але знай про це (exit 0)
#   ✗  блокер — далі йти немає сенсу (exit 1)
#
# Свідомо без jq і без `sort -V`: перший є не скрізь, другий на macOS (BSD sort)
# поводиться інакше, ніж на Linux. Скрипт має однаково працювати і в Git Bash.

LANG_ARG="${1:-}"
STAGE_ARG="${2:-}"

PGPORT="${PGPORT:-5432}"
HTTP_PORT="${HTTP_PORT:-8080}"

BLOCKERS=0
WARNINGS=0

ok()    { printf '  \033[32m✓\033[0m %s\n' "$1"; }
warn()  { printf '  \033[33m!\033[0m %s\n' "$1"; WARNINGS=$((WARNINGS + 1)); }
fail()  { printf '  \033[31m✗\033[0m %s\n' "$1"; BLOCKERS=$((BLOCKERS + 1)); }
hint()  { printf '      %s\n' "$1"; }

# ---------------------------------------------------------------- helpers ---

have() { command -v "$1" >/dev/null 2>&1; }

# Перше число.число з рядка: "go version go1.25.13 darwin/arm64" -> "1.25.13"
extract_version() {
	printf '%s\n' "$1" | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n 1
}

# ver_ge 1.25.13 1.25 -> 0 (true), якщо перша версія не менша за другу
ver_ge() {
	local a1 a2 a3 b1 b2 b3
	IFS='.' read -r a1 a2 a3 <<<"${1%%[!0-9.]*}"
	IFS='.' read -r b1 b2 b3 <<<"${2%%[!0-9.]*}"
	a1=${a1:-0}; a2=${a2:-0}; a3=${a3:-0}
	b1=${b1:-0}; b2=${b2:-0}; b3=${b3:-0}
	[ "$a1" -gt "$b1" ] && return 0
	[ "$a1" -lt "$b1" ] && return 1
	[ "$a2" -gt "$b2" ] && return 0
	[ "$a2" -lt "$b2" ] && return 1
	[ "$a3" -ge "$b3" ]
}

# Чи слухає хтось порт. bash уміє /dev/tcp сам — не треба ні lsof, ні nc,
# яких немає ні в Git Bash, ні в частині мінімальних Linux-образів.
port_busy() {
	(exec 3<>"/dev/tcp/127.0.0.1/$1") >/dev/null 2>&1 || return 1
	exec 3>&- 2>/dev/null
	exec 3<&- 2>/dev/null
	return 0
}

# ----------------------------------------------------------------- docker ---

check_docker() {
	if ! have docker; then
		fail "docker не знайдено"
		hint "Постав Docker Desktop (macOS/Windows) або docker engine (Linux):"
		hint "https://docs.docker.com/get-started/get-docker/"
		return
	fi
	local dv
	dv="$(extract_version "$(docker --version 2>/dev/null)")"

	if ! docker info >/dev/null 2>&1; then
		fail "docker ${dv:-?} встановлений, але демон не відповідає"
		hint "Запусти Docker Desktop і дочекайся зеленого статусу, тоді повтори."
		return
	fi
	ok "docker ${dv:-?}, демон відповідає"

	if docker compose version >/dev/null 2>&1; then
		local cv
		cv="$(extract_version "$(docker compose version 2>/dev/null)")"
		if ver_ge "${cv:-0}" "2.0"; then
			ok "docker compose v${cv}"
		else
			fail "docker compose v${cv} — потрібен compose v2"
			hint "Стара окрема утиліта docker-compose (v1) не читає ключ name:."
		fi
	else
		fail "docker compose (v2) не знайдено"
		hint "Перевір: docker compose version"
	fi
}

# ------------------------------------------------------------------ ports ---

check_ports() {
	if ! port_busy "$PGPORT"; then
		ok "порт $PGPORT вільний"
	elif have docker && [ -n "$(docker compose ps -q postgres 2>/dev/null)" ]; then
		ok "порт $PGPORT зайнятий контейнером цього ж стейджа — це нормально"
	else
		fail "порт $PGPORT зайнятий чужим процесом"
		hint "Швидше за все, це локальний Postgres. Він перехопить з'єднання,"
		hint "і ти побачиш 'password authentication failed for user \"demo\"'."
		hint "Візьми інший порт:  make db-up PGPORT=5433"
		hint "або пропиши PGPORT=5433 у .env (cp .env.example .env)."
	fi

	if port_busy "$HTTP_PORT"; then
		warn "порт $HTTP_PORT зайнятий"
		hint "Якщо це твій же 'make run' у сусідньому терміналі — все гаразд."
		hint "Якщо ні: make run HTTP_PORT=8081 (і смоук на BASE_URL з тим же портом)."
	else
		ok "порт $HTTP_PORT вільний"
	fi
}

# --------------------------------------------------------------------- go ---

check_go() {
	if ! have go; then
		fail "go не знайдено"
		hint "Постав Go 1.25+: https://go.dev/dl/"
		hint "Немає бажання ставити Go? Візьми ts/ або py/ — потік ідентичний."
		return
	fi
	local gv toolchain
	gv="$(extract_version "$(go version 2>/dev/null)")"
	toolchain="$(go env GOTOOLCHAIN 2>/dev/null)"

	if ver_ge "${gv:-0}" "1.25"; then
		ok "go ${gv}"
	elif [ "$toolchain" = "local" ]; then
		fail "go ${gv} < 1.25, а GOTOOLCHAIN=local забороняє доїхати новішому"
		hint "Або постав Go 1.25+, або: go env -w GOTOOLCHAIN=auto"
	else
		warn "go ${gv} < 1.25, але GOTOOLCHAIN=${toolchain:-auto} — Go доїде сам"
		hint "Першому запуску потрібна мережа: він завантажить go1.25.x."
	fi

	if have go && [ -n "$(go env GOMODCACHE 2>/dev/null)" ] \
		&& [ ! -d "$(go env GOMODCACHE)/github.com/go-chi" ]; then
		warn "залежності модуля ще не завантажені"
		hint "Запусти: make install"
	fi
}

# ------------------------------------------------------------------- node ---

check_node() {
	if ! have node; then
		fail "node не знайдено"
		hint "Постав Node 22 LTS: https://nodejs.org/ (або nvm install)"
		return
	fi
	local nv want
	nv="$(extract_version "$(node --version 2>/dev/null)")"
	want=""
	[ -f .nvmrc ] && want="$(tr -d ' \t\r\n' < .nvmrc)"

	if ver_ge "${nv:-0}" "20"; then
		if [ -n "$want" ] && [ "${nv%%.*}" != "${want%%.*}" ]; then
			warn "node ${nv}, а .nvmrc просить ${want}"
			hint "Демо перевірене на ${want} LTS. Швидкий шлях: nvm use"
		else
			ok "node ${nv}"
		fi
	else
		fail "node ${nv} — застарий, потрібен 20+ (демо перевірене на ${want:-22})"
	fi

	if ! have npm; then
		fail "npm не знайдено (він іде разом з node)"
	fi

	if [ ! -x node_modules/.bin/tsx ]; then
		warn "залежності не встановлені (немає node_modules)"
		hint "Запусти: make install"
	fi
}

# ----------------------------------------------------------------- python ---

check_python() {
	if ! have python3; then
		fail "python3 не знайдено"
		hint "Потрібен Python 3.12–3.14: https://www.python.org/downloads/"
		return
	fi
	local pv
	pv="$(extract_version "$(python3 --version 2>&1)")"

	if ver_ge "${pv:-0}" "3.12" && ! ver_ge "${pv:-0}" "3.15"; then
		ok "python ${pv}"
	elif ! ver_ge "${pv:-0}" "3.12"; then
		fail "python ${pv} — потрібен 3.12+"
	else
		fail "python ${pv} — новіший за перевірений діапазон (3.12–3.14)"
		hint "Частина залежностей ще не має коліс під цю версію."
		hint "Створи venv на 3.14: python3.14 -m venv .venv && source .venv/bin/activate"
	fi

	if [ -n "${VIRTUAL_ENV:-}" ]; then
		ok "активний venv: ${VIRTUAL_ENV}"
	else
		fail "venv не активований"
		hint "Без нього pip у сучасних системах відмовить:"
		hint "  error: externally-managed-environment"
		hint "Зроби так (з теки цього стейджа):"
		hint "  python3 -m venv .venv"
		hint "  source .venv/bin/activate      # Windows: .venv\\Scripts\\activate"
		hint "  make install"
		return
	fi

	if ! python3 -c "import fastapi, psycopg" >/dev/null 2>&1; then
		warn "залежності ще не поставлені в цей venv"
		hint "Запусти: make install"
	fi
	if [ "$STAGE_ARG" = "3" ] && ! have lint-imports; then
		warn "import-linter ще не поставлений"
		hint "Запусти: make install (або make arch-lint-install)"
	fi
}

# ------------------------------------------------------------------- інше ---

check_common() {
	if have curl; then
		ok "curl на місці"
	else
		warn "curl не знайдено — 'make smoke' не спрацює"
		hint "macOS/Linux: curl зазвичай уже є. Windows: він іде з Git Bash."
	fi
}

# ------------------------------------------------------------------- main ---

case "$LANG_ARG" in
	go|ts|py) ;;
	*)
		echo "usage: preflight.sh <go|ts|py> [1|2|3]" >&2
		exit 2
		;;
esac

printf '\nПеревірка середовища · %s stage-%s\n' "$LANG_ARG" "${STAGE_ARG:-?}"

check_docker
check_ports
case "$LANG_ARG" in
	go) check_go ;;
	ts) check_node ;;
	py) check_python ;;
esac
check_common

echo ""
if [ "$BLOCKERS" -gt 0 ]; then
	printf '\033[31m✗ Блокерів: %s\033[0m (попереджень: %s). Полагодь їх і повтори: make doctor\n\n' \
		"$BLOCKERS" "$WARNINGS"
	exit 1
fi
if [ "$WARNINGS" -gt 0 ]; then
	printf '\033[33m! Попереджень: %s\033[0m — йти далі можна.\n\n' "$WARNINGS"
else
	printf '\033[32m✓ Середовище готове.\033[0m\n\n'
fi
exit 0
