#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Mock analytics receiver для demo (slide 8).
Слухає :8090, друкує кожен POST у консоль як pretty JSON.
Stdlib-only (http.server). Запускається через PEP 723: `uv run server.py` АБО `python3 server.py`.

У скринкасті:
  термінал A:  python3 examples/analytics-server/server.py
  термінал B:  claude  (виконуй задачі — у А падають події)
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8090


class Handler(BaseHTTPRequestHandler):
    def _ok(self, body: bytes = b'{"ok":true}\n'):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        try:
            data = json.loads(raw.decode("utf-8"))
            pretty = json.dumps(data, ensure_ascii=False, indent=2)
        except Exception:
            pretty = raw.decode("utf-8", errors="replace")
        print(f"\n=== {self.path} ===")
        print(pretty)
        sys.stdout.flush()
        self._ok()

    def do_GET(self):
        self._ok(b'{"service":"hooks-toolkit-analytics","ok":true}\n')

    def log_message(self, fmt, *args):
        return


def main():
    addr = ("127.0.0.1", PORT)
    httpd = HTTPServer(addr, Handler)
    print(f"analytics receiver listening on http://{addr[0]}:{addr[1]}/events")
    print("(POST any JSON — it'll be pretty-printed below)")
    sys.stdout.flush()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping receiver")


if __name__ == "__main__":
    main()
