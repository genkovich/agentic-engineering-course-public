# Module 10 — Agent Teams

Тема модуля: від одного агента до **команд агентів** — subagents (вбудовані й кастомні),
координація між кількома сесіями Claude Code, прямий обмін повідомленнями. Цей корінь
заводиться першим demo Module 10 — golden-task evals для кастомних subagents.

| Lecture | Тема | Demo |
|---|---|---|
| 10.1 | Subagents — делегування та ізоляція контексту | [10.1-subagents](./10.1-subagents) |
| 10.2 | Custom Subagents — авторинг спеціалізованих агентів | [10.2-custom-subagents](./10.2-custom-subagents) |
| 10.3 | Evals і регресійне тестування агентів — golden-task evals для `.claude/` | [10.3-evals-regression](./10.3-evals-regression) |
| 10.4 | Agent Teams — команди агентів-пірів | [10.4-agent-teams](./10.4-agent-teams) |

Demo 10.1 — runnable монореп із чотирма незалежними пошуковими поверхнями (billing з ризиком
округлення й знижок, queue з тонким багом дубль-requeue, auth із трьох файлів під fan-out,
reports із навмисно flaky-тестом) + read-only `ro-reviewer`. `make sandbox` будує чисту
git-пісочницю з seed-історією (`Co-Authored-By: Claude`), `node --test` показує зелені пакети й
flaky; на ньому знімаються всі чотири `🎬`-скринкасти лекції (fan-out / orchestrator-worker /
voting / контракт результату). Чистий node, без npm.

Demo 10.2 — authoring-фокус (на противагу 10.3, куди перенесено golden-task harness): шість
авторських subagents (`safe-researcher`/`file-writer` для least privilege, `bug-hunter` для
model-per-agent, `code-explainer-vague`/`code-explainer-proactive` для auto-delegation,
`memory-keeper` для persistent memory) + fixtures для spawn-restriction (два незалежні механізми)
і scope-priority (project vs user). `setup.sh` будує self-contained `sandbox/`; шість
`🎬`-сценаріїв у `screencast-prompts.md`.

Demo 10.3 — runnable harness, що ставиться до `.claude/` як до **версіонованої конфігурації
агента** і захищає її **малим golden-task регресійним сьютом + детермінованими чекерами**:
реальний `claude -p` на golden-задачах, `check.sh` (exit 0/1) ловить регресії конфігурації.
Канонічна структура `tests/agent/cases/<case>/{prompt,setup,check}.sh` + детермінований
`make check` без токенів (CI/pre-commit-шар).

Demo 10.4 — пісочниця **одного наскрізного прогону** лекції 10.4: команда з трьох
тіммейтів-пірів (billing-owner / queue-owner / reports-owner) будує фічу «звіт по знижках»
на монорепі 10.1. `make sandbox` = ті самі 5 seed-комітів + 6-й team-prep коміт (env-флаг
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, quality-gate `task-gate.sh` на `TaskCompleted`,
логер `task-log.sh`, стабілізований reports-тест — flaky з 10.1 мигав би гейтом);
`make gate-test` ізольовано перевіряє обидві гілки хука. П'ять `🎬`-епізодів у
`screencast-prompts.md`. Механіку звірено живим прогоном (v2.1.201): peer-повідомлення,
хук-блок з фідбеком, «команда вмирає — список задач лишається». Запис лише інтерактивно:
headless `claude -p` команду не спавнить.

## Convention

Слуги — `N-topic` (`10-agent-teams`) + `N.M-subtopic` (`10.3-evals-regression`), як в інших
модулях. Demo має `README.md`, `Makefile`, `screencast-prompts.md` і самодостатній harness.
`modules/README.md` (корінь) — загальна Module → Artifacts мапа.
