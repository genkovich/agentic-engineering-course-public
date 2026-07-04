"""check_route.py - грейдер route-auth: підняти живий сервіс і звірити
фактичні HTTP-коди. Агент міг написати middleware десятьма способами -
грейдеру байдуже, яким: перевіряється поведінка сервісу."""
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import http_status, wait_for_port  # noqa: E402

WORKDIR = Path(__file__).resolve().parents[1] / "workdir-route"
PORT = 7841


def get_assert(output, context):
    if not (WORKDIR / "server.js").is_file():
        return {"pass": False, "score": 0.0,
                "reason": "workdir-route/server.js відсутній - забули bash setup.sh?"}
    log = open(WORKDIR / "server.out", "w")
    srv = subprocess.Popen(["node", "server.js"], cwd=WORKDIR,
                           env=dict(os.environ, PORT=str(PORT)),
                           stdout=log, stderr=log)
    base = f"http://127.0.0.1:{PORT}"
    try:
        if not wait_for_port("127.0.0.1", PORT):
            return {"pass": False, "score": 0.0,
                    "reason": "сервіс не піднявся (див. workdir-route/server.out)"}
        checks = {
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
    failed = [label for label, ok in checks.items() if not ok]
    return {"pass": not failed, "score": 1.0 - len(failed) / 3,
            "reason": "всі три HTTP-контракти виконані" if not failed
                      else "провалено: " + "; ".join(failed)}
