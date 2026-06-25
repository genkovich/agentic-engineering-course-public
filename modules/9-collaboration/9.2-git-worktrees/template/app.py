"""Minimal env-driven HTTP service for the worktree demo.

Reads PORT and DB_NAME from a local .env (loaded by hand, no pip deps), so
two worktrees with different .env values bind different ports and talk to
different databases. That is the whole point of Slides 10-11: file isolation
alone is not enough — you also have to isolate the environment.

Run it from any worktree:  python3 app.py  (or `make serve` from the fixture).
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer


def load_env():
    """Load KEY=VALUE pairs from the .env sitting next to this file.

    Each worktree carries its own copy (delivered via .worktreeinclude and
    re-pointed by the `w` helper), so the values differ per worktree.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, ".env")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


load_env()

PORT = int(os.environ.get("PORT", "8000"))
DB_NAME = os.environ.get("DB_NAME", "app_dev")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(("service up on port %d, db=%s\n" % (PORT, DB_NAME)).encode())

    def log_message(self, *args):
        pass  # keep the screencast terminal quiet


def main():
    print("serving on http://127.0.0.1:%d  (db=%s)" % (PORT, DB_NAME))
    print("Ctrl-C to stop")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
