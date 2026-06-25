"""Minimal env-driven HTTP service for the worktree merge/cleanup demo.

Reads PORT and DB_NAME from a local .env (loaded by hand, no pip deps), so the
service stays continuous with 9.2. The one line that matters for this lecture is
GREETING below: both worktree branches (worktree-feature-a, worktree-bugfix-b)
edit that single line in their own way, so when you merge the second branch back
you get a real merge conflict on it — exactly the situation Slide 4 describes.

Run it from any worktree:  python3 app.py  (or `make serve` from the fixture).
"""

import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# The single line both worktree branches edit differently — the merge-conflict
# locus for Скринкаст #1. Keep it on its own line so the conflict stays clean.
GREETING = "service up"


def load_env():
    """Load KEY=VALUE pairs from the .env sitting next to this file."""
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
        self.wfile.write(
            ("%s on port %d, db=%s\n" % (GREETING, PORT, DB_NAME)).encode()
        )

    def log_message(self, *args):
        pass  # keep the screencast terminal quiet


def main():
    print("serving on http://127.0.0.1:%d  (db=%s)" % (PORT, DB_NAME))
    print("Ctrl-C to stop")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
