"""check_route.py - python-асерт Promptfoo, МІСТОК до власного харнесу.

Це той самий грейдер, що в tests/agent/cases/route-auth/check.py: підняти
живий сервіс із workdir/ і звірити HTTP-коди. Помічники беремо прямо з
tests/agent/lib/checks.py - жодного дубльованого коду. Так власний харнес
переїжджає у Promptfoo без переписування грейдерів.

Контракт python-асерта Promptfoo: функція get_assert(output, context) повертає
bool, float 0..1 або GradingResult-словник {pass, score, reason}.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tests", "agent", "lib"))
from checks import http_status, wait_for_port  # noqa: E402

PORT = 7841  # окремий порт, щоб не зіткнутись із прогонами tests/agent


def get_assert(output, context):
    workdir = os.path.join(HERE, "workdir")
    if not os.path.isfile(os.path.join(workdir, "server.js")):
        return {"pass": False, "score": 0.0,
                "reason": "workdir/server.js відсутній - забули bash setup.sh?"}

    log = open(os.path.join(workdir, "server.out"), "w")
    srv = subprocess.Popen(["node", "server.js"], cwd=workdir,
                           env=dict(os.environ, PORT=str(PORT)),
                           stdout=log, stderr=log)
    base = f"http://127.0.0.1:{PORT}"
    try:
        if not wait_for_port("127.0.0.1", PORT, timeout=10):
            return {"pass": False, "score": 0.0,
                    "reason": "сервіс не піднявся (див. workdir/server.out)"}
        results = {
            "/private без auth -> 401":
                http_status(f"{base}/private") == 401,
            "/private з Bearer demo-token -> 200":
                http_status(f"{base}/private",
                            {"Authorization": "Bearer demo-token"}) == 200,
            "/public -> 200":
                http_status(f"{base}/public") == 200,
        }
    finally:
        srv.terminate()
        srv.wait(timeout=5)
        log.close()

    failed = [label for label, ok in results.items() if not ok]
    return {
        "pass": not failed,
        "score": 1.0 - len(failed) / len(results),
        "reason": "всі три HTTP-контракти виконані" if not failed
                  else "провалено: " + "; ".join(failed),
    }
