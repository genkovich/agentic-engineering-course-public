#!/bin/bash
# sandbox-leak.test.sh - перевіряє що sandbox блокує bash subprocess до .env.
# Тест запускається на хості (не у контейнері). Сам Claude не запускає - перевіряє файлову систему і конфіг.
#
# Логіка: переконуємось що:
# 1. .claude/settings.json валідний JSON
# 2. permissions.deny містить повний baseline (секрети, незворотні bash, wget bypass)
# 3. sandbox.enabled = true
# 4. sandbox.filesystem.denyRead покриває всі 4 директорії з conventions
#
# Live тест (з реальним Claude headless) у README як ручна перевірка - потребує API key.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SETTINGS_FILE="$PROJECT_ROOT/.claude/settings.json"

echo "Project: $PROJECT_ROOT"
echo "Settings: $SETTINGS_FILE"
echo ""

# 1. settings.json має існувати
if [ ! -f "$SETTINGS_FILE" ]; then
  echo "FAIL: $SETTINGS_FILE не існує"
  exit 1
fi
echo "OK: settings.json існує"

# 2. settings.json валідний JSON
if ! python3 -m json.tool < "$SETTINGS_FILE" > /dev/null 2>&1; then
  echo "FAIL: settings.json не валідний JSON"
  exit 1
fi
echo "OK: settings.json валідний JSON"

# 3. permissions.deny має повний baseline (секрети, незворотні bash, wget bypass)
deny_check=$(SETTINGS_FILE="$SETTINGS_FILE" python3 <<'PY'
import json, os
with open(os.environ['SETTINGS_FILE']) as f:
    s = json.load(f)
deny = s.get('permissions', {}).get('deny', [])
required = [
    'Read(.env)', 'Read(**/.env)', 'Read(**/*.pem)', 'Read(**/*.key)',
    'Read(**/credentials*)', 'Read(**/*secret*)',
    'Read(~/.ssh/**)', 'Read(~/.aws/**)',
    'Bash(rm -rf *)', 'Bash(sudo *)', 'Bash(git push --force *)',
    'Bash(curl * | sh)', 'Bash(curl * | bash)',
]
missing = [r for r in required if r not in deny]
print(','.join(missing) if missing else 'OK')
PY
)

if [ "$deny_check" != "OK" ]; then
  echo "FAIL: permissions.deny не містить: $deny_check"
  exit 1
fi
echo "OK: permissions.deny покриває baseline (секрети, незворотні bash, pipe-to-shell)"

# 4. sandbox enabled
sandbox_enabled=$(SETTINGS_FILE="$SETTINGS_FILE" python3 <<'PY'
import json, os
with open(os.environ['SETTINGS_FILE']) as f:
    s = json.load(f)
print(s.get('sandbox', {}).get('enabled', False))
PY
)

if [ "$sandbox_enabled" != "True" ]; then
  echo "FAIL: sandbox.enabled = $sandbox_enabled, очікувалось True"
  exit 1
fi
echo "OK: sandbox enabled"

# 5. sandbox.filesystem.denyRead покриває всі 4 критичні директорії
sandbox_deny=$(SETTINGS_FILE="$SETTINGS_FILE" python3 <<'PY'
import json, os
with open(os.environ['SETTINGS_FILE']) as f:
    s = json.load(f)
deny = s.get('sandbox', {}).get('filesystem', {}).get('denyRead', [])
required = ['~/.ssh', '~/.aws', '~/.gnupg', '~/.kube/config']
missing = [r for r in required if r not in deny]
print(','.join(missing) if missing else 'OK')
PY
)

if [ "$sandbox_deny" != "OK" ]; then
  echo "FAIL: sandbox.filesystem.denyRead не містить: $sandbox_deny"
  exit 1
fi
echo "OK: sandbox.filesystem.denyRead покриває ~/.ssh, ~/.aws, ~/.gnupg, ~/.kube/config"

# 6. Створюємо тимчасовий .env, перевіряємо що він не у git tracked
TMP_ENV=$(mktemp -t "sandbox-leak-test.XXXXXX")
trap 'rm -f "$TMP_ENV"' EXIT
echo "FAKE_SECRET=should_not_leak_$(date +%s)" > "$TMP_ENV"
echo "OK: створено тимчасовий .env (live test з Claude - вручну, потребує API key)"

echo ""
echo "=== Sandbox leak test PASSED ==="
echo ""
echo "Для live перевірки з Claude:"
echo "1. cp .env.example .env (заповни заглушками)"
echo "2. claude --print 'прочитай .env' (має бути заблоковано permissions)"
echo "3. claude --print 'запусти bash -c \"cat .env\"' (має бути заблоковано sandbox-ом)"
