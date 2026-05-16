# Module 5 — Claude Code extended

Розширення базового Claude Code: custom commands, agent skills, hooks, plugins, team marketplace, SDK orchestration. Цей модуль про те, як перетворити агента із розумного бекенду у спеціалізованого члена команди для свого проєкту.

## Лекції модуля

- 5.1 Custom Commands — чому `.claude/commands/` це стартова точка кастомізації
- 5.2 Agent Skills — як працюють skills і чим відрізняються від commands
- 5.3 Створення власних Skills — SKILL.md, frontmatter, scripts, eval loop
- 5.4 Hooks — автоматизація на рівні lifecycle подій
- 5.5 Plugins: встановлення і створення — локальні і shared плагіни
- 5.6 Створення marketplace для команди — як шерити налаштування у команді
- 5.7 Claude Agent SDK + capstone wrap — орхестрація і capstone-плагін

## Артефакти модуля

| Demo | Що показує | ДЗ лекції |
|---|---|---|
| [pdf-form-filler](../../demos/5-claude-code-extended/5.2-skills-intro/pdf-form-filler) | Production-ready skill для заповнення PDF AcroForm: bundled scripts, error catalog, output template — клонуй і прогон `make demo` | 5.2 |
| [audit-api-endpoint](../../demos/5-claude-code-extended/5.3-skills-creation/audit-api-endpoint) | Один наскрізний skill: повний frontmatter, bundled PEP 723 script, bad/good приклади дизайну скриптів для агента, gotchas, template, validation loop | 5.3 |
| [hooks-toolkit](../../demos/5-claude-code-extended/5.4-hooks) | 13 hooks. Для ДЗ 5.4 — почни з 4 production recipes (`recipe-1-auto-format.sh`, `recipe-2-protect-files.sh`, `recipe-3-secrets-scan.py`, `recipe-4-session-context.sh`); решта (observability, MCP allowlist) — для досвідних. | 5.4 |
| [plugins](../../demos/5-claude-code-extended/5.5-plugins) | 3 sub-demos: `before/` (standalone .claude/), `after/` (universal hello-plugin), `red-flag/` (intentionally bad plugin для trust audit) | 5.5 |
| [sdk-cli](../../demos/5-claude-code-extended/5.7-sdk/sdk-cli) | Release-notes orchestration через `claude -p` subprocess з dual auth (OAuth + env var) і Haiku model pinning | 5.7 |

## Як працює clone-and-run

Кожен demo — окрема директорія з:
- `Makefile` — `make demo` запускає end-to-end
- `README.md` — інструкції, gotchas, troubleshooting
- `.claude/skills/<name>/SKILL.md` — skill body з frontmatter

Структура `.claude/skills/` всередині demo означає що ти можеш склонувати demo як окремий проєкт і запустити Claude Code там — без впливу на свій основний `~/.claude/`.

```bash
# Приклад для 5.3
cd demos/5-claude-code-extended/5.3-skills-creation/audit-api-endpoint
make demo                                # прогнати end-to-end
make audit ENDPOINT=/ TARGET=...         # на свій таргет
```

## Pre-requisites

- Claude Code встановлений (див. Module 3 starters)
- [uv](https://docs.astral.sh/uv/) для self-contained Python скриптів у skills
- Один зі starter-проєктів Module 3 у `../../starters/`
- ANTHROPIC_API_KEY у `.env` (або OAuth через `claude auth login`)

## Що робити після цього модуля

Module 5 — останній перед capstone (Module 11). Усі шматки, які ти зібрав тут (commands, skills, hooks, plugins), у 5.7 збираються через Claude Agent SDK orchestration і ляжуть в основу твого capstone-плагіну у Module 11.

ДЗ модуля 5:
- 5.2 — clone `pdf-form-filler`, прогнати `make demo`, observe SKILL.md structure.
- 5.3 — adapt `audit-api-endpoint` під свій endpoint (свій бекенд або pet-проект).
- 5.4 — extend один з 4 production recipes своїм правилом (наприклад, додати custom file path до `recipe-2-protect-files`).
- 5.5 — modify один з 3 plugin sub-demos (наприклад, додати command до `after/hello-plugin`).
- 5.7 — adapt `sdk-cli/release-notes.sh` для свого release-notes pipeline.
