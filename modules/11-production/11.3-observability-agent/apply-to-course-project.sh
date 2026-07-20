#!/usr/bin/env bash
set -euo pipefail

MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$MODULE_DIR/course-project-files"
BASELINE="$MODULE_DIR/baseline/deploy-vps.11.2.yml"
TARGET="${1:-}"

if [[ -z "$TARGET" ]]; then
  echo "Usage: $0 /absolute/path/to/course-project" >&2
  exit 2
fi

if [[ ! -d "$TARGET/.git" ]]; then
  echo "Target is not a Git repository: $TARGET" >&2
  exit 2
fi

for required in \
  package.json \
  package-lock.json \
  compose.vps.yml \
  .github/workflows/deploy-vps.yml \
  app/api/memes/route.ts \
  app/api/memes/random/route.ts; do
  if [[ ! -f "$TARGET/$required" ]]; then
    echo "Missing 11.2 prerequisite: $TARGET/$required" >&2
    exit 2
  fi
done

if [[ -n "$(git -C "$TARGET" status --porcelain)" ]]; then
  echo "Target has local changes. Commit or stash them before applying Lecture 11.3." >&2
  git -C "$TARGET" status --short >&2
  exit 2
fi

if ! cmp -s "$BASELINE" "$TARGET/.github/workflows/deploy-vps.yml"; then
  echo "deploy-vps.yml differs from the untouched Lecture 11.2 version." >&2
  echo "Use the manual path in README.md so your custom deploy steps are preserved." >&2
  exit 2
fi

files=(
  .github/workflows/deploy-vps.yml
  .github/workflows/release-watch.yml
  app/api/metrics/route.ts
  app/api/memes/route.ts
  app/api/memes/random/route.ts
  compose.observability.yml
  lib/observability.ts
  observability/prometheus.yml
  scripts/watch_release.py
)

for file in "${files[@]}"; do
  mkdir -p "$(dirname "$TARGET/$file")"
  cp "$SOURCE/$file" "$TARGET/$file"
done
chmod +x "$TARGET/scripts/watch_release.py"

cd "$TARGET"
npm install --save-exact prom-client@15.1.3

echo
echo "Lecture 11.3 files copied to: $TARGET"
echo "Next: git status --short"
echo "Validate the diff, then create the VPS password and GitHub secrets before merge."
echo "README.md contains the full manual and automated routes."
