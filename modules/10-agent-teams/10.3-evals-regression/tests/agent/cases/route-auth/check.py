#!/usr/bin/env python3
"""Грейдер кейса route-auth.

Асерт на РЕЗУЛЬТАТ - HTTP-коди ЖИВОГО сервісу, а не текст агента:
  /private без auth -> 401; з Bearer secret-token -> 200; /public -> 200.
Агент міг написати middleware десятьма способами - грейдеру байдуже, яким:
перевіряється поведінка сервісу.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.environ["LIB_DIR"])
from checks import Checker, http_status, wait_for_port  # noqa: E402

c = Checker()
sb = os.environ["SANDBOX"]
port = int(os.environ.get("ROUTE_PORT", "7831"))
base = f"http://127.0.0.1:{port}"

if not os.path.isfile(os.path.join(sb, "server.js")):
    c.fail("server.js зник із пісочниці")
    sys.exit(1)

# Піднімаємо сервіс просто з пісочниці.
with open(os.path.join(sb, "server.out"), "w") as log:
    srv = subprocess.Popen(["node", "server.js"], cwd=sb,
                           env=dict(os.environ, PORT=str(port)),
                           stdout=log, stderr=log)
try:
    if not wait_for_port("127.0.0.1", port, timeout=10):
        c.fail(f"сервіс не піднявся на :{port} (див. server.out у пісочниці)")
        sys.exit(1)

    c.eq(http_status(f"{base}/private"), 401,
         "/private без auth -> 401")
    c.eq(http_status(f"{base}/private",
                     {"Authorization": "Bearer secret-token"}), 200,
         "/private з Bearer secret-token -> 200")
    c.eq(http_status(f"{base}/public"), 200,
         "/public лишається відкритим -> 200")
finally:
    srv.terminate()
    srv.wait(timeout=5)

sys.exit(c.exit_code())
