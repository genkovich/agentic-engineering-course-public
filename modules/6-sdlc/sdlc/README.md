# SDLC toolkit (Module 6 freeze)

Lean SDLC pipeline для Claude Code: документи-артефакти + Claude Code skills + checklists. Цей каталог відповідає матеріалу Module 6 курсу "Agentic Engineering з Claude" — артефакт-орієнтованому SDLC від ідеї до tasks.

> **Дисклеймер.** Це freezed snapshot SDLC toolkit з приватного робочого репозиторію. Канонічна версія еволюціонує далі; тут зберігається версія, що відповідає Module 6 LMS-курсу. Артефакти у `examples/` синтетичні (домени `course-lesson-mvp`, `goals-tracking`, `rate-limiting`) — реальні TeamHub-артефакти не публікуються.

## Що тут лежить

| Каталог | Що це |
|---|---|
| `00-overview/` | Definition of Ready / Done, мапа фаз, MVP-vs-Full матриця, rollout plan |
| `document-templates/` | Cross-feature / manual / legacy шаблони (SPEC, CONTEXT-MAP, arc42, ADR, migration plan, rollback, review checklist, task breakdown) |
| `plugin/skills/` | 11 Claude Code skills: 9 stage-skills + 2 cross-cutting (`fix-term`, `classify-size`) |
| `plugin/plugin.json` | Plugin manifest — `name: sdlc`, version, опис кожного skill |
| `examples/course-lesson-mvp/` | Наскрізний приклад: CONTEXT.md + idea-brief.md + PRD.md + sad.md + ADRs + data-model.md + OpenAPI + tasks/ (з `_epic.md` і `tracker.md`) |
| `examples/goals-tracking/` | Приклад arc42 для модуля з OKR-логікою (синтетичний `goals` модуль) |
| `examples/rate-limiting/` | Приклад артефактів для cross-cutting feature |
| `scripts/` | Допоміжні скрипти (`generate-gates.sh`, `sdlc_lint.py`) |

## Як використати

### 1. Як plugin для Claude Code

```bash
git clone https://github.com/genkovich/agentic-engineering-course-public.git
cd agentic-engineering-course-public/modules/6-sdlc/sdlc

# Опція A: підключити одним рядком через CLI
claude --plugin-dir ./plugin

# Опція B: скопіювати у глобальні plugins
cp -r plugin ~/.claude/plugins/sdlc
```

Після цього команди `/sdlc-interview`, `/sdlc-write-prd`, `/sdlc-architecture-design`, `/sdlc-complete-sequence-diagrams`, `/sdlc-generate-data-model`, `/sdlc-api-forge`, `/sdlc-break-tasks`, `/sdlc-plan-tests`, `/sdlc-decide-adr`, `/sdlc-fix-term`, `/sdlc-classify-size` стають доступні у Claude Code.

### 2. Як шаблони у свій репо (без plugin)

```bash
mkdir -p docs/features/<your-slug>
cp document-templates/SPEC.md docs/features/<your-slug>/PRD.md
# або тягни шаблон з відповідного скіла напряму:
cp plugin/skills/fix-term/templates/CONTEXT.md docs/features/<your-slug>/CONTEXT.md
cp plugin/skills/interview/templates/idea-brief.md docs/features/<your-slug>/idea-brief.md
```

Кожен `SKILL.md` тримає протокол кроків — їх можна виконувати рукою, якщо плагін не встановлено.

### 3. Як reference для домашки

Дивись мапу нижче — кожна лекція Module 6 вказує, які саме файли з цього toolkit використовуються у її ДЗ.

## Мапа Module 6 → файли toolkit

| Лекція | Тема | Skills і шаблони |
|---|---|---|
| 6.1 | SDLC через артефакти | `00-overview/`, `examples/course-lesson-mvp/` |
| 6.2 | Gate 1 — словник домену та idea-brief | `plugin/skills/fix-term/` (+ `templates/CONTEXT.md`), `plugin/skills/interview/` (+ `templates/idea-brief.md`), `plugin/skills/classify-size/` |
| 6.3 | PRD | `plugin/skills/write-prd/` (+ `templates/PRD-template.md`) |
| 6.4 | Architecture (SAD + ADR + C4) | `plugin/skills/architecture-design/` (+ `templates/sad-template.md`, `adr-template.md`, `c4-context.md`, `c4-container.md`), `plugin/skills/decide-adr/`, `document-templates/arc42.md` |
| 6.5 | Sequence diagrams + data model | `plugin/skills/complete-sequence-diagrams/`, `plugin/skills/generate-data-model/` (+ `templates/data-model.md`, `rules-migrations-baseline.md`) |
| 6.6 | API contracts (OpenAPI) | `plugin/skills/api-forge/` (+ `templates/openapi.yaml`, `events.md`) |
| 6.7 | Tasks | `plugin/skills/break-tasks/`, `plugin/skills/plan-tests/`, `examples/course-lesson-mvp/tasks/` (з `_epic.md` + `tracker.md` + 27 story-файлів) |

## DoR / DoD коротко

`00-overview/definition-of-ready.md` і `definition-of-done.md` містять чек-листи переходу між фазами. Кожен skill робить prereq-check на старті і відмовляється запускатися, якщо обов'язкових вхідних артефактів немає.

## Що поза скоупом цього freeze

- Capstone / runner (Module 7+) — тут лише до tasks
- Internal TeamHub конфігурації, prod-домени, ticket-ідентифікатори
- Робочі гілки приватного репозиторію
