# Сценарій запису лекції 11.1

У записі використовуємо тільки слайди, GitHub і короткі команди `gh`/`make`.
Локального веб-сервера немає.

## До запису

```bash
cd ~/sources/agentic-engineering-course/modules/11-production/11.1-security-redteam
gh auth status
make verify
```

Онови OAuth token Claude поза кадром:

```bash
claude setup-token
pbpaste | gh secret set CLAUDE_CODE_OAUTH_TOKEN \
  --repo genkovich/course-project
printf '' | pbcopy
```

Відкрий вкладки:

1. [course-project](https://github.com/genkovich/course-project).
2. [issue #11](https://github.com/genkovich/course-project/issues/11).
3. [issue-worker Actions](https://github.com/genkovich/course-project/actions/workflows/issue-worker.yml).
4. [готовий blocked run](https://github.com/genkovich/course-project/actions/runs/29204148920).

## Демонстрація 1 — небезпечний issue

### Екран 1: Slide 2

Покажи чотири активи: Claude token, GitHub token, правила worker-а та `main`.

Скажи:

«Ми не захищаємо абстрактного агента. Ми не даємо тексту issue дістатися до
секретів, переписати workflow або самостійно змінити main».

### Екран 2: Slide 4

Покажи червону схему:

`прихована інструкція → модель → інструмент → секрет або workflow → наслідок`.

Поясни, що цей шлях не запускаємо зі справжніми secrets. Це гіпотеза атаки.

### Екран 3: GitHub issue #11

Через `… → Edit` покажи прихований HTML-коментар. Вийди через `Cancel`.

### Екран 4: термінал

```bash
make agent-block-demo
```

Відкрий URL Actions run, який надрукує команда.

Скажи: «Make тут нічого не запускає локально. Він через GitHub CLI створює run
у Actions і показує його стан у терміналі».

### Екран 5: GitHub Actions

Покажи:

- `Find and reserve one issue` — success;
- checkout — skipped;
- install Claude — skipped;
- implement — skipped;
- create PR — skipped.

### Екран 6: GitHub issue #11

Покажи `agent-blocked`, коментар від `github-actions` і відсутність PR.

Скажи:

«Це не модель вирішила поводитися добре. Модель узагалі не запускалася».

## Демонстрація 2 — звичайна задача

### Екран 1: термінал

```bash
make agent-create-issue
```

Відкрий URL, який надрукувала команда.

### Екран 2: новий GitHub issue

Покажи `agent-ready`, один очікуваний файл і критерії приймання.

### Екран 3: термінал

```bash
make agent-run
```

Відкрий надрукований Actions URL.

### Екран 4: GitHub issue та Actions

Під час роботи покажи `agent-in-progress` і крок `Implement the issue`.

### Екран 5: draft PR

Після завершення відкрий PR із коментаря в issue. Покажи:

- `agent-pr-open`;
- статус `Draft`;
- `Files changed`;
- `Closes #issue`;
- checks.

Скажи:

«Агент підготував зміну, але не злив її. Фінальне рішення залишилося за
людиною».

## Фінальний слайд

Покажи два регресійні сценарії:

- безпечний issue → draft PR;
- шкідливий issue → `agent-blocked`, агент не запущений, PR немає.
