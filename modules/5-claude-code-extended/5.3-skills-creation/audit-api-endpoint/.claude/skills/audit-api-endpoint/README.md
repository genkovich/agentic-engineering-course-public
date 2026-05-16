# audit-api-endpoint skill

Audit one HTTP endpoint for production-readiness defects: missing Content-Type,
uptime-only health checks, suspicious status codes, malformed bodies, missing
cache headers. Language- and framework-agnostic — works against any HTTP
server (Go, Node, Python, Rust, anything that speaks HTTP).

## Install (personal scope)

Copy this directory into your personal skills folder:

```bash
cp -r .claude/skills/audit-api-endpoint ~/.claude/skills/
```

Or pull it directly from the course repo:

```bash
git clone --depth=1 https://github.com/your-org/agentic-engineering-course /tmp/c
cp -r /tmp/c/demos/5-claude-code-extended/lecture-3/audit-api-endpoint/.claude/skills/audit-api-endpoint ~/.claude/skills/
```

The skill is self-contained — only `SKILL.md`, `scripts/audit_endpoint.py`,
`templates/audit-report.md`, and this README live inside the skill directory.
Nothing else is required.

## Requirements

- [`uv`](https://docs.astral.sh/uv/) — runs the script and resolves its
  declared dependencies (none right now, the script is stdlib-only). Install:
  `curl -LsSf https://astral.sh/uv/install.sh | sh`.

That's it. No Python project, no `requirements.txt`, no virtualenv to manage.

## Usage

In Claude Code:

```
/audit-api-endpoint http://localhost:3000/health
/audit-api-endpoint https://api.example.com/users/me
```

Standalone (without the skill harness):

```
uv run ~/.claude/skills/audit-api-endpoint/scripts/audit_endpoint.py --url https://example.com
```

## What it checks

- HTTP status code (2xx/3xx/4xx/5xx classification + reachability)
- `Content-Type` header (present? matches body shape?)
- Body shape (valid JSON if `application/json` is claimed; valid UTF-8 if `text/*`)
- `Cache-Control` / `ETag` / `Last-Modified` presence (info-level)
- `/health` vs `/ready` hint (flags uptime-only health pattern)
- Single-shot wall-clock response time (info-level, not a benchmark)

## What it does NOT check

- Static source (the skill is runtime-only — black box, no source parsing)
- Multi-endpoint flows or contract testing across the API
- Auth semantics beyond reporting `401` / `403`
- Performance under load or concurrency behaviour
- OAuth / signed requests / mTLS — pass at most one static `--header`

For anything beyond a single-URL black-box probe, reach for a different tool.
