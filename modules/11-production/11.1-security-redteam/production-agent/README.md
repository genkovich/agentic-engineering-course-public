# Реальний GitHub issue-worker

Worker працює в
[`genkovich/course-project`](https://github.com/genkovich/course-project), а не
на ноутбуці викладача.

## Два результати

```text
безпечний issue  → agent-in-progress → draft PR → agent-pr-open
шкідливий issue → agent-blocked → агент не запущений → PR немає
```

## Реальні посилання

- Workflow: [issue-worker](https://github.com/genkovich/course-project/actions/workflows/issue-worker.yml).
- Шкідливий issue: [#11](https://github.com/genkovich/course-project/issues/11).
- Blocked run: [29204148920](https://github.com/genkovich/course-project/actions/runs/29204148920).
- Workflow був доданий через merged [PR #14](https://github.com/genkovich/course-project/pull/14).

## Файли

| Файл | Для чого |
|---|---|
| `github/issue-worker.yml` | черга, перевірка входу, запуск агента, checks і draft PR |
| `.claude/agents/issue-worker.md` | правила та межі агента |
| `demo-issue.md` | безпечна задача для живого запуску |
| `agent-flow.md` | схема для слайда |

## Запуск шкідливого сценарію

```bash
make agent-block-demo
```

Очікувано: issue #11 отримує `agent-blocked`, а checkout, Claude і PR steps у
GitHub Actions пропускаються.

## Запуск безпечного сценарію

```bash
make agent-create-issue
make agent-run
```

Очікувано: новий issue проходить `agent-ready → agent-in-progress →
agent-pr-open` і отримує посилання на draft PR.

Для безпечного сценарію repository secret `CLAUDE_CODE_OAUTH_TOKEN` має бути
чинним. Значення secret у матеріалах не зберігається.
