#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KIT="$ROOT/course-project-files"

required=(
  README.md
  Makefile
  apply-to-course-project.sh
  baseline/deploy-vps.11.2.yml
  course-project-files/.env.observability.example
  course-project-files/.github/workflows/deploy-vps.yml
  course-project-files/.github/workflows/release-watch.yml
  course-project-files/app/api/metrics/route.ts
  course-project-files/app/api/memes/route.ts
  course-project-files/app/api/memes/random/route.ts
  course-project-files/compose.observability.yml
  course-project-files/lib/observability.ts
  course-project-files/observability/prometheus.yml
  course-project-files/scripts/watch_release.py
)

for file in "${required[@]}"; do
  test -s "$ROOT/$file"
done

bash -n "$ROOT/apply-to-course-project.sh"
bash -n "$ROOT/scripts/verify-materials.sh"

python3 -c 'import pathlib; compile(pathlib.Path(__import__("sys").argv[1]).read_text(), "watch_release.py", "exec")' \
  "$KIT/scripts/watch_release.py"

ruby -e 'require "yaml"; ARGV.each { |path| YAML.safe_load(File.read(path), aliases: true) }' \
  "$ROOT/baseline/deploy-vps.11.2.yml" \
  "$KIT/.github/workflows/deploy-vps.yml" \
  "$KIT/.github/workflows/release-watch.yml" \
  "$KIT/compose.observability.yml" \
  "$KIT/observability/prometheus.yml"

rg -q 'course_project_http_requests_total' "$KIT/lib/observability.ts"
rg -q 'course_project_http_request_duration_seconds' "$KIT/lib/observability.ts"
rg -q 'raise SystemExit\(42 if reason else 0\)' "$KIT/scripts/watch_release.py"
rg -q 'watch_minutes.*20|inputs.watch_minutes.*20|inputs.watch_minutes \|\| .20.' \
  "$KIT/.github/workflows/release-watch.yml" || rg -q "inputs.watch_minutes || '20'" \
  "$KIT/.github/workflows/release-watch.yml"

if rg -ni 'loki|alloy|alertmanager' "$KIT"; then
  echo "The minimal Lecture 11.3 kit unexpectedly contains a removed service." >&2
  exit 1
fi

echo "OK: Lecture 11.3 materials are complete and syntactically valid."
