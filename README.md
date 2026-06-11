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
| [Module 7 - Execution & Scale](modules/7-execution-scale/) | Патерни виконання: Ralph, /goal, dynamic workflows, фон/розклад, feedback loops, TDD | demos (7, runnable) |
| [Module 8 - MCP](modules/8-mcp/) | Власний MCP-сервер і клієнт, транспорти, дистрибуція, прод, MCP vs CLI | demos (3, runnable) + fixtures |

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

### Module 8 demos

```bash
cd modules/8-mcp/8.6-first-mcp-server
make install && make test   # 17 тестів зелені
make run                    # MCP-сервер на stdio; make run-http — Streamable HTTP на :3335
```

Три runnable демо (task-store сервер, notify-hub з Dockerfile + DEPLOY.md, власний клієнт) і два набори фікстур (дистрибуція, аудит конфігу). Мапа демо до лекцій — у [`modules/8-mcp/README.md`](modules/8-mcp/README.md).

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
    ├── 6-sdlc/
    │   ├── README.md
    │   └── sdlc/                    SDLC toolkit (Module 6 freeze)
    │       ├── README.md            мапа лекцій → файлів, способи використання
    │       ├── 00-overview/         DoR / DoD / process map / MVP-vs-Full
    │       ├── document-templates/  cross-feature / legacy / manual snippets
    │       ├── plugin/              Claude Code plugin: 11 skills (sdlc-*)
    │       ├── examples/            course-lesson-mvp / goals-tracking / rate-limiting
    │       └── scripts/             generate-gates.sh, sdlc_lint.py
    ├── 7-execution-scale/           патерни виконання, 7 runnable демо (Module 7)
    │   ├── README.md                мапа патернів → лекцій, як запустити
    │   ├── 7.1-execution-map/       seed-домен snippets + мапа «задача → патерн» (7.1)
    │   ├── 7.2-ralph-loop/          канонічний Ralph: bash-цикл + sentinel DONE (7.2)
    │   ├── 7.3-goal/                /goal: умова завершення + модель-оцінювач (7.3)
    │   ├── 7.4-dynamic-workflows/   agent()/parallel()/pipeline() оркестрація (7.4)
    │   ├── 7.5-background/          матриця рівнів розкладу + рецепти (7.5)
    │   ├── 7.6-feedback-loops/      детермінований гейт + браузер через Playwright (7.6)
    │   └── 7.7-tdd-discipline/      RGR однією командою: orchestrator + 3 agents (7.7)
    └── 8-mcp/                       MCP: сервер, клієнт, дистрибуція (Module 8)
        ├── README.md                мапа демо → лекцій, швидкий старт
        ├── 8.6-first-mcp-server/    task-store: tools/resource/prompt, stdio + HTTP (8.6-8.8, 8.10-8.11)
        ├── 8.8-notify-hub/          webhook-приймач + MCP endpoint, Dockerfile + DEPLOY.md (8.8, 8.12)
        ├── 8.9-mcp-client/          власний клієнт: listTools → tool-use loop (8.9)
        ├── 8.11-distribution/       заготовки mcpb-бандла і MCP Registry (8.11)
        └── 8.13-audit-config/       фікстура .mcp.json для аудиту «MCP чи CLI» (8.13)
```

## Курс

Курс «Agentic Engineering з Claude» — 11 модулів. У public репо зараз — Modules 3 (starters), 4 (prompting demos), 5 (Claude Code extended), 6 (SDLC toolkit), 7 (execution & scale demos) і 8 (MCP demos).

Деталі курсу: писати [@genkovich у Telegram](https://t.me/genkovich).

## License

MIT. Дивись [LICENSE](LICENSE).
