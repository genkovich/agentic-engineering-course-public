# SDLC toolkit (знімок v4.5.1)

SDLC-пайплайн для Claude Code: документи-артефакти, Claude Code skills, агенти і чек-листи. Каталог супроводжує Module 6 курсу "Agentic Engineering з Claude" і далі модулі, де фіча доходить до коду, рев'ю і релізу.

> **Дисклеймер.** Це знімок плагіна `sdlc` версії 4.5.1. Канонічна версія живе в [github.com/genkovich/sdlc](https://github.com/genkovich/sdlc) і розвивається там. Якщо хочеш свіжіше, став плагін звідти (спосіб 2 нижче). Артефакти в `examples/` синтетичні (домени `course-lesson-mvp`, `goals-tracking`, `rate-limiting`), справжні робочі артефакти сюди не потрапляють.

## Що тут лежить

| Каталог | Що це |
|---|---|
| `00-overview/` | Definition of Ready / Done, мапа фаз, MVP-vs-Full матриця, rollout plan, метрики процесу |
| `document-templates/` | Шаблони для cross-feature, ручної і legacy роботи (SPEC, CONTEXT-MAP, arc42, ADR, migration plan, rollback, review checklist, task breakdown) |
| `plugin/skills/` | 21 skill: 12 етапів основного пайплайну, `interview`, `scaffold` і 7 допоміжних утиліт |
| `plugin/agents/` | 11 агентів, яких скіли викликають як `sdlc:<name>` (explorer, researcher, strategist, analyst, devils-advocate, critic, test-author, implementer, refactor, reviewer, doc-flow) |
| `plugin/skills/_shared/` | Спільні протоколи для кількох скілів: сократичний цикл, критик, handoff між етапами, матриця розмірів, `target_surfaces`, ростер агентів |
| `plugin/tests/` | Рубрика і фікстури для перевірки скілів |
| `plugin/plugin.json` | Маніфест плагіна (`name: sdlc`, версія) |
| `.claude-plugin/marketplace.json` | Маніфест маркетплейсу, щоб поставити плагін прямо з цього каталогу |
| `examples/course-lesson-mvp/` | Наскрізний приклад: CONTEXT.md, idea-brief.md, PRD.md, sad.md, ADR, data-model.md, staged `migrations/`, OpenAPI, `tasks/` з `tasks.json`, `_review/`, CHANGELOG |
| `examples/goals-tracking/` | Приклад arc42 для модуля з OKR-логікою |
| `examples/rate-limiting/` | Приклад артефактів для cross-cutting фічі |
| `scripts/` | `sdlc_lint.py` (перевірка структури, `make sdlc-check`) і `generate-gates.sh` |

Повний опис кожного скіла, агента і спільного механізму лежить у [`plugin/README.md`](plugin/README.md).

## Як підключити

Команди плагіна в Claude Code мають вигляд `/sdlc:<skill>`, наприклад `/sdlc:interview <slug>`.

### 1. Цей знімок, без встановлення

```bash
git clone https://github.com/genkovich/agentic-engineering-course-public.git
cd agentic-engineering-course-public/modules/6-sdlc/sdlc
claude --plugin-dir ./plugin
```

Плагін живе тільки в цій сесії. Зручно, щоб пройти ДЗ саме на тій версії, що в лекціях.

### 2. Канонічна версія через marketplace

У Claude Code:

```
/plugin marketplace add genkovich/sdlc
/plugin install sdlc@sdlc
```

Так ставиться свіжа версія з [genkovich/sdlc](https://github.com/genkovich/sdlc), і вона оновлюється разом із маркетплейсом. Може трохи відрізнятися від цього знімка.

### 3. Шаблони руками, без плагіна

```bash
mkdir -p docs/features/<your-slug>
cp plugin/skills/fix-term/templates/CONTEXT.md docs/features/<your-slug>/CONTEXT.md
cp plugin/skills/interview/templates/idea-brief.md docs/features/<your-slug>/idea-brief.md
cp plugin/skills/write-prd/templates/PRD-template.md docs/features/<your-slug>/PRD.md
```

Кожен `SKILL.md` описує кроки протоколу, тож їх можна пройти руками, якщо плагін не стоїть.

## Мапа Module 6 → файли toolkit

| Лекція | Тема | Skills і шаблони |
|---|---|---|
| 6.1 | SDLC через артефакти | `00-overview/`, `examples/course-lesson-mvp/`, `plugin/skills/map-architecture/` (скан репо один раз на старті, далі всі читають `docs/architecture-map.md`) |
| 6.2 | Gate 1: словник домену та idea-brief | `plugin/skills/fix-term/` (+ `templates/CONTEXT.md`), `plugin/skills/interview/` (+ `templates/idea-brief.md`), `plugin/skills/classify-size/` |
| 6.3 | PRD | `plugin/skills/write-prd/` (+ `templates/PRD-template.md`) |
| 6.4 | Architecture (SAD + ADR + C4) | `plugin/skills/architecture-design/` (+ `templates/sad-template.md`, `adr-template.md`, `c4-context.md`, `c4-container.md`), `plugin/skills/decide-adr/`, `document-templates/arc42.md`; вхід для SAD дає `map-architecture` |
| 6.5 | Sequence diagrams + data model | `plugin/skills/complete-sequence-diagrams/`, `plugin/skills/generate-data-model/` (+ `templates/data-model.md`, `rules-migrations-baseline.md`) |
| 6.6 | API contracts (OpenAPI) | `plugin/skills/api-forge/` (+ `templates/openapi.yaml`, `events.md`, `cli.md`, `public-api.md`) |
| 6.7 | Tasks | `plugin/skills/break-tasks/`, `plugin/skills/plan-tests/`, `examples/course-lesson-mvp/tasks/` (`_epic.md`, `tracker.md`, `tasks.json` і story-файли) |

## Module 7+ і далі

Ці скіли в лекціях Module 6 не розбираються. Вони продовжують той самий ланцюжок артефактів після tasks, а також закривають старт проєкту і UI.

| Skill | Навіщо |
|---|---|
| `clarify-prd` | Прохід по PRD у пошуках неоднозначностей, правки прямо в `PRD.md` |
| `implement-tasks` | TDD по `tasks.json`: red, green, refactor, gate, commit; переносить staged міграції в живе дерево |
| `review-feature` | Незалежне рев'ю фічі проти PRD і acceptance criteria, звіт у `_review/` |
| `ship-feature` | CHANGELOG, текст PR, перенос фічі в Shipped у `docs/roadmap.md` |
| `verify-ui` | Перевірка acceptance criteria в живому браузері зі скріншотами |
| `roadmap` | `docs/roadmap.md` з таблицями Now / Next / Later / Shipped |
| `scaffold` | Каркас нового проєкту з шаблону після `map-architecture` на порожньому репо |
| `prepare-design-spec` | Один UI design spec з урахуванням репо і вбудованим Definition of Done |
| `user-documentation` | Документація для користувача з живого застосунку: проходи по флоу, скріншоти, скрінкасти за бажанням |

## DoR / DoD коротко

`00-overview/definition-of-ready.md` і `definition-of-done.md` тримають чек-листи переходу між фазами. Кожен skill на старті перевіряє вхідні артефакти. Етапи з позначкою 🚪 у [`plugin/README.md`](plugin/README.md) відмовляються стартувати, поки обов'язкового артефакту немає.

## Що сюди не входить

- Внутрішні конфігурації робочих проєктів, прод-домени, ідентифікатори тікетів
- CI і службові скрипти приватного репозиторію
- Версії плагіна новіші за 4.5.1: їх шукай у [genkovich/sdlc](https://github.com/genkovich/sdlc)
