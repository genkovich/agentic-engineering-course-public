#!/usr/bin/env bash
set -euo pipefail

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-}"

if [[ -z "$TARGET" || ! -f "$TARGET/package.json" ]]; then
  echo "Usage: $0 /absolute/path/to/course-project" >&2
  exit 2
fi

mkdir -p \
  "$TARGET/app/api/health" \
  "$TARGET/.github/workflows" \
  "$TARGET/.claude/skills/prepare-vps-deploy/agents" \
  "$TARGET/.claude/skills/prepare-vps-deploy/scripts"

cp "$MODULE_DIR/course-project-files/Dockerfile.production" "$TARGET/"
cp "$MODULE_DIR/course-project-files/compose.vps.yml" "$TARGET/"
cp "$MODULE_DIR/course-project-files/.dockerignore" "$TARGET/"
cp "$MODULE_DIR/course-project-files/.env.vps.example" "$TARGET/"
cp "$MODULE_DIR/course-project-files/app/api/health/route.ts" "$TARGET/app/api/health/"
cp "$MODULE_DIR/course-project-files/.github/workflows/deploy-vps.yml" "$TARGET/.github/workflows/"
cp "$MODULE_DIR/course-project-files/.claude/skills/prepare-vps-deploy/SKILL.md" \
  "$TARGET/.claude/skills/prepare-vps-deploy/"
cp "$MODULE_DIR/course-project-files/.claude/skills/prepare-vps-deploy/agents/openai.yaml" \
  "$TARGET/.claude/skills/prepare-vps-deploy/agents/"
cp "$MODULE_DIR/course-project-files/.claude/skills/prepare-vps-deploy/scripts/verify-deploy.sh" \
  "$TARGET/.claude/skills/prepare-vps-deploy/scripts/"
chmod +x "$TARGET/.claude/skills/prepare-vps-deploy/scripts/verify-deploy.sh"

if ! rg -q 'process\.env\.DB_PATH' "$TARGET/lib/db.ts"; then
  patch --no-backup-if-mismatch -d "$TARGET" -p1 < "$MODULE_DIR/patches/db-path.patch"
fi

if ! rg -q '^!\.env\.vps\.example$' "$TARGET/.gitignore"; then
  patch --no-backup-if-mismatch -d "$TARGET" -p1 < "$MODULE_DIR/patches/gitignore.patch"
fi

echo "Applied Lecture 11.2 deploy kit to $TARGET"
echo "Next: cp .env.vps.example .env.vps && inspect git diff"
