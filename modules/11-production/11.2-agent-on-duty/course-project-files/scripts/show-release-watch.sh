#!/usr/bin/env bash
set -euo pipefail

OBSERVABILITY_ENV_FILE="${OBSERVABILITY_ENV_FILE:-$HOME/.config/course-project/observability.env}"

docker compose \
  --env-file "$OBSERVABILITY_ENV_FILE" \
  -f compose.vps.yml \
  -f compose.observability.yml \
  logs --tail=100 watcher

docker compose \
  --env-file "$OBSERVABILITY_ENV_FILE" \
  -f compose.vps.yml \
  -f compose.observability.yml \
  exec watcher sh -lc 'ls -lt artifacts && for file in artifacts/*; do echo "--- $file"; cat "$file"; done'
