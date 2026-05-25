---
status: Approved
owner: Kyrylo
reviewers: [Backend Lead, QA]
updated_at: "2026-05-14"
feature_size: S
stage: "16"
ticket: INC-841
---

# Review checklist — Rate limiting

## Correctness
- [ ] AC-01/02/03 з [SPEC.md](SPEC.md) покриті тестами.
- [ ] Lua-script відповідає алгоритму у [data-model.md](data-model.md) дослівно.
- [ ] `Retry-After` обчислюється від найстарішого запису, не від `now + window`.

## Security
- [ ] Rate limit застосовується **після** Auth (user_id з токена, не з body).
- [ ] Ключ у Redis prefixed `rl:` — не колізує з іншими модулями.
- [ ] Lua-EVAL не приймає user-controlled input як код (тільки параметри).

## Performance
- [ ] Один Lua EVAL, не серія команд.
- [ ] `EvalSha` з cache; `Eval` лише при NOSCRIPT.
- [ ] Timeout 50ms задано через `context.WithTimeout`, не client config.

## Observability
- [ ] `rate_limit_decisions_total{decision="allow|deny"}` інкрементується.
- [ ] `rate_limit_redis_errors_total` інкрементується при fail-open.
- [ ] Structured log на fail-open: `WARN rate_limit.redis_unavailable user_id=… err=…`.
- [ ] Alert у Grafana: `rate(rate_limit_redis_errors_total[5m]) > 0.1`.

## API
- [ ] OpenAPI оновлено: `429` + `X-RateLimit-*` headers.
- [ ] Error body: `{"code":"rate_limit.exceeded","message":"…"}`.

## Migrations
- [ ] N/A — без SQL-міграцій.

## Docs
- [ ] CHANGELOG entry у `docs/CHANGELOG.md`.
- [ ] KB note `KB/api/rate-limiting.md` створено.
- [ ] ADR-0007 + ADR-0008 merged (Accepted).
- [ ] Runbook оновлено: «що робити при `rate_limit.redis_unavailable` alert».
