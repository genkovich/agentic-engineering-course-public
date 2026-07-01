#!/usr/bin/env bash
# common.sh — спільні helpers для golden-task suite (лекція 10.3).
#
# Дві ролі:
#   1. run.sh підключає це, щоб готувати пісочниці й ганяти агента (run_agent).
#   2. cases/<case>/check.sh підключає це, щоб робити ДЕТЕРМІНОВАНІ асерти
#      проти фінального стану пісочниці (assert_*).
#
# Центральна теза 10.3: прогін агента недетермінований, тому ми асертимо на
# РЕЗУЛЬТАТ (роут віддав 401? секрет не витік? рівно 3 коміти?), а не на текст.
# Детермінований чекер над недетермінованим агентом — це і є eval конфігурації.
#
# Сумісність: тримаємось bash 3.2 (дефолт на macOS) — без `declare -A`,
# без `${var,,}`. Все на масивах і case.

# --- ANSI кольори (просто, без CI-детекту, як у 5.4 run-isolation-tests.sh) ---
C_GREEN="\033[32m"
C_RED="\033[31m"
C_YELLOW="\033[33m"
C_DIM="\033[2m"
C_BOLD="\033[1m"
C_RESET="\033[0m"

# Корінь пакета (…/10.3-evals-regression) — рахуємо від цього файлу.
# lib/ → agent/ → tests/ → <package root>
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(cd "$LIB_DIR/.." && pwd)"
PKG_ROOT="$(cd "$AGENT_DIR/../.." && pwd)"
REPO_ROOT="$(cd "$PKG_ROOT/../.." && pwd)"   # …/agentic-engineering-course
FIXTURES_DIR="$PKG_ROOT/fixtures"
TMP_DIR="$PKG_ROOT/tmp"

# =============================================================================
# Підготовка пісочниці
# =============================================================================

# make_sandbox <case-name> → друкує шлях до чистої пісочниці tmp/run-<case>/
make_sandbox() {
  local name="$1"
  local sb="$TMP_DIR/run-$name"
  rm -rf "$sb"
  mkdir -p "$sb"
  printf '%s' "$sb"
}

# sandbox_git_init <sandbox> — робить пісочницю самодостатнім git-репо,
# щоб (а) check.sh міг асертити по git diff/log, (б) claude трактував її як
# окремий проект і брав .claude/ саме звідси, а не з монорепо вище.
sandbox_git_init() {
  local sb="$1"
  (
    cd "$sb" || exit 1
    git init -q
    git config user.email "evals@example.com"
    git config user.name "golden-task evals"
    git config commit.gpgsign false
    git add -A
    git commit -q -m "chore: seed sandbox" --no-verify >/dev/null 2>&1 || true
  )
}

# copy_fixture <fixture-name> <sandbox> — копіює fixtures/<name>/ у пісочницю.
copy_fixture() {
  local fx="$1" sb="$2"
  if [ ! -d "$FIXTURES_DIR/$fx" ]; then
    echo "copy_fixture: fixture '$fx' not found at $FIXTURES_DIR/$fx" >&2
    return 1
  fi
  # -R із крапкою копіює вміст разом з dotfiles (.env, .claude тощо).
  cp -R "$FIXTURES_DIR/$fx/." "$sb/"
}

# =============================================================================
# Прогін агента (єдина точка реального claude -p)
# =============================================================================

# run_agent <sandbox> <prompt-file> [extra claude flags...]
# Ганяє headless `claude -p` У ПІСОЧНИЦІ, пише ndjson-транскрипт у
# <sandbox>/transcript.jsonl (stream-json), stderr → <sandbox>/agent.stderr.
# НЕ валить набір на ненульовому коді — повертаємо 0, вердикт дає check.sh.
run_agent() {
  local sb="$1" prompt_file="$2"
  shift 2
  local transcript="$sb/transcript.jsonl"
  local prompt
  prompt="$(cat "$prompt_file")"

  # Патерн headless-прогону взято з 7.2 ralph.sh (реальний claude -p).
  # stream-json потребує --verbose. acceptEdits, НЕ bypassPermissions —
  # інакше deny-правила й guardrail-хуки з .claude/ пісочниці не спрацюють.
  (
    cd "$sb" || exit 1
    claude -p "$prompt" \
      --output-format stream-json --verbose \
      --permission-mode "${AGENT_PERMISSION_MODE:-acceptEdits}" \
      "$@"
  ) >"$transcript" 2>"$sb/agent.stderr" || true

  printf '%s' "$transcript"
}

# transcript_text <transcript> — витягує лише текстові репліки асистента.
transcript_text() {
  local t="$1"
  [ -f "$t" ] || return 0
  if command -v jq >/dev/null 2>&1; then
    jq -r 'select(.type=="assistant") | .message.content[]?
           | select(.type=="text") | .text' "$t" 2>/dev/null
  else
    cat "$t"
  fi
}

# transcript_cost <transcript> — друкує сумарний cost (USD) з фінального result.
transcript_cost() {
  local t="$1"
  [ -f "$t" ] || { printf '0'; return; }
  if command -v jq >/dev/null 2>&1; then
    jq -r 'select(.type=="result") | .total_cost_usd // empty' "$t" 2>/dev/null \
      | tail -n1
  else
    printf '?'
  fi
}

# transcript_turns <transcript> — друкує num_turns з фінального result.
transcript_turns() {
  local t="$1"
  [ -f "$t" ] || { printf '0'; return; }
  if command -v jq >/dev/null 2>&1; then
    jq -r 'select(.type=="result") | .num_turns // empty' "$t" 2>/dev/null | tail -n1
  else
    printf '?'
  fi
}

# =============================================================================
# Асерти для check.sh — кожен друкує діагностику й копить FAILED
# =============================================================================
# Конвенція: check.sh виставляє `FAILED=0` і викликає assert_*; ті піднімають
# FAILED=1 на провалі. Наприкінці check.sh: `exit $FAILED`.

_ok()   { printf "  ${C_GREEN}✓${C_RESET} %s\n" "$1"; }
_fail() { printf "  ${C_RED}✗${C_RESET} %s\n" "$1"; FAILED=1; }

# assert_eq <actual> <expected> <label>
assert_eq() {
  if [ "$1" = "$2" ]; then _ok "$3 ($1)"; else _fail "$3 — очікував '$2', отримав '$1'"; fi
}

# assert_file_contains <file> <substring> <label>
assert_file_contains() {
  if [ -f "$1" ] && grep -qF -- "$2" "$1"; then _ok "$3"; else _fail "$3 — '$2' не знайдено у $1"; fi
}

# assert_file_absent_value <file> <value> <label>
# Ключовий guardrail-асерт: значення (напр. секрет) НЕ має бути у файлі/транскрипті.
assert_file_absent_value() {
  if [ ! -f "$1" ]; then _fail "$3 — файл $1 відсутній"; return; fi
  if grep -qF -- "$2" "$1"; then _fail "$3 — значення '$2' ПРОСОЧИЛОСЬ у $1"; else _ok "$3"; fi
}

# assert_grep <file> <regex> <label> — grep -E
assert_grep() {
  if [ -f "$1" ] && grep -qE -- "$2" "$1"; then _ok "$3"; else _fail "$3 — патерн /$2/ не знайдено у $1"; fi
}

# assert_clean_diff <repo-dir> <pathspec> <label>
# Перевіряє, що під <pathspec> НЕМА змін (для read-only агента / незайманих tests/).
assert_clean_diff() {
  local d="$1" spec="$2" label="$3" out
  out="$(cd "$d" && git --no-pager diff --stat -- "$spec" 2>/dev/null; cd "$d" && git status --porcelain -- "$spec" 2>/dev/null)"
  if [ -z "$out" ]; then _ok "$label"; else _fail "$label — є зміни під '$spec':\n$out"; fi
}

# assert_commit_count <repo-dir> <n> <label>
assert_commit_count() {
  local d="$1" want="$2" label="$3" got
  got="$(cd "$d" && git rev-list --count HEAD 2>/dev/null || echo 0)"
  # Віднімаємо 1 seed-коміт (chore: seed sandbox).
  got=$((got - 1))
  assert_eq "$got" "$want" "$label"
}

# assert_http <url> <expected-status> <label> [curl extra args...]
# Очікує, що сервіс уже піднято. Друкує фактичний статус.
assert_http() {
  local url="$1" want="$2" label="$3"
  shift 3
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' "$@" "$url" 2>/dev/null || echo 000)"
  assert_eq "$code" "$want" "$label"
}

# wait_for_port <host> <port> <timeout-sec> — чекає, поки сервіс відкриє порт.
wait_for_port() {
  local host="$1" port="$2" timeout="${3:-10}" i=0
  while [ "$i" -lt "$((timeout * 10))" ]; do
    if (exec 3<>"/dev/tcp/$host/$port") 2>/dev/null; then exec 3>&- 3<&-; return 0; fi
    i=$((i + 1))
    perl -e 'select(undef,undef,undef,0.1)' 2>/dev/null || sleep 1
  done
  return 1
}
