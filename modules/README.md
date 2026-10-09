# Module → Artifacts mapping

Таблиця відповідності між модулями курсу і demos / starters / recipes у repo.

Працюєш на Windows — спершу [WINDOWS.md](../WINDOWS.md): де запускати bash-скрипти і Makefile'и, що працює натівно у PowerShell.

## Module 1 - LLM Mechanics

Тема модуля: внутрішня механіка LLM (токени, контекстне вікно, латентність, ціна, embeddings, агентний loop).

| Lecture | Тема | Demo |
|---|---|---|
| 1.1, 1.2 | Що таке токен, input vs output ціна | [1-llm-mechanics/1.2-token-counter](./1-llm-mechanics/1.2-token-counter) |
| 1.3, 1.7 | Контекстне вікно, stateless природа моделі | [1-llm-mechanics/1.3-context-window](./1-llm-mechanics/1.3-context-window) |
| 1.4 | Стохастичність, temperature, промпт як ручка | [1-llm-mechanics/1.4-stochasticity](./1-llm-mechanics/1.4-stochasticity) |
| 1.9 | Embeddings, cosine similarity, vector arithmetic | [1-llm-mechanics/1.9-embeddings](./1-llm-mechanics/1.9-embeddings) |

Demos самостійні: запускаються Python-скриптом, ілюструють одну концепцію.

## Module 2 - Ecosystem and Agentic Mindset

Тема модуля: екосистема навколо LLM (tool use, coding assistants, fine-tuning vs RAG vs prompting, prompt injection, агентний loop як патерн).

| Lecture | Тема | Demo |
|---|---|---|
| 2.1, 2.2 | Tool use, coding assistant | [2-ecosystem/2.1-tool-use](./2-ecosystem/2.1-tool-use) |
| 2.3 | Agentic loop (observe → think → act) | [2-ecosystem/2.3-agentic-loop](./2-ecosystem/2.3-agentic-loop) |
| 2.5 | RAG pipeline (PGVector + OpenAI + Claude) | [2-ecosystem/2.5-rag](./2-ecosystem/2.5-rag) |
| 2.5 | Fine-tuning опенсорс (QLoRA + Unsloth) | [2-ecosystem/2.5-fine-tune](./2-ecosystem/2.5-fine-tune) |
| 2.6 | Prompt injection і defense in depth | [2-ecosystem/2.6-prompt-injection](./2-ecosystem/2.6-prompt-injection) |
| 2.7 | Data privacy: telemetry env vars | [2-ecosystem/2.7-data-privacy](./2-ecosystem/2.7-data-privacy) |

## Module 3 - Claude Code Setup

Тема модуля: встановлення Claude Code, налаштування під свій стек, ключові режими роботи (сесії, compaction) і блок безпеки (permissions, sandbox, devcontainer).

| Lecture | Тема | Що з starter покриває |
|---|---|---|
| 3.4 | Settings.json - повний гід | `.claude/settings.json` (Project tier), `.claude/settings.local.json.example` (Local) |
| 3.6 | Permissions | `.claude/settings.json` блок `permissions` (deny secrets, allow workflow) |
| 3.7 | Sandboxing | `.claude/settings.json` блок `sandbox`, тести `tests/sandbox-leak.test.sh` |
| 3.8 | Docker та devcontainers | `.devcontainer/{devcontainer.json, Dockerfile, init-firewall.sh}`, `docker-compose.yml` |
| 3.9 | Claude Code поза терміналом + capstone HW | весь starter як "Шлях B" для capstone |

Reference приклади з лекцій (для Шляху A capstone, написати конфіг з нуля) — окремі артефакти на тому ж рівні що starters:

| Reference | Лекція | Що показує |
|---|---|---|
| [3-claude-code-setup/3.3-commands](./3-claude-code-setup/3.3-commands) | 3.3 | Довідник slash-команд Claude Code |
| [3-claude-code-setup/3.4-settings](./3-claude-code-setup/3.4-settings) | 3.4 | 3 tier settings.json (User, Project, Local) |
| [3-claude-code-setup/3.6-permissions](./3-claude-code-setup/3.6-permissions) | 3.6 | 4 пресети permissions (team-shared, secrets, python, go) |
| [3-claude-code-setup/3.7-sandbox](./3-claude-code-setup/3.7-sandbox) | 3.7 | Sandbox config + init-firewall.sh |
| [3-claude-code-setup/3.8-devcontainer](./3-claude-code-setup/3.8-devcontainer) | 3.8 | devcontainer.json, Dockerfile, docker-compose.yml |

Всі 4 starters покривають той самий набір лекцій:

| Starter | Лекції 3.4, 3.6, 3.7, 3.8, 3.9 |
|---|---|
| [3.9-starters/nodejs-typescript](./3-claude-code-setup/3.9-starters/nodejs-typescript/) | повне покриття |
| [3.9-starters/python-fastapi](./3-claude-code-setup/3.9-starters/python-fastapi/) | повне покриття |
| [3.9-starters/go-chi](./3-claude-code-setup/3.9-starters/go-chi/) | повне покриття |
| [3.9-starters/rust-axum](./3-claude-code-setup/3.9-starters/rust-axum/) | повне покриття |

Лекції 3.1-3.5 проходяться без коду, тільки CLI і конфіг. Starter використовується з Lecture 3.6 і далі.

## Module 6 - SDLC через артефакти

Тема модуля: проєктування фічі з агентом без втрати контексту — інформація живе у файлах-артефактах, які працюють гейтами між фазами від ідеї до атомарних задач у tasks/.

| Lecture | Тема | Артефакт |
|---|---|---|
| 6.1 | SDLC через артефакти — мапа фаз і гейтів | [sdlc/README.md](../sdlc/README.md), [00-overview/](../sdlc/00-overview/) |
| 6.2 | Gate 1: словник домену → idea-brief | [fix-term](../sdlc/plugin/skills/fix-term/), [interview](../sdlc/plugin/skills/interview/) |
| 6.3 | PRD | [write-prd](../sdlc/plugin/skills/write-prd/) |
| 6.4 | Architecture Design (arc42 + ADR + C4) | [architecture-design](../sdlc/plugin/skills/architecture-design/) |
| 6.5 | Sequence diagrams + data model | [complete-sequence-diagrams](../sdlc/plugin/skills/complete-sequence-diagrams/), [generate-data-model](../sdlc/plugin/skills/generate-data-model/) |
| 6.6 | API contracts (OpenAPI) | [api-forge](../sdlc/plugin/skills/api-forge/) |
| 6.7 | Tasks breakdown + test plan | [break-tasks](../sdlc/plugin/skills/break-tasks/), [plan-tests](../sdlc/plugin/skills/plan-tests/) |

Артефакт модуля — toolkit `sdlc/` у корені репо (на нього посилаються LMS-уроки), модульний README з мапою лекцій: [6-sdlc](./6-sdlc). Наскрізний приклад усіх артефактів однієї фічі — [sdlc/examples/course-lesson-mvp](../sdlc/examples/course-lesson-mvp).

## Module 7 - Execution & Scale

Тема модуля: як specs з Module 6 стають кодом — патерни виконання (Ralph loop, dynamic workflows, автономне/фонове виконання, TDD, feedback loops, brownfield). Running thread — beer-lms (продовження M6 capstone).

| Lecture | Тема | Demo |
|---|---|---|
| 7.2 | Ralph loop — автономний примітив виконання | [7-execution-scale/7.2-ralph-loop](./7-execution-scale/7.2-ralph-loop) |

Демо 7.2 — canonical bash-цикл (реальний `claude -p`) на абстрактній задачі + скрінкаст-сценарії, зокрема прогін на реальному M6 backlog beer-lms у git worktree.

## Module 8 - MCP

Тема модуля: Model Context Protocol від юзера до автора - підключення серверів, екосистема, власний сервер і клієнт, транспорти, advanced-можливості протоколу і безпека MCP.

| Lecture | Тема | Demo |
|---|---|---|
| 8.6-8.8, 8.10 | task-store - перший власний MCP-сервер (tools/resource/prompt, stdio + Streamable HTTP, buggy-варіант для Inspector) | [8-mcp/8.6-first-mcp-server](./8-mcp/8.6-first-mcp-server) |
| 8.9 | mcp-client - власний клієнт: listTools → tool-use loop з Claude API | [8-mcp/8.9-mcp-client](./8-mcp/8.9-mcp-client) |

Демо 8.6 - повноцінний starter: Makefile, тести, навмисно зламаний `server.buggy.ts` для Inspector-дебагу у 8.7 і HTTP-варіант транспорту для 8.8. Мапа демо ↔ лекції ↔ скрінкасти - у [8-mcp/README.md](./8-mcp/README.md).

## Module 9 - Collaboration

Тема модуля: як код виходить за межі однієї сесії у командну роботу - git workflow з агентом, гілки й коміти, звірка діфів, рівні відкату, паралельна робота через worktree.

| Lecture | Тема | Demo |
|---|---|---|
| 9.1 | Git workflow: trunk-based, охайні коміти, чанкування, bisect, відкат, секрет-guard | [9-collaboration/9.1-git-workflow](./9-collaboration/9.1-git-workflow) |
| 9.2 | Git worktrees: паралельні агенти, ізоляція оточення, helper `w`, субагенти, agent-vs-agent | [9-collaboration/9.2-git-worktrees](./9-collaboration/9.2-git-worktrees) |
| 9.3 | Worktree merge + cleanup: порядок merge, конфлікти, paper-cut push + safety-hook, remove/prune | [9-collaboration/9.3-worktree-merge-cleanup](./9-collaboration/9.3-worktree-merge-cleanup) |
| 9.5 | Code review локально в сесії: `/code-review`, `/simplify`, `/security-review`, multi-pass `/codereview`, субагент у чистому контексті | [9-collaboration/9.5-code-review](./9-collaboration/9.5-code-review) |
| 9.6 | Code review на платформі: GitHub App (`@claude` + авто `/code-review`), екосистема рев'юерів (Codex/Copilot/CodeRabbit), спільний `AGENTS.md` | [9-collaboration/9.6-github-platform](./9-collaboration/9.6-github-platform) |
| 9.7 | Реліз і документація з Claude: локальні skills → CI release pipeline, release notes й docs автоматизація | [9-collaboration/9.7-release-docs](./9-collaboration/9.7-release-docs) |

Демо 9.1 - fixture зі своєю seed-історією, що будується в runtime у git-ignored `sandbox/`. Два режими: `make sandbox` (чиста історія + tag `good-baseline` для bisect/відкату/секрет-guard) і `make arm` (змішане дерево для коміту/чанкування/`git add -p`). П'ять `🎬`-скринкастів лекції знімаються на ньому; ANTHROPIC_API_KEY не потрібен.

Демо 9.2 - fixture, що будує детермінований стартовий стан (git + ≥1 commit + локальний `origin` із `main`/`develop` — передумова worktree і база `origin/HEAD`) у git-ignored `sandbox/`. `make sandbox` (чистий репо з `.worktreeinclude`/`.env`/закоміченим helper `w`/субагентом `isolation: worktree`/`render_card`-задачею), `make serve` (env-driven сервіс на `PORT` із `.env` — доводить ізоляцію порту), `make reset` (перебудувати між дублями). Сім `🎬`-скринкастів (inline під слайдами фішок, точні команди) знімаються на ньому; ANTHROPIC_API_KEY для бази не потрібен, живі агент-сесії потребують Claude Code. Merge/cleanup паралельних гілок свідомо НЕ тут — це 9.3.

Демо 9.3 - fixture безпечного фінішу, що будує стартовий стан під merge і cleanup у git-ignored `sandbox/` + worktree-сіблінгах. `make sandbox` піднімає дві worktree-гілки (`worktree-feature-a`/`worktree-bugfix-b`), що правлять той самий рядок `app.py` (тому другий merge дає справжній конфлікт), забутий worktree `worktree-old-experiment` під cleanup, локальний `origin` із `main`, та safety-hook `block-main-push.sh` (`PreToolUse` Bash → `exit 2` на `git push ... main`). `make serve` (той самий env-driven сервіс), `make reset` (перебудувати між дублями). Два `🎬`-скринкасти (вливання двох гілок + конфлікт + paper-cut; cleanup `remove`/`prune`) знімаються на ньому; ANTHROPIC_API_KEY для бази не потрібен, авто-removal на виході веде жива Claude Code сесія. Хуки `WorktreeCreate`/`WorktreeRemove` навмисно не пишемо наперед — це talking-point для не-git VCS і складного провіженінгу.

Демо 9.5 - runnable fixture для **локального** рев'ю в сесії: крихітний Python-task-tracker, у якого `main` — чиста база (тест зелений), а гілка `feat/reminders` несе PR-in-progress із трьома навмисними дефектами — off-by-one (P1, ловить і `make test`), command injection (P0) і дубльований формат-хелпер (P2), кожен під свій інструмент (`/code-review`/`/security-review`/`/simplify`). `make sandbox` будує базу + feature-гілку + локальний bare `origin` (PR без мережі), `make test` червоний на гілці й зелений на `clean-baseline`, `make reset`/`clean` між дублями. `template/.claude/` несе рев'ю як файли проєкту (команди `code-review`/`security-review`/multi-pass `codereview` + субагент-рев'юер з 7.6). Два `🎬`-скринкасти (тур стеку + handoff; `/security-review` глибше). ANTHROPIC_API_KEY не потрібен; `codex` CLI — пререк запису кроку Codex-плагіна.

Демо 9.6 - **не** sandbox, а набір валідних шаблонів конфігів + runbook для рев'ю **на платформі** GitHub (вимагає живого репо зі встановленими App/Codex/Copilot). Файли: `.github/workflows/claude.yml` (mention-режим `@claude` + авто-рев'ю `prompt: /code-review`), спільний `AGENTS.md` із P0/P1/P2 (читають Codex і Copilot), `.github/copilot-instructions.md`, `.coderabbit.yaml` (схема v2), `CLAUDE.md`, і `planted-bug/` із навмисним SQL-injection під PR. Чотири `🎬`-скринкасти (setup + `@claude`; короткий контраст GitLab; екосистема рев'юерів Codex/Copilot на одному PR; безпека `@claude`). Локально перевіряється лише валідність YAML; самі рев'ю записуються на живому репо за runbook.

## Module 10 - Agent Teams

Тема модуля: від одного агента до команд агентів — subagents (вбудовані й кастомні), координація між сесіями, прямий обмін повідомленнями.

| Lecture | Тема | Demo |
|---|---|---|
| 10.1 | Subagents: делегування та ізоляція контексту | [10-agent-teams/10.1-subagents](./10-agent-teams/10.1-subagents) |
| 10.2 | Custom Subagents — авторинг спеціалізованих агентів | [10-agent-teams/10.2-custom-subagents](./10-agent-teams/10.2-custom-subagents) |
| 10.3 | Evals і регресійне тестування агентів — golden-task evals для `.claude/` | [10-agent-teams/10.3-evals-regression](./10-agent-teams/10.3-evals-regression) |
| 10.4 | Agent Teams — команди агентів-пірів | [10-agent-teams/10.4-agent-teams](./10-agent-teams/10.4-agent-teams) |

Демо 10.2 — authoring-фокус: шість авторських subagents (least privilege, model-per-agent, auto-delegation, persistent memory) + fixtures для spawn-restriction і scope-priority. `setup.sh` будує self-contained `sandbox/`.

Демо 10.3 — runnable harness, що ставиться до `.claude/` як до версіонованої конфігурації агента: реальний `claude -p` на golden-задачах + детермінований `check.sh` (exit 0/1) ловить регресії конфігурації. Канонічна структура `tests/agent/cases/<case>/{prompt,setup,check}.sh`; `make check` — CI/pre-commit-шар без токенів.

Демо 10.4 — пісочниця наскрізного прогону Agent Teams: три тіммейти-піри будують фічу «звіт по знижках» на монорепі 10.1. `make sandbox` кладе в пісочницю env-флаг, quality-gate `task-gate.sh` (TaskCompleted, exit 2) і логер хук-подій ще до спавну; `make gate-test` перевіряє обидві гілки гейта без агентів. П'ять `🎬`-епізодів; механіку звірено живим прогоном. Запис лише інтерактивно — headless `claude -p` команду не спавнить.

## Module 11 - Production

Тема модуля: production workflow для агентів, від керованого execution і security testing до design-to-code та зовнішніх інтеграцій.

| Lecture | Тема | Demo |
|---|---|---|
| 11.1 | Безпека агента в проді, attack path і regression test | [11-production/11.1-security-redteam](./11-production/11.1-security-redteam) |
| 11.2 | Від порожньої VPS до deploy `course-project` через self-hosted runner | [11-production/11.2-vps-deploy](./11-production/11.2-vps-deploy) |
| 11.2.1 | Monitoring, observability та AI-черговий поверх готового deploy | [11-production/11.2-agent-on-duty](./11-production/11.2-agent-on-duty) |
| 11.3 | Мінімальні metrics і Docker logs, 20-хвилинний watcher та draft PR від AI-чергового | [11-production/11.3-observability-agent](./11-production/11.3-observability-agent) |
| 11.4 | Дизайн з Claude: від дизайн-системи до першої сторінки | [11-production/11.4-first-page](./11-production/11.4-first-page) |
| 11.5 | Професійний дизайн з Claude: Figma Official, Console і Pencil | [11-production/11.5-figma-pencil](./11-production/11.5-figma-pencil) |
| 11.6 | Claude Code в команді: від пілота до стандарту | — |

Демо 11.2 дає copy-paste kit для реального `course-project`: production Dockerfile,
SQLite volume, health route, GitHub self-hosted runner workflow і repo-native
skill для перевірки deploy-файлів. Поверх готового deploy лягає 11.2.1 із повним
стеком: app metrics, Prometheus, Grafana OSS, логи через Alloy у Loki,
Alertmanager і watcher, який на алерт відкриває draft PR. Демо 11.3 проходить
той самий шлях коротшим маршрутом, лише Prometheus і Grafana плюс Python watcher
над трьома метриками й свіжими error logs. Усі три маршрути мають deterministic
`make verify`.

Демо 11.4 і 11.5 складають design-to-code трек: 11.4 веде від дизайн-системи до
першої сторінки, а 11.5 додає професійний потік через Figma Official, Figma Console
і Pencil з prompts, student workbook і `apply-to-course-project.sh`.

## Convention

- **Demo** це короткий self-contained Python скрипт (1-3 файли) до однієї концепції. Запускається `make run`. Минимум залежностей.
- **Starter** це повний cloneable проект, можна запустити. Має Makefile, Dockerfile, тести, повну Claude Code конфігурацію.
- **Recipe** це короткий self-contained snippet (1-3 файли), копіюєш у свій проект.

`modules/N-topic/README.md` посилається на конкретні demos, starters або recipes у тому ж `modules/N-topic/` каталозі.
