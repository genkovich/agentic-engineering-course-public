"""check_nplusone.py - грейдер fix-n-plus-one: інструментований лічильник
запитів. Байдуже, ЯК агент переписав код, - важливо, що запитів стало ≤2,
а звіт лишився коректним."""
import re
import shutil
import subprocess
from pathlib import Path

SUITE = Path(__file__).resolve().parents[1]
WORKDIR = SUITE / "workdir-nplusone"


def get_assert(output, context):
    # runner.js - ДОВІРЕНИЙ: перекопіюємо з cases/, щоб агент не міг підмінити.
    shutil.copy2(SUITE / "cases" / "fix-n-plus-one" / "runner.js",
                 WORKDIR / "runner.js")
    r = subprocess.run(["node", "runner.js"], cwd=WORKDIR,
                       capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    m = re.search(r"queries=(\d+)", out)
    queries = int(m.group(1)) if m else None
    ok = r.returncode == 0 and queries is not None and queries <= 2
    return {"pass": ok, "score": 1.0 if ok else 0.0,
            "reason": f"exit={r.returncode}, queries={queries} "
                      "(PASS = exit 0 і ≤2 запитів)"}
