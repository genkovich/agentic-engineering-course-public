#!/usr/bin/env bash
set -euo pipefail

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash -n "$MODULE_DIR/apply-to-course-project.sh"
bash -n "$MODULE_DIR/course-project-files/.claude/skills/prepare-vps-deploy/scripts/verify-deploy.sh"

required=(
  "README.md"
  "course-project-files/Dockerfile.production"
  "course-project-files/compose.vps.yml"
  "course-project-files/app/api/health/route.ts"
  "course-project-files/.github/workflows/deploy-vps.yml"
  "course-project-files/.claude/skills/prepare-vps-deploy/SKILL.md"
)

for file in "${required[@]}"; do
  test -s "$MODULE_DIR/$file" || { echo "Missing $file" >&2; exit 1; }
done

! rg -n ':[[:space:]]*latest([[:space:]]|$)' "$MODULE_DIR/course-project-files"
! rg -n 'pull_request:' "$MODULE_DIR/course-project-files/.github/workflows/deploy-vps.yml"
rg -q 'course-vps' "$MODULE_DIR/course-project-files/.github/workflows/deploy-vps.yml"
rg -q 'healthcheck:' "$MODULE_DIR/course-project-files/compose.vps.yml"

if command -v docker >/dev/null 2>&1; then
  docker compose --env-file "$MODULE_DIR/course-project-files/.env.vps.example" \
    -f "$MODULE_DIR/course-project-files/compose.vps.yml" config >/dev/null
fi

echo "PASS: Lecture 11.2 VPS deploy materials"
