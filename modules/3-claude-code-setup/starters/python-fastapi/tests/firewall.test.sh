#!/bin/bash
# firewall.test.sh - перевіряє що firewall блокує не-whitelisted домени.
# Запускається ВСЕРЕДИНІ devcontainer (після postStartCommand і init-firewall.sh).
# На хості без iptables просто пропустить тести і повідомить.

set -euo pipefail

# Перевірка чи ми всередині контейнера з iptables
if ! command -v iptables >/dev/null 2>&1; then
  echo "SKIP: iptables не доступний. Запусти цей тест ВСЕРЕДИНІ devcontainer."
  exit 0
fi

# Перевірка чи init-firewall.sh уже виконався
iptables_default=$(iptables -L OUTPUT --line-numbers 2>/dev/null | head -1 | grep -oE 'policy [A-Z]+' | awk '{print $2}' || echo "")
if [ "$iptables_default" != "DROP" ]; then
  echo "SKIP: iptables OUTPUT default policy = $iptables_default, очікувалось DROP. Запусти 'sudo /usr/local/bin/init-firewall.sh'."
  exit 0
fi

echo "=== Firewall behavior test ==="
echo ""

# 1. api.anthropic.com має бути доступний (whitelist)
echo "Test 1: api.anthropic.com (whitelist) має пройти"
if curl -fsS --max-time 5 https://api.anthropic.com -o /dev/null; then
  echo "OK: api.anthropic.com доступний"
else
  echo "FAIL: api.anthropic.com заблокований - whitelist зламаний"
  exit 1
fi
echo ""

# 2. example.com має бути заблокований (default-deny)
echo "Test 2: example.com (не у whitelist) має бути заблокований"
if curl -fsS --max-time 5 https://example.com -o /dev/null 2>&1; then
  echo "FAIL: example.com доступний - default-deny зламаний"
  exit 1
else
  echo "OK: example.com заблокований (timeout або refused)"
fi
echo ""

# 3. pypi.org має бути доступний (whitelist для Python стеку)
echo "Test 3: pypi.org (whitelist для Python) має пройти"
if curl -fsS --max-time 5 https://pypi.org -o /dev/null; then
  echo "OK: pypi.org доступний"
else
  echo "FAIL: pypi.org заблокований - стекоспецифічний whitelist зламаний"
  exit 1
fi
echo ""

# 4. github.com має бути доступний (whitelist)
echo "Test 4: github.com (whitelist) має пройти"
if curl -fsS --max-time 5 https://github.com -o /dev/null; then
  echo "OK: github.com доступний"
else
  echo "FAIL: github.com заблокований - whitelist зламаний"
  exit 1
fi
echo ""

echo "=== Firewall test PASSED ==="
