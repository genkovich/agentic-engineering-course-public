# Capstone Log

Auto-append лог метрик F1 vs F2. Заповнюється після кожного коміту в `feature-1/` або `feature-2/`.

Auto-rule у scaffold CLAUDE.md: «після коміту в `feature-1/` або `feature-2/` дописати рядок сюди з timestamp, коротким описом, метрикою (час від старту фічі, № промпта, чи спрацював hook)».

## Формат рядка

```
YYYY-MM-DD HH:MM | F1|F2 | commit <sha> | "<short desc>" | prompt #N | <metric>
```

## F1 — manual

<!-- приклади:
2026-05-12 14:00 | F1 | start | feature: Note CRUD | prompt #1 | t=0
2026-05-12 14:32 | F1 | commit a1b2c3 | "migration notes" | prompt #4 | 32 min
2026-05-12 16:05 | F1 | commit d4e5f6 | "tests note repo" | prompt #11 | manually fixed import 2x
2026-05-12 17:10 | F1 | DONE | green tests | prompt #18 | total=3h10m
-->

## Phase B — extraction notes

<!-- що виніс у плагін, чому саме це:
- prompts #3, #7, #14 повторювали "scaffold migration з UUID v7" → /feature-scaffold
- ручний запуск `make test` після кожної зміни → pre-commit hook
- руками перевіряв імпорти між модулями → PreToolUse Edit hook
-->

## F2 — with plugin

<!-- приклади:
2026-05-13 10:00 | F2 | start | feature: Bookmark CRUD | prompt #1 | t=0
2026-05-13 10:04 | F2 | /feature-scaffold bookmark | 1 plugin call | 4 min
2026-05-13 10:15 | F2 | hook BC-check blocked import | resolved by moving to shared/
2026-05-13 10:35 | F2 | DONE | green tests | prompt #5 | total=35m
-->

## Summary

| Metric | F1 | F2 | Δ |
|---|---|---|---|
| Total time | | | |
| Prompts | | | |
| Manual fixes | | | |
| Hook hits | — | | |
