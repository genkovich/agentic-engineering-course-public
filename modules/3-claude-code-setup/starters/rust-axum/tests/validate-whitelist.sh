#!/bin/bash
# validate-whitelist.sh - перевіряє консистентність sandbox і firewall whitelists.
# sandbox.network.allowedDomains у .claude/settings.json має повністю збігатися
# з ALLOWED_DOMAINS у .devcontainer/init-firewall.sh.
#
# Чому: якщо домен у sandbox але не у firewall - Claude дозволить запит,
# а iptables його заблокує (silent fail). Якщо домен у firewall але не у sandbox -
# навпаки, Claude заблокує до того як firewall взагалі побачить пакет.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SETTINGS_JSON="$PROJECT_ROOT/.claude/settings.json"
INIT_FW="$PROJECT_ROOT/.devcontainer/init-firewall.sh"

if [ ! -f "$SETTINGS_JSON" ] || [ ! -f "$INIT_FW" ]; then
  echo "FAIL: settings.json або init-firewall.sh не знайдено"
  exit 1
fi

SETTINGS_JSON="$SETTINGS_JSON" INIT_FW="$INIT_FW" python3 <<'PY'
import json, os, re, sys
with open(os.environ['SETTINGS_JSON']) as f:
    s = json.load(f)
sandbox_domains = set(s.get('sandbox', {}).get('network', {}).get('allowedDomains', []))
with open(os.environ['INIT_FW']) as f:
    fw = f.read()
m = re.search(r'ALLOWED_DOMAINS=\(([^)]+)\)', fw, re.DOTALL)
if not m:
    print("FAIL: ALLOWED_DOMAINS array не знайдено у init-firewall.sh")
    sys.exit(1)
fw_domains = set(re.findall(r'"([^"]+)"', m.group(1)))
only_sandbox = sandbox_domains - fw_domains
only_firewall = fw_domains - sandbox_domains
if only_sandbox or only_firewall:
    if only_sandbox:
        print(f"FAIL: тільки у sandbox.allowedDomains, не у firewall: {sorted(only_sandbox)}")
    if only_firewall:
        print(f"FAIL: тільки у firewall, не у sandbox.allowedDomains: {sorted(only_firewall)}")
    print("Whitelists мають збігатися - інакше Claude дозволить запит, а firewall його заблокує (або навпаки).")
    sys.exit(1)
print(f"OK: sandbox і firewall whitelists збігаються ({len(sandbox_domains)} доменів)")
PY
