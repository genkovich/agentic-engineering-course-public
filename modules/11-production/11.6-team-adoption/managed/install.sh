#!/usr/bin/env bash
# install.sh - кладе managed-settings.json у системну теку ClaudeCode (macOS/Linux).
# ЗАПИСУЄ СИСТЕМНУ ПОЛІТИКУ. Після демо обов'язково прожени uninstall.sh.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$HERE/managed-settings.json"

# CLAUDE_MANAGED_DIR дозволяє протестувати скрипт проти тимчасової теки без sudo:
#   CLAUDE_MANAGED_DIR=/tmp/cc-managed bash install.sh
# Порожній override → бойова системна тека (потрібен sudo).
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

echo "→ Джерело:      $SRC"
echo "→ Призначення:  $DEST"

if [ -z "${CLAUDE_MANAGED_DIR:-}" ] && [ "$(id -u)" -ne 0 ]; then
  echo "Потрібен sudo для запису в $DEST_DIR. Запусти: sudo bash $0"
  exit 1
fi

# Бекап наявної політики, якщо є (щоб не затерти реальну корпоративну).
if [ -f "$DEST" ]; then
  BACKUP="$DEST.pre-11.5-demo.bak"
  echo "→ Знайдено наявний managed-settings.json, бекап у $BACKUP"
  cp "$DEST" "$BACKUP"
fi

mkdir -p "$DEST_DIR"
cp "$SRC" "$DEST"
chmod 644 "$DEST"

echo "✅ Managed settings встановлено."
echo "   Перевір у Claude Code: /status → рядок Setting sources має показати managed."
echo "   Відкат: sudo bash $HERE/uninstall.sh"
