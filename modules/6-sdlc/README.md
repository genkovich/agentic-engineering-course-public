# Module 6 — SDLC через артефакти

Як проєктувати фічу з агентом без втрати контексту: інформація живе у файлах-артефактах (CONTEXT, idea-brief, PRD, sad, data-model, OpenAPI, tasks/), а Claude Code skills проводять тебе по фазах від ідеї до атомарних задач.

## Лекції модуля

- 6.1 SDLC через артефакти — мапа фаз і гейтів, "чому файли, а не пам'ять сесії"
- 6.2 Gate 1: словник домену → idea-brief — `fix-term`, `interview`, `classify-size`
- 6.3 PRD — `write-prd`, PRD-template, Claude.ai/Projects як альтернативний транспорт
- 6.4 Architecture Design — `architecture-design`, arc42 12 секцій + ADR + C4 L1/L2
- 6.5 Sequence diagrams + data model — `complete-sequence-diagrams`, `generate-data-model`, expand/backfill/contract міграції
- 6.6 API contracts (OpenAPI) — `api-forge`, drift check, scenarios A vs B
- 6.7 Tasks — `break-tasks`, `plan-tests`, 3-stage breakdown, `_epic.md` + `tracker.md`

## Артефакт модуля

| Toolkit | Що показує |
|---|---|
| [sdlc/](./sdlc/) | Lean SDLC pipeline: 11 skills + document templates + наскрізний example. Клонуй, підключи як plugin, або тягни шаблони у свій репо |

## Як використовувати

```bash
cd modules/6-sdlc/sdlc
claude --plugin-dir ./plugin
# далі в Claude Code: /sdlc-interview <slug>
```

Детальний розбір — у [`sdlc/README.md`](./sdlc/README.md) з мапою лекцій до файлів і трьома способами використання (plugin / шаблони у свій репо / reference для ДЗ).

## Pre-requisites

- Claude Code локально (див. Module 3)
- `git`
- Свій робочий репо для домашки (можна один зі starter-проєктів Module 3)

## ДЗ модуля

Кожна лекція має простий і складний рівень. Простий — взяти готовий skill/template з `sdlc/` і запустити. Складний — переробити під свій pet-проект або фічу. Деталі — у LMS-уроках відповідної лекції.
