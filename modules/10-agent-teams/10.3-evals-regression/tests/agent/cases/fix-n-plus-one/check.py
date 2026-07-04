#!/usr/bin/env python3
"""Грейдер кейса fix-n-plus-one.

Асерт на РЕЗУЛЬТАТ: інструментований лічильник запитів впав до ≤2 (N+1
усунено), а звіт лишився коректним. runner.js - ДОВІРЕНИЙ: перекопіюємо
його з кейса перед запуском, щоб агент не міг його підмінити.
"""
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.environ["LIB_DIR"])
from checks import Checker  # noqa: E402

c = Checker()
sb = os.environ["SANDBOX"]
case_dir = os.environ["CASE_DIR"]

# Перекопіюємо довірений раннер поверх того, що лежить у пісочниці.
shutil.copy2(os.path.join(case_dir, "runner.js"), os.path.join(sb, "runner.js"))

r = subprocess.run(["node", "runner.js"], cwd=sb, capture_output=True, text=True)
out = (r.stdout + r.stderr).strip()
c.info(f"runner: {out.splitlines()[0] if out else '(порожньо)'}")

c.eq(r.returncode, 0, "runner exit 0 (звіт коректний і N+1 усунено)")

m = re.search(r"queries=(\d+)", out)
queries = int(m.group(1)) if m else None
c.expect(queries is not None and queries <= 2,
         f"SQL-викликів: {queries} (≤2)",
         f"{queries} запитів (>2) - N+1 лишився")

sys.exit(c.exit_code())
