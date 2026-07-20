#!/usr/bin/env bash
# uninstall.sh - прибирає demo managed-settings.json і відновлює бекап, якщо був.
# Повертає систему в чистий стан після запису скринкаста #2.
set -euo pipefail

# CLAUDE_MANAGED_DIR - той самий override, що й в install.sh (для тестів без sudo).
if [ -n "${CLAUDE_MANAGED_DIR:-}" ]; then
  DEST_DIR="$CLAUDE_MANAGED_DIR"
else
  case "$(uname -s)" in
    Darwin) DEST_DIR="/Library/Application Support/ClaudeCode" ;;
    Linux)  DEST_DIR="/etc/claude-code" ;;
    *) echo "Unsupported OS: $(uname -s)"; exit 1 ;;
  esac
fi

DEST="$DEST_DIR/managed-settings.json"
BACKUP="$DEST.pre-11.5-demo.bak"

if [ -z "${CLAUDE_MANAGED_DIR:-}" ] && [ "$(id -u)" -ne 0 ]; then
  echo "Потрібен sudo. Запусти: sudo bash $0"
  exit 1
fi

if [ -f "$BACKUP" ]; then
  echo "→ Відновлюю попередній managed-settings.json з $BACKUP"
  mv "$BACKUP" "$DEST"
  echo "✅ Реальну політику повернуто на місце."
elif [ -f "$DEST" ]; then
  echo "→ Видаляю demo managed-settings.json"
  rm "$DEST"
  echo "✅ Managed settings прибрано. Система в чистому стані."
else
  echo "Нічого прибирати: $DEST не існує."
fi

echo "   Перевір у Claude Code: /status → рядок managed має зникнути."
