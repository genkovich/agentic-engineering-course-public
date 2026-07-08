#!/usr/bin/env bash
# PreToolUse egress guard — structural safety on the OUTBOUND boundary.
#
# The whole point of lecture 11.1: you cannot reliably stop the agent from
# READING a secret (a child process `cat .env` bypasses file-deny — shown in
# 3.6/3.7). So the durable control is on EGRESS: block secret-shaped material
# from leaving through ANY tool parameter.
#
# Contract (same as Claude Code PreToolUse): the tool call arrives as JSON on
# stdin; exit code 2 = block, stderr = the reason shown to the model/user.
set -euo pipefail

payload="$(cat)"

# Flatten the tool call into one string: command + url + the raw input JSON.
call="$(printf '%s' "$payload" | python3 -c 'import sys,json
d=json.load(sys.stdin); i=d.get("tool_input",{})
print((i.get("command","") or "")+" "+(i.get("url","") or "")+" "+json.dumps(i))' 2>/dev/null || printf '%s' "$payload")"

# Is this call an outbound channel at all?
if printf '%s' "$call" | grep -qiE 'curl|wget|https?://|webhook|nc |ncat'; then
  # secret-shaped material riding in a tool parameter
  if printf '%s' "$call" | grep -qE 'sk-demo-|PAYMENTS_API_KEY|-----BEGIN|AKIA[0-9A-Z]{16}|ghp_[0-9A-Za-z]{36}'; then
    echo "egress-guard: secret-shaped payload in an outbound tool call — blocked" >&2
    exit 2
  fi
  # a secret file feeding an outbound call in one compound command
  if printf '%s' "$call" | grep -qE '\.env|id_rsa|\.pem|\.ssh/'; then
    echo "egress-guard: secret file feeding an outbound call — blocked" >&2
    exit 2
  fi
fi
exit 0
