#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

MINUTES = max(1, min(int(sys.argv[1] if len(sys.argv) > 1 else 20), 20))
PROMETHEUS = "http://127.0.0.1:9090"
ENV_FILE = str(Path.home() / ".config/course-project/observability.env")
REPORT_DIR = Path(os.getenv("REPORT_DIR", "/tmp/release-watch"))


def metric(query):
    url = f"{PROMETHEUS}/api/v1/query?{urlencode({'query': query})}"
    with urlopen(url, timeout=5) as response:
        result = json.load(response)["data"]["result"]
    return float(result[0]["value"][1]) if result else 0.0


def error_logs():
    command = [
        "docker", "compose", "--env-file", ENV_FILE,
        "-f", "compose.vps.yml", "-f", "compose.observability.yml",
        "logs", "--since", "70s", "--tail", "200",
        "--no-color", "--no-log-prefix", "app",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    lines = (result.stdout + result.stderr).splitlines()
    return [
        line for line in lines
        if '"level":"error"' in line or '"status":5' in line
    ][-40:]


queries = {
    "up": 'up{job="course-project"}',
    "errors_1m": 'sum(increase(course_project_http_requests_total{status=~"5.."}[1m])) or vector(0)',
    "p95_seconds": 'histogram_quantile(0.95, sum by (le) (rate(course_project_http_request_duration_seconds_bucket[5m]))) or vector(0)',
}

reason = None
measurements = {"up": None, "errors_1m": None, "p95_seconds": None}
logs = []

for minute in range(1, MINUTES + 1):
    try:
        measurements = {name: metric(query) for name, query in queries.items()}
        logs = error_logs()
        reason = (
            "app_not_up" if measurements["up"] != 1 else
            "new_5xx" if measurements["errors_1m"] > 0 else
            "p95_over_one_second" if measurements["p95_seconds"] > 1 else
            "error_log_detected" if logs else None
        )
    except Exception as error:
        reason = "signals_unavailable"
        logs = [f"{type(error).__name__}: {error}"]

    print(f"minute {minute}/{MINUTES}: {measurements}, error_logs={len(logs)}")
    if reason or minute == MINUTES:
        break
    time.sleep(60)

REPORT_DIR.mkdir(parents=True, exist_ok=True)
report_file = REPORT_DIR / "report.json"
report = {
    "schema_version": 1,
    "release_sha": os.getenv("RELEASE_SHA", "unknown"),
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "status": "anomaly" if reason else "healthy",
    "reason": reason or "none",
    "thresholds": {"up": 1, "errors_1m": 0, "p95_seconds": 1},
    "measurements": measurements,
    "recent_error_logs": logs,
}
report_file.write_text(json.dumps(report, indent=2) + "\n")
print(f"report={report_file}")
raise SystemExit(42 if reason else 0)
