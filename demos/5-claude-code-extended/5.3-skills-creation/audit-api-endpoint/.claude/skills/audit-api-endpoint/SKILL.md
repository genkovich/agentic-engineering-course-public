---
name: audit-api-endpoint
description: Use when reviewing one HTTP endpoint for production readiness — checks status, Content-Type, body shape, cache headers, and surfaces health-vs-ready confusion. Black-box runtime probe, works on any HTTP server regardless of language (Go, Node, Python, Rust, etc.). Trigger when the user names a single URL to audit, asks about /health or /ready quality, or wants a structured audit report for one endpoint.
allowed-tools: Bash(uv run *), Bash(curl *), Read, Glob, Grep
disable-model-invocation: false
context: fork
agent: Explore
argument-hint: '[url]'
model: opus-4-7
effort: xhigh
---

# audit-api-endpoint

Goal: produce a structured audit of one HTTP endpoint and surface defects the engineer can fix in the same pass.

## Workflow

Use this checklist literally. Mark each step done before moving to the next.

- [ ] Step 1: Plan. Read `templates/audit-report.md` so you know the output shape. Run `uv run ${CLAUDE_SKILL_DIR}/scripts/audit_endpoint.py --help` and confirm the flags exist.
- [ ] Step 2: Verify the URL is reachable. Run `curl -sf -m 5 -o /dev/null -w "%{http_code}\n" "$0" || echo "not reachable"`. Record the raw status; if the host is unreachable, stop and tell the user (no point auditing a URL nothing answers on).
- [ ] Step 3: Run the probe. Run exactly:

  ```
  uv run ${CLAUDE_SKILL_DIR}/scripts/audit_endpoint.py --url "$0" --format json
  ```

  Do not modify the command. The script returns exit code 0 (no blocking findings) or 1 (findings present). Any other code is a usage error and must be reported as-is.

### Loop

1. Run the probe (Step 3).
2. Parse JSON. If findings is empty - report success.
3. If findings present - propose fixes inline (на стороні сервера, поза скілом).
4. Після того як користувач задеплоїв fix - re-run probe проти того ж URL.
5. Loop until findings is empty or user is satisfied.

- [ ] Step 4: Validate. Parse the JSON. If `findings` is empty, write a short report saying so. Otherwise group findings by `category`.
- [ ] Step 5: Render. Use the template in `templates/audit-report.md`. Fill every section. Do not invent findings the script did not produce.

## Якщо URL не передано

When the user asks "audit my API" without naming a URL, do not guess. Ask one clarifying question — which endpoint? Suggest the typical readiness-related paths first:

1. `/health` and `/ready` — public outage signals, audit these first.
2. A read endpoint that returns business data (e.g. `/users/me`, `/products`).
3. A single-purpose info endpoint like `/version`, `/metrics`, `/`.

Ask for the full URL (`http://localhost:3000/health` or `https://api.example.com/health`), not just a path — the probe runs over the network, it needs a host.

## Calling the probe (rigid part)

The script is the source of truth. Run exactly the command in Step 3. Do not add extra flags, do not write your own curl pipeline, do not skip the run because "the URL looks fine". Findings come from the script or they do not exist.

If the endpoint needs an auth header, pass it explicitly: append `--header "Authorization: Bearer $TOKEN"` to Step 3. The script does not read env vars — the agent supplies the value.

## Gotchas

- The script needs `uv` on PATH. If `uv run` fails with `command not found`, instruct the user to install uv (https://docs.astral.sh/uv) and stop.
- Self-signed certs: the probe verifies TLS by default. If the user audits an internal HTTPS host with a self-signed cert, append `--insecure` to Step 3. Only do this if the user explicitly says they trust the host.
- Auth-required endpoints: the probe sends no Authorization header by default. A `401` or `403` will be reported as a finding even if the endpoint is healthy. Either probe a public path or pass `--header "Authorization: ..."`.
- Non-2xx is not always a defect: `404` on `/missing` is correct behaviour. The script reports findings; you decide which matter for the user's intent.
- `/health` returning 200 with `OK` does not mean the system is healthy. The script flags this exact uptime-only pattern. Do not wave it off as "the endpoint works".
- Output truncation: by default the JSON includes only the first 3 findings plus a `truncated: true` flag. Pass `--full` if you need every finding for a long report.

## Output format

Use `templates/audit-report.md`. Keep the structure even if some sections are empty (write "no findings" instead of omitting the section).

## When NOT to use this skill

- Multi-endpoint audits across the whole API. Use a higher-level orchestrator that calls this skill per endpoint.
- Performance audits (latency under load, memory, throughput). The probe fires one request — single-shot wall-clock time is reported as info, not a benchmark.
- Endpoints that require non-trivial auth flow (OAuth login dance, request signing, mTLS). The probe accepts a static header at most. For anything beyond that, audit manually.
- Static source review (is this handler logged? is the route registered?). The probe is a black box — it sees only what the wire returns.


