# Agentic Engineering з Claude — public demos

Public repository for the **Agentic Engineering з Claude** course. Contains hands-on demos for self-learners and homework artifacts for cohort participants.

> Курс ведеться українською. Лекції та теорія — у LMS курсу. Цей репо тримає тільки **код, що клонується і запускається**.

## Modules covered here

| Module | Тема | Тип |
|---|---|---|
| [Module 3 — Claude Code Setup](modules/3-claude-code-setup/) | Встановлення, settings, permissions, sandbox, devcontainer | starters (4 стеки) |
| [Module 4 — Prompting Mastery](modules/4-prompting-mastery/) | Промпти, контекст, `.claude/`, `CLAUDE.md`, rules, Plan/Think, BC, legacy refactor | demos (text + runnable) |
| [Module 5 — Claude Code Extended](modules/5-claude-code-extended/) | Slash commands, custom skills, subagents, hooks, output styles, plan mode, plugins | demos (~7 production-ready) |
| [Module 6 — SDLC через артефакти](modules/6-sdlc/) | Idea → CONTEXT/PRD/SAD/data-model/OpenAPI/tasks через 11 skills і шаблони | SDLC toolkit + наскрізний example |

Інші модулі курсу — окремо у LMS.

## Як використовувати

### Module 3 starters

```bash
# Знайди starter під свій стек
cd modules/3-claude-code-setup/3.9-starters/go-chi  # або nodejs-typescript / python-fastapi / rust-axum

# Відкрий у VS Code, натисни "Reopen in Container" (потрібен Docker Desktop)
# Усередині контейнера:
make verify  # усі security checks мають пройти
```

Альтернатива devcontainer: `docker compose up`.

### Module 5 demos

```bash
cd modules/5-claude-code-extended/5.2-skills-intro/pdf-form-filler
make demo  # прогнати end-to-end
```

Кожен demo — окрема директорія з власним `Makefile`, `README.md`, `.claude/skills/<name>/SKILL.md`. Структура `.claude/skills/` всередині demo дозволяє склонувати demo як локальний проєкт і запустити Claude Code там, не торкаючись свого основного `~/.claude/`.

Детальний розбір кожного demo — у [`modules/5-claude-code-extended/README.md`](modules/5-claude-code-extended/README.md).

### Module 6 SDLC toolkit

```bash
cd modules/6-sdlc/sdlc
claude --plugin-dir ./plugin
# далі в Claude Code: /sdlc-interview <your-slug>
```

Toolkit з 11 skills (interview, write-prd, architecture-design, …) і шаблонами артефактів. Можна підключити як plugin, скопіювати шаблони у свій репо рукою, або взяти за reference для домашки Module 6. Детально — у [`modules/6-sdlc/sdlc/README.md`](modules/6-sdlc/sdlc/README.md) з мапою лекцій до файлів.

## Pre-requisites

- Claude Code локально (див. Module 3)
- [uv](https://docs.astral.sh/uv/) для self-contained Python скриптів у skills
- Docker Desktop (для devcontainer і `docker compose`)
- ANTHROPIC_API_KEY у `.env` (або OAuth через `claude auth login`)

## Structure

```
.
├── README.md
├── LICENSE                 MIT
└── modules/                один корінь курсу, лекційні та runnable артефакти разом
    ├── 3-claude-code-setup/
    │   ├── README.md
    │   └── 3.9-starters/            cloneable working projects (Module 3)
    │       ├── go-chi/
    │       ├── nodejs-typescript/
    │       ├── python-fastapi/
    │       └── rust-axum/
    ├── 4-prompting-mastery/
    │   ├── README.md
    │   ├── 4.1-prompts/             text examples (PROMPTS.md, не runnable) (4.1)
    │   ├── 4.8-bc/                  Bounded Contexts — Go × TS × Py × 3 stages (4.8)
    │   └── 4.9-legacy-refactor/     FastAPI legacy → account через 7 skills (4.9)
    ├── 5-claude-code-extended/
    │   ├── README.md
    │   ├── 5.2-skills-intro/        PDF form-filler skill (5.2)
    │   ├── 5.3-skills-creation/     audit-api-endpoint skill walkthrough (5.3)
    │   ├── 5.4-hooks/               hooks toolkit з 13 hooks (5.4)
    │   ├── 5.5-plugins/             3 sub-demos: before/after/red-flag (5.5)
    │   └── 5.7-sdk/                 release-notes via claude -p (5.7)
    └── 6-sdlc/
        ├── README.md
        └── sdlc/                    SDLC toolkit (Module 6 freeze)
            ├── README.md            мапа лекцій → файлів, способи використання
            ├── 00-overview/         DoR / DoD / process map / MVP-vs-Full
            ├── document-templates/  cross-feature / legacy / manual snippets
            ├── plugin/              Claude Code plugin: 11 skills (sdlc-*)
            ├── examples/            course-lesson-mvp / goals-tracking / rate-limiting
            └── scripts/             generate-gates.sh, sdlc_lint.py
```

## Курс

Курс «Agentic Engineering з Claude» — 11 модулів. У public репо зараз — Modules 3 (starters), 4 (prompting demos), 5 (Claude Code extended) і 6 (SDLC toolkit).

Деталі курсу: писати [@genkovich у Telegram](https://t.me/genkovich).

## License

MIT. Дивись [LICENSE](LICENSE).
