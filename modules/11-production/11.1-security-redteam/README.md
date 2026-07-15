# Lecture 11.1 — GitHub issue-worker security demo

У цьому демо немає локального worker-а, cron, веб-сервера чи копії GitHub.
Усе, що бачить аудиторія, відбувається в реальному репозиторії
[`genkovich/course-project`](https://github.com/genkovich/course-project).

## Що ми показуємо

Є два сценарії:

1. Безпечний issue проходить через агента й закінчується draft PR.
2. Issue з прихованою інструкцією зупиняється до запуску агента.

Що було б без захисту, показуємо Mermaid-схемою на слайді. Реальний витік
секрету з GitHub Actions не виконуємо.

## Де працює worker

- Workflow: [issue-worker](https://github.com/genkovich/course-project/actions/workflows/issue-worker.yml).
- Код у репозиторії: `.github/workflows/issue-worker.yml`.
- Правила агента: `.claude/agents/issue-worker.md`.
- Шкідливий issue: [#11](https://github.com/genkovich/course-project/issues/11).
- Готовий blocked run: [29204148920](https://github.com/genkovich/course-project/actions/runs/29204148920).

## Що захищаємо

| Актив | Захист |
|---|---|
| OAuth token Claude | issue перевіряється до запуску моделі; агент не має мережевих команд |
| GitHub token | агент не виконує `gh`, commit або push |
| `.github/` і `.claude/` | workflow відхиляє зміну захищених файлів |
| `main` | агент може підготувати лише draft PR |

## Підготовка один раз

Потрібні GitHub CLI і робоча авторизація:

```bash
gh auth status
claude auth status
```

Для безпечного сценарію онови OAuth token поза записом:

```bash
claude setup-token
pbpaste | gh secret set CLAUDE_CODE_OAUTH_TOKEN \
  --repo genkovich/course-project
printf '' | pbcopy
```

## Демонстрація 1 — шкідливий issue

```bash
cd ~/sources/agentic-engineering-course/modules/11-production/11.1-security-redteam
make agent-block-demo
```

Команда:

1. повертає issue #11 у `agent-ready`;
2. запускає реальний GitHub Actions workflow;
3. чекає завершення run.

Якщо запустити тільки `make agent-run` без issue з `agent-ready`, workflow
завершиться після перевірки порожньої черги. Claude в такому запуску не стартує.

У GitHub покажи:

- `agent-blocked` на issue #11;
- коментар від `github-actions`;
- у run зелений лише `Find and reserve one issue`;
- checkout, Claude і створення PR пропущені;
- прив'язаного PR немає.

## Демонстрація 2 — безпечний issue

```bash
make agent-create-issue
make agent-run
```

Перша команда надрукує URL нового issue. Відкрий його й покажи `agent-ready`.
Під час другого запуску label зміниться на `agent-in-progress`. Після успіху в
issue з'являться `agent-pr-open` і коментар із draft PR.

`make agent-run` не запускає модель на комп'ютері. Він виконує
`gh workflow run`, а потім `gh run watch`. Сам агент працює на GitHub runner.

У PR покажи:

- статус `Draft`;
- вкладку `Files changed`;
- `Closes #номер-issue`;
- результати перевірок.

## Що означають labels

| Label | Стан |
|---|---|
| `agent-ready` | задача чекає worker-а |
| `agent-in-progress` | worker уже забрав задачу |
| `agent-pr-open` | draft PR створено |
| `agent-blocked` | небезпечний вхід зупинено до моделі |
| `agent-failed` | агент або перевірки впали; дивись Actions log |

## Файли матеріалів

| Файл | Що в ньому |
|---|---|
| `production-agent/github/issue-worker.yml` | копія production workflow для пояснення |
| `production-agent/.claude/agents/issue-worker.md` | правила агента |
| `production-agent/demo-issue.md` | тіло безпечного issue |
| `production-agent/agent-flow.md` | схема циклу |
| `screencast-prompts.md` | точний маршрут запису |

## Перевірка матеріалів

```bash
make verify
```

Команда перевіряє лише локальні файли матеріалів. Вона не запускає агента й не
змінює GitHub. Для живого запуску є окремі `make agent-run` і
`make agent-block-demo`.
