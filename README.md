# Agentic Engineering з Claude — public demos

Public repository for the **Agentic Engineering з Claude** course. Contains hands-on demos for self-learners and homework artifacts for cohort participants.

> Курс ведеться українською. Лекції та теорія — у LMS курсу. Цей репо тримає тільки **код, що клонується і запускається**.

## Modules covered here

| Module | Тема | Тип |
|---|---|---|
| [Module 1 — LLM Mechanics](modules/1-llm-mechanics/) | Токени, контекстне вікно, стохастичність, embeddings | demos (4, runnable) |
| [Module 2 — Ecosystem](modules/2-ecosystem/) | Tool use, agentic loop, RAG vs fine-tune, prompt injection, privacy | demos (6, runnable) |
| [Module 3 — Claude Code Setup](modules/3-claude-code-setup/) | Встановлення, settings, permissions, sandbox, devcontainer | starters (4 стеки) |
| [Module 4 — Prompting Mastery](modules/4-prompting-mastery/) | Промпти, контекст, `.claude/`, `CLAUDE.md`, rules, Plan/Think, BC, legacy refactor | demos (text + runnable) |
| [Module 5 — Claude Code Extended](modules/5-claude-code-extended/) | Slash commands, custom skills, subagents, hooks, output styles, plan mode, plugins | demos (~7 production-ready) |
| [Module 6 — SDLC через артефакти](modules/6-sdlc/) | Idea → CONTEXT/PRD/SAD/data-model/OpenAPI/tasks через 11 skills і шаблони | SDLC toolkit + наскрізний example |
| [Module 7 - Execution & Scale](modules/7-execution-scale/) | Патерни виконання: Ralph, /goal, dynamic workflows, фон/розклад, feedback loops, TDD | demos (7, runnable) |
| [Module 8 - MCP](modules/8-mcp/) | Власний MCP-сервер і клієнт, транспорти, advanced-можливості і безпека MCP | demos (3, runnable) |
| [Module 9 — Collaboration](modules/9-collaboration/) | Git workflow, worktrees, merge/cleanup, PR, code review локально й на платформі, реліз і docs | demos (7, runnable) |
| [Module 10 — Agent Teams](modules/10-agent-teams/) | Evals і регресії, agentic debugging | demos (2, runnable) |

Лекції та теорія всіх модулів — у LMS курсу; тут — код, що клонується і запускається.

## Як використовувати

### Modules 1-2 demos

```bash
cd modules/1-llm-mechanics/1.2-token-counter
pip install -r requirements.txt && make run
```

Кожен demo — самостійна Python-директорія (`README.md`, `main.py`, `requirements.txt`, `Makefile`, `.env.example`). Потрібен `ANTHROPIC_API_KEY`. Перелік демо до лекцій — у README модулів [1](modules/1-llm-mechanics/README.md) і [2](modules/2-ecosystem/README.md).

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

Три runnable демо: task-store сервер (stdio + HTTP), канал web-chat і власний MCP-клієнт. Мапа демо до лекцій — у [`modules/8-mcp/README.md`](modules/8-mcp/README.md).

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
    ├── 1-llm-mechanics/            як LLM працює зсередини, 4 runnable демо (Module 1)
    │   ├── README.md               мапа демо → лекцій
    │   ├── 1.2-token-counter/      токени, ціна input/output, UA vs EN (1.1-1.2)
    │   ├── 1.3-context-window/     вигорання контекстного вікна за сесію (1.3, 1.7)
    │   ├── 1.4-stochasticity/      той самий промпт через T=0/0.5/1.0 (1.4)
    │   └── 1.9-embeddings/         cosine similarity, king-man+woman≈queen (1.9)
    ├── 2-ecosystem/                LLM → агент: tool use, RAG, захисти, 6 демо (Module 2)
    │   ├── README.md               мапа демо → лекцій
    │   ├── 2.1-tool-use/           базовий tool use: tool_use → tool_result (2.1-2.2)
    │   ├── 2.3-agentic-loop/       observe → think → act без SDK helpers (2.3)
    │   ├── 2.5-rag/                RAG pipeline: PGVector + embeddings + Claude (2.5)
    │   ├── 2.5-fine-tune/          QLoRA з Unsloth на TinyLlama, Colab T4 (2.5)
    │   ├── 2.6-prompt-injection/   3 типи атак + defense-in-depth pipeline (2.6)
    │   └── 2.7-data-privacy/       env vars що контролюють telemetry (2.7)
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
    ├── 8-mcp/                       MCP: сервер, канал, клієнт (Module 8)
    │   ├── README.md                мапа демо → лекцій, швидкий старт
    │   ├── 8.6-first-mcp-server/    task-store: tools/resource/prompt, stdio + HTTP (8.6-8.8, 8.10)
    │   ├── 8.8-web-chat-channel/    канал Claude Code: MCP-канал + веб-чат на SSE (8.8)
    │   └── 8.9-mcp-client/          власний клієнт: listTools → tool-use loop (8.9)
    ├── 9-collaboration/             git-командна робота, 7 runnable демо (Module 9)
    │   ├── README.md                мапа демо → лекцій
    │   ├── 9.1-git-workflow/        trunk-based, коміти, bisect, відкат, секрет-guard (9.1)
    │   ├── 9.2-git-worktrees/       паралельні агенти, ізоляція оточення (9.2)
    │   ├── 9.3-worktree-merge-cleanup/  merge, конфлікти, safety-hook, cleanup (9.3)
    │   ├── 9.4-pull-requests/       PR-воркфлоу з агентом (9.4)
    │   ├── 9.5-code-review/         локальне рев'ю в сесії: /code-review, /security-review (9.5)
    │   ├── 9.6-github-platform/     рев'ю на платформі: GitHub App, екосистема рев'юерів (9.6)
    │   └── 9.7-release-docs/        локальні skills → CI release pipeline, docs (9.7)
    └── 10-agent-teams/              від агента до команд агентів (Module 10)
        ├── 10.3-evals-regression/   golden-task evals для .claude/ (10.3)
        └── 10.5-agentic-debugging/  агентний дебаг, bisect (10.5)
```

## Курс

Курс «Agentic Engineering з Claude» — 11 модулів. У public репо зараз — Modules 1 (LLM mechanics demos), 2 (ecosystem demos), 3 (starters), 4 (prompting demos), 5 (Claude Code extended), 6 (SDLC toolkit), 7 (execution & scale demos), 8 (MCP demos), 9 (collaboration demos) і 10 (agent teams demos).

Деталі курсу: писати [@genkovich у Telegram](https://t.me/genkovich).

## License

MIT. Дивись [LICENSE](LICENSE).
