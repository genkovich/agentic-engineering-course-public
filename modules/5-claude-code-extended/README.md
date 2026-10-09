# Module 5 - Claude Code extended

Розширення базового Claude Code: custom commands, agent skills, hooks, plugins, team marketplace, SDK orchestration. Цей модуль про те, як перетворити агента із розумного бекенду у спеціалізованого члена команди для свого проєкту.

Артефакти модуля впорядковані за LMS-нумерацією: `modules/5-claude-code-extended/5.N-<topic>/`.

## Лекції модуля

- 5.1 Custom Commands - чому `.claude/commands/` це стартова точка кастомізації
- 5.2 Agent Skills - як працюють skills і чим відрізняються від commands
- 5.3 Створення власних Skills - SKILL.md, frontmatter, scripts, eval loop
- 5.4 Hooks - автоматизація на рівні lifecycle подій
- 5.5 Plugins: встановлення і створення - локальні і shared плагіни
- 5.6 Створення marketplace для команди - як шерити налаштування у команді
- 5.7 Claude Agent SDK + capstone wrap - орхестрація і capstone-плагін

## Артефакти модуля

| Demo | Що показує | Лекції |
|---|---|---|
| [pdf-form-filler](./5.2-skills-intro/pdf-form-filler) | Production-ready skill для заповнення PDF AcroForm: bundled scripts, error catalog, output template — приклад skill як завершений артефакт | 5.2 |
| [audit-api-endpoint](./5.3-skills-creation/audit-api-endpoint) | Один наскрізний skill: повний frontmatter, bundled PEP 723 script, bad/good приклади дизайну скриптів для агента, gotchas, template, checklist, validation loop, plan-validate-execute | 5.3 |
| [audit-pytest-file](./5.3-skills-creation/audit-pytest-file) | Паралельний skill (pytest output audit) — другий worked example skill-creation протоколу на іншому домені | 5.3 |
| [hooks-toolkit](./5.4-hooks) | 13 hooks: 4 production recipes (auto-format, file-protection, secrets-scan, session-context) + observability (tool-trace, subagent lifecycle, prompt transcript) + notifications + MCP allowlist | 5.4 |
| [plugins](./5.5-plugins) | Plugin walkthrough: `before/` (standalone .claude/), `after/` (універсальний hello-plugin з усіма 4 компонентами), `red-flag/` (intentionally bad для trust audit) | 5.5 |
| [team-marketplace](./5.6-marketplace) | Team plugin distribution: full marketplace repo з 3 опублікованими плагінами, GitHub Actions, SECURITY policy, release-notes pipeline | 5.6 |
| [sdk-cli + sdk-python](./5.7-sdk) | Release-notes orchestration: `claude -p` subprocess (sdk-cli) + claude-agent-sdk Python orchestration (sdk-python) — обидва з dual auth і Haiku model pinning | 5.7 |


## Pre-requisites

- Claude Code локально (див. Module 3)
- [uv](https://docs.astral.sh/uv/) для self-contained Python скриптів у skills
- Один зі starter-проєктів Module 3 (демо 5.3 цілиться у `modules/3-claude-code-setup/3.9-starters/go-chi/`)

## Як використовувати

Кожен demo - окрема директорія із власним `Makefile`, `README.md` і `.claude/skills/<name>/SKILL.md`. Структура `.claude/skills/` всередині demo дозволяє склонувати demo як локальний проєкт і запустити Claude Code там, не торкаючись свого основного `~/.claude/`.

```bash
cd modules/5-claude-code-extended/5.3-skills-creation/audit-api-endpoint
make demo                                # прогнати end-to-end
make audit ENDPOINT=/ TARGET=...         # на свій таргет
```

## Що робити після цього модуля

Module 5 - останній перед capstone (Module 11). Усі шматки, які ти зібрав тут (commands, skills, hooks, plugins, marketplace), у 5.7 збираються через Claude Agent SDK orchestration і ляжуть в основу твого capstone-плагіну у Module 11.
