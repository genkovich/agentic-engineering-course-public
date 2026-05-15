#!/bin/bash
# validate-devcontainer.sh - перевіряє що .devcontainer/devcontainer.json має runArgs
# з NET_ADMIN і NET_RAW capabilities, і postStartCommand запускає init-firewall.sh.
# Без NET_ADMIN/NET_RAW iptables не запуститься у postStartCommand.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEVCONTAINER_JSON="$PROJECT_ROOT/.devcontainer/devcontainer.json"

if [ ! -f "$DEVCONTAINER_JSON" ]; then
  echo "FAIL: $DEVCONTAINER_JSON не існує"
  exit 1
fi

DEVCONTAINER_JSON="$DEVCONTAINER_JSON" python3 <<'PY'
import json, os, sys
with open(os.environ['DEVCONTAINER_JSON']) as f:
    d = json.load(f)
run_args = d.get('runArgs', [])
required_caps = ['--cap-add=NET_ADMIN', '--cap-add=NET_RAW']
missing = [c for c in required_caps if c not in run_args]
if missing:
    print(f"FAIL: devcontainer.json runArgs не містить: {','.join(missing)}")
    print("Без NET_ADMIN/NET_RAW iptables не запуститься, firewall зламаний.")
    sys.exit(1)
print("OK: devcontainer.json runArgs має NET_ADMIN, NET_RAW")
psc = d.get('postStartCommand', '')
if 'init-firewall.sh' not in psc:
    print(f"FAIL: postStartCommand не запускає init-firewall.sh: {psc!r}")
    sys.exit(1)
print("OK: postStartCommand запускає init-firewall.sh")
PY
