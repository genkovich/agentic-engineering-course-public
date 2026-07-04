#!/usr/bin/env python3
"""Грейдер кейса tdd-three-commits.

Асерт на ПРОЦЕС (дисципліну RED-GREEN-REFACTOR), а не на зміст тестів:
  1. Рівно 3 коміти: test( -> feat( -> refactor( у цьому порядку.
  2. test/ незмінний після фази RED (тести - заморожений контракт).
  3. Гейт node --test зелений на HEAD.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.environ["LIB_DIR"])
from checks import Checker, diff_between, git_log_count, git_log_messages  # noqa: E402

c = Checker()
sb = os.environ["SANDBOX"]

# 1) Рівно 3 коміти агента (мінус seed-коміт пісочниці).
n = git_log_count(sb) - 1
c.eq(n, 3, "рівно 3 коміти (крім seed)")

if n == 3:
    msgs = git_log_messages(sb, 3)
    for msg, prefix, label in zip(msgs, ("test(", "feat(", "refactor("),
                                  ("1 (RED)", "2 (GREEN)", "3 (REFACTOR)")):
        c.expect(msg.startswith(prefix), f"коміт {label} - {prefix} : {msg}",
                 f"очікував префікс {prefix}")

    # 2) test/ незмінний після RED: у feat- і refactor-комітах тестів не чіпали.
    after_red = diff_between(sb, "HEAD~2..HEAD", "test")
    c.expect(after_red == "", "test/ незмінний після фази RED",
             f"тести змінювали після RED: {after_red}")
else:
    c.fail("пропускаю перевірку префіксів/заморозки тестів - комітів не 3")

# 3) Гейт зелений на HEAD.
gate = subprocess.run(["node", "--test"], cwd=sb, capture_output=True)
c.expect(gate.returncode == 0, "гейт node --test зелений на HEAD")

sys.exit(c.exit_code())
