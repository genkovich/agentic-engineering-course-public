#!/bin/bash
# init-firewall.sh - default-deny outbound + minimal whitelist для Claude Code container.
# Запускається у postStartCommand devcontainer або entrypoint docker compose.
# Потребує capabilities NET_ADMIN і NET_RAW (cap_add у Docker Compose або runArgs у devcontainer).

set -euo pipefail

# 1. Скинути попередні правила, поставити default policy
iptables -F OUTPUT
iptables -F INPUT
iptables -P OUTPUT DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP

# 2. Loopback завжди дозволений
iptables -A INPUT  -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# 3. Уже встановлені з'єднання - ACCEPT (без цього навіть DNS-відповідь не пройде)
iptables -A INPUT  -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 4. DNS (UDP/TCP 53) - без розрізнення доменів
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT

# 5. Whitelist через ipset (динамічне резолювання доменів у IP)
ipset destroy claude-allowed 2>/dev/null || true
ipset create  claude-allowed hash:net family inet hashsize 1024 maxelem 65536

ALLOWED_DOMAINS=(
  "api.anthropic.com"
  "statsig.anthropic.com"
  "sentry.io"
  "registry.npmjs.org"
  "api.github.com"
  "github.com"
  "objects.githubusercontent.com"
  "codeload.github.com"
)

for domain in "${ALLOWED_DOMAINS[@]}"; do
  ips=$(getent ahosts "$domain" | awk '/STREAM/ {print $1}' | sort -u)
  if [ -z "$ips" ]; then
    echo "WARN: не вдалось зрезолвити $domain - пропускаємо"
    continue
  fi
  for ip in $ips; do
    ipset add claude-allowed "$ip" 2>/dev/null || true
  done
done

# 6. GitHub CIDR ranges - отримуємо з api.github.com/meta (тимчасово відкриваємо api.github.com)
gh_ip=$(getent ahosts api.github.com | awk '/STREAM/ {print $1; exit}')
if [ -n "$gh_ip" ]; then
  iptables -I OUTPUT 1 -d "$gh_ip" -p tcp --dport 443 -j ACCEPT
  github_cidrs=$(curl -fsS --max-time 10 https://api.github.com/meta \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('\n'.join(c for c in d.get('git',[]) if ':' not in c))" \
    || true)
  for cidr in $github_cidrs; do
    ipset add claude-allowed "$cidr" 2>/dev/null || true
  done
fi

# 7. ACCEPT для всіх IP/CIDR з whitelist на портах 80/443
iptables -A OUTPUT -p tcp -m set --match-set claude-allowed dst --dport 443 -j ACCEPT
iptables -A OUTPUT -p tcp -m set --match-set claude-allowed dst --dport 80  -j ACCEPT

# 8. Self-validation - переконатись що firewall працює як треба
echo "=== Firewall self-validation ==="

if curl -fsS --max-time 5 https://api.anthropic.com -o /dev/null; then
  echo "OK: api.anthropic.com доступний"
else
  echo "FAIL: api.anthropic.com має бути доступний - whitelist зламаний"
  exit 1
fi

if curl -fsS --max-time 5 https://example.com -o /dev/null 2>&1; then
  echo "FAIL: example.com має бути заблокований - default-deny зламаний"
  exit 1
else
  echo "OK: example.com заблокований (як і має бути)"
fi

echo "=== Firewall ready ==="
