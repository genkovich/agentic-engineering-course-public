#!/usr/bin/env bash
set -euo pipefail

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$MODULE_DIR/course-project-files"
TARGET="${1:-}"

if [[ -z "$TARGET" || ! -f "$TARGET/package.json" ]]; then
  echo "Usage: $0 /absolute/path/to/course-project" >&2
  exit 2
fi

if [[ ! -f "$TARGET/compose.vps.yml" ]]; then
  echo "Apply Lecture 11.2 VPS kit before Lecture 11.2.1." >&2
  exit 1
fi

mkdir -p \
  "$TARGET/app/api/metrics" \
  "$TARGET/app/api/memes/random" \
  "$TARGET/lib" \
  "$TARGET/observability" \
  "$TARGET/scripts" \
  "$TARGET/.github/workflows" \
  "$TARGET/.claude/agents" \
  "$TARGET/.claude/skills/review-release-health"

cp -R "$SOURCE/observability/." "$TARGET/observability/"
cp -R "$SOURCE/.claude/skills/review-release-health/." \
  "$TARGET/.claude/skills/review-release-health/"
cp "$SOURCE/.env.observability.example" "$TARGET/"
cp "$SOURCE/compose.observability.yml" "$TARGET/"
cp "$SOURCE/lib/observability.ts" "$TARGET/lib/"
cp "$SOURCE/app/api/metrics/route.ts" "$TARGET/app/api/metrics/"
cp "$SOURCE/app/api/memes/route.ts" "$TARGET/app/api/memes/"
cp "$SOURCE/app/api/memes/random/route.ts" "$TARGET/app/api/memes/random/"
cp "$SOURCE/.github/workflows/deploy-vps.yml" "$TARGET/.github/workflows/"
cp "$SOURCE/.github/workflows/release-watch.yml" "$TARGET/.github/workflows/"
cp "$SOURCE/.github/workflows/alert-worker.yml" "$TARGET/.github/workflows/"
cp "$SOURCE/.claude/agents/alert-worker.md" "$TARGET/.claude/agents/"
cp "$SOURCE/scripts/show-release-watch.sh" "$TARGET/scripts/"
cp "$SOURCE/scripts/latest-anomaly.sh" "$TARGET/scripts/"

chmod +x \
  "$TARGET/observability/init-secrets.sh" \
  "$TARGET/scripts/show-release-watch.sh" \
  "$TARGET/scripts/latest-anomaly.sh" \
  "$TARGET/.claude/skills/review-release-health/scripts/validate-verdict.mjs"

if ! rg -q '^!\.env\.observability\.example$' "$TARGET/.gitignore"; then
  patch --no-backup-if-mismatch -d "$TARGET" -p1 < "$MODULE_DIR/patches/gitignore-observability.patch"
fi

(cd "$TARGET" && npm install --save-exact prom-client@15.1.3)

echo "Applied Lecture 11.2.1 observability kit to $TARGET"
echo "Next on the VPS: observability/init-secrets.sh"
