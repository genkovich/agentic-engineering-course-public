#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="${1:-$HOME/.config/course-project}"
umask 077
mkdir -p "$CONFIG_DIR"

openssl rand -hex 32 > "$CONFIG_DIR/watcher-token.txt"
openssl rand -base64 24 > "$CONFIG_DIR/grafana-admin-password.txt"
touch "$CONFIG_DIR/anthropic-api-key.txt"

{
  printf 'WATCHER_TOKEN_FILE=%s/watcher-token.txt\n' "$CONFIG_DIR"
  printf 'GRAFANA_ADMIN_PASSWORD_FILE=%s/grafana-admin-password.txt\n' "$CONFIG_DIR"
  printf 'ANTHROPIC_API_KEY_FILE=%s/anthropic-api-key.txt\n' "$CONFIG_DIR"
  printf 'CLAUDE_MODEL=sonnet\n'
} > "$CONFIG_DIR/observability.env"

echo "Created production config in $CONFIG_DIR."
echo "Paste an Anthropic API key into $CONFIG_DIR/anthropic-api-key.txt only if AI review is required."
echo "Copy watcher-token.txt into GitHub secret WATCHER_WEBHOOK_TOKEN."
