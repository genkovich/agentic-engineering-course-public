#!/usr/bin/env bash
set -euo pipefail

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KIT="$MODULE_DIR/course-project-files"

bash -n "$MODULE_DIR/apply-to-course-project.sh"
bash -n "$KIT/observability/init-secrets.sh"
bash -n "$KIT/scripts/show-release-watch.sh"
node --check "$KIT/observability/watcher/server.mjs"
node "$KIT/.claude/skills/review-release-health/scripts/validate-verdict.mjs" \
  "$MODULE_DIR/fixtures/healthy-verdict.json"

test -s "$KIT/app/api/metrics/route.ts"
test -s "$KIT/lib/observability.ts"
test -s "$KIT/observability/grafana/dashboards/course-project.json"
test -s "$KIT/.github/workflows/deploy-vps.yml"
test -s "$KIT/.github/workflows/release-watch.yml"

node -e 'JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"))' \
  "$KIT/observability/grafana/dashboards/course-project.json"

if rg -n ':[[:space:]]*latest([[:space:]]|$)' "$KIT"; then
  echo "Unpinned latest image found" >&2
  exit 1
fi
if rg -n '^\s+- "0\.0\.0\.0:(3001|9090|9093|3100|12345)' \
  "$KIT/compose.observability.yml"; then
  echo "An admin port is exposed publicly" >&2
  exit 1
fi
rg -q '127\.0\.0\.1:3001:3000' "$KIT/compose.observability.yml"
rg -q 'WATCHER_WEBHOOK_TOKEN' "$KIT/.github/workflows/release-watch.yml"
rg -q '\.config/course-project/observability.env' "$KIT/.github/workflows/deploy-vps.yml"
rg -q -- '-f compose.observability.yml' "$KIT/.github/workflows/deploy-vps.yml"

# Lecture 11.3 alert-worker: alert → draft PR
bash -n "$KIT/scripts/latest-anomaly.sh"
test -s "$KIT/.claude/agents/alert-worker.md"
node "$KIT/.claude/skills/review-release-health/scripts/validate-verdict.mjs" \
  "$MODULE_DIR/fixtures/anomaly-verdict.json"
node -e 'JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"))' \
  "$MODULE_DIR/fixtures/anomaly-report.json"

# Structural safety of the alert-worker workflow. The write-agent must never
# run on the VPS; the read-only detect job must never carry write scope.
python3 - "$KIT/.github/workflows/alert-worker.yml" <<'PY'
import sys, yaml

wf = yaml.safe_load(open(sys.argv[1]))
jobs = wf["jobs"]
detect = jobs["detect"]
author = jobs["author-fix"]

# detect stays read-only, next to the watcher on the VPS.
assert detect["runs-on"] == ["self-hosted", "linux", "x64", "course-vps"], detect["runs-on"]
assert detect["permissions"] == {"contents": "read"}, detect["permissions"]

# author-fix does every write, gated on detect, on an ephemeral GitHub VM.
assert author["needs"] == "detect", author["needs"]
assert author["runs-on"] == "ubuntu-latest", author["runs-on"]
assert author["if"].strip() == "needs.detect.outputs.open_pr == 'true'", author["if"]
assert author["permissions"].get("contents") == "write", author["permissions"]
assert author["permissions"].get("pull-requests") == "write", author["permissions"]

detect_run = " ".join(str(s.get("run", "")) for s in detect["steps"])
author_run = " ".join(str(s.get("run", "")) for s in author["steps"])

# The model runs only in author-fix, never on the VPS.
assert "claude -p" not in detect_run, "model must not run in detect"
assert "claude -p" in author_run, "model must run in author-fix"

# The model sandbox blocks GitHub, push and commit.
for needle in ["Bash(gh *)", "Bash(git push *)", "Bash(git commit *)"]:
    assert needle in author_run, needle

# Protected files include observability, so the agent cannot weaken its alarms.
assert "observability/" in author_run, "observability must be a protected path"

print("PASS: alert-worker structural safety")
PY

echo "PASS: Lecture 11.2.1 observability materials"
