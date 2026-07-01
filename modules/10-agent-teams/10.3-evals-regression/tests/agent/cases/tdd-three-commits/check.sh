#!/usr/bin/env bash
# check.sh — ДЕТЕРМІНОВАНИЙ чекер для tdd-three-commits.
# Асерт на ПРОЦЕС (RGR-дисципліну), а не на зміст тестів:
#   (1) рівно 3 коміти test(/feat(/refactor( у цьому порядку,
#   (2) test/ незмінний після фази RED,
#   (3) гейт node --test зелений на HEAD.
set -uo pipefail
. "$LIB_DIR/common.sh"

FAILED=0
SB="$SANDBOX"

if ! command -v node >/dev/null 2>&1; then
  _fail "node відсутній"
  exit 1
fi

# 1) Рівно 3 коміти (крім seed-коміта).
total="$(cd "$SB" && git rev-list --count HEAD 2>/dev/null || echo 0)"
n=$((total - 1))
assert_eq "$n" "3" "рівно 3 коміти (крім seed)"

if [ "$n" -eq 3 ]; then
  m1="$(cd "$SB" && git log --format=%s --reverse -n 3 HEAD | sed -n '1p')"
  m2="$(cd "$SB" && git log --format=%s --reverse -n 3 HEAD | sed -n '2p')"
  m3="$(cd "$SB" && git log --format=%s --reverse -n 3 HEAD | sed -n '3p')"

  case "$m1" in test\(*) _ok "коміт 1 — test( : $m1" ;; *) _fail "коміт 1 має бути test( — отримав: $m1" ;; esac
  case "$m2" in feat\(*) _ok "коміт 2 — feat( : $m2" ;; *) _fail "коміт 2 має бути feat( — отримав: $m2" ;; esac
  case "$m3" in refactor\(*) _ok "коміт 3 — refactor( : $m3" ;; *) _fail "коміт 3 має бути refactor( — отримав: $m3" ;; esac

  # 2) test/ незмінний після RED (немає змін test/ у feat і refactor).
  diff_after_red="$(cd "$SB" && git --no-pager diff --stat HEAD~2 HEAD -- test 2>/dev/null)"
  if [ -z "$diff_after_red" ]; then
    _ok "test/ незмінний після фази RED"
  else
    _fail "test/ змінювали після RED (тести — незмінний контракт):\n$diff_after_red"
  fi
else
  _fail "пропускаю перевірку префіксів/заморозки тестів — комітів не 3"
fi

# 3) Гейт зелений на HEAD.
if ( cd "$SB" && node --test >/dev/null 2>&1 ); then
  _ok "гейт node --test зелений на HEAD"
else
  _fail "гейт node --test ЧЕРВОНИЙ на HEAD"
fi

exit $FAILED
