#!/usr/bin/env bash
# Read-only. Print the newest watcher verdict and its paired release report.
#
# Mirrors show-release-watch.sh: it only reads artifacts the watcher already
# wrote, over `docker compose exec`. It holds no GitHub token and changes
# nothing. The alert-worker detect job and a human inspecting the queue both
# reuse it.
#
# Usage: scripts/latest-anomaly.sh [OUT_DIR]
#   Writes OUT_DIR/verdict.json and OUT_DIR/report.json (default OUT_DIR: .).
#   Exit 3 when the watcher has no verdict yet.
set -euo pipefail

OBSERVABILITY_ENV_FILE="${OBSERVABILITY_ENV_FILE:-$HOME/.config/course-project/observability.env}"
OUT_DIR="${1:-.}"

compose() {
  docker compose \
    --env-file "$OBSERVABILITY_ENV_FILE" \
    -f compose.vps.yml \
    -f compose.observability.yml \
    "$@"
}

mkdir -p "$OUT_DIR"

# Newest verdict file name, resolved inside the watcher container (read-only).
verdict_name="$(compose exec -T watcher sh -lc \
  'ls -1t artifacts 2>/dev/null | grep -- "-verdict.json$" | head -n1')"

if [[ -z "$verdict_name" ]]; then
  echo "No watcher verdict found yet." >&2
  exit 3
fi

run_id="${verdict_name%-verdict.json}"
report_name="${run_id}-release-report.json"

compose exec -T watcher sh -lc "cat artifacts/$verdict_name" > "$OUT_DIR/verdict.json"
compose exec -T watcher sh -lc "cat artifacts/$report_name" > "$OUT_DIR/report.json"

echo "Wrote $OUT_DIR/verdict.json and $OUT_DIR/report.json (run_id=$run_id)."
