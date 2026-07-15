#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

required=(
  Dockerfile.production
  compose.vps.yml
  app/api/health/route.ts
  .github/workflows/deploy-vps.yml
)

for file in "${required[@]}"; do
  test -s "$file" || { echo "Missing $file" >&2; exit 1; }
done

rg -q 'process\.env\.DB_PATH' lib/db.ts
rg -q 'course-project-data:/app/data' compose.vps.yml
rg -q '/api/health' compose.vps.yml .github/workflows/deploy-vps.yml
rg -q 'runs-on: \[self-hosted, linux, x64, course-vps\]' .github/workflows/deploy-vps.yml
! rg -q 'pull_request:' .github/workflows/deploy-vps.yml
! rg -n 'uses: [^@]+@(main|master|v[0-9]+)' .github/workflows/deploy-vps.yml
! rg -n ':[[:space:]]*latest([[:space:]]|$)' Dockerfile.production compose.vps.yml

docker compose --env-file .env.vps.example -f compose.vps.yml config >/dev/null
npm run build
git diff --check

echo "PASS: repository is ready for a human-reviewed VPS deploy"
