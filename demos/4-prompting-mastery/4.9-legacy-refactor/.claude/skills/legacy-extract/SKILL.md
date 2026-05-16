---
name: legacy-extract
description: Use when running Step 2 of legacy refactoring protocol — extracts a 6-section summary of a legacy module via parallel subagents per file. Triggers on '/legacy-extract <module>' or when user asks to 'витягти legacy', 'extract legacy module', 'дослідити старий код через subagents'.
argument-hint: <module-name> (e.g. account)
allowed-tools: Read, Grep, Glob, Bash, Task
disable-model-invocation: false
---

# legacy-extract — Step 2.1 витяг через subagents per-file

Один subagent на один великий файл, кожен повертає 6-секційне резюме на ≤2k токенів. Main agent агрегує результати у `LEGACY/<module>.md`.

## Аргументи

- `<module-name>` — імʼя нового модуля (наприклад `account`). Файли беруться з `internal/users/` (legacy) або з шляху, описаного у SPIKE.md.

## Стратегії розподілу subagents (для спагетті)

Перш ніж запускати subagents, обери стратегію за шириною/щільністю модуля:

1. **Entry-points map** (default для невеликих модулів):
   `grep -E "^def [a-z]" internal/users/*.py` → один subagent на одну entry-функцію + її pull-через-call граф.
2. **Subagent-per-usecase**: якщо модуль має чіткі use cases (`register`, `verify`, `reset`) — один subagent на use case, незалежно від кількості файлів.
3. **Dependency-graph SCC**: для дуже спагеттіного модуля з циклічними імпортами — побудуй call graph, знайди Strongly Connected Components, один subagent на SCC.

Стратегію зафіксуй у першому рядку `LEGACY/<module>.md`: «Стратегія: entry-points / per-usecase / dependency-SCC».

## Промпт для кожного subagent (фіксований шаблон)

```
Read $FILE_PATH в ізольованій сесії. Поверни Markdown з шістьма секціями:

1. Що файл робить назовні — public methods, exports
2. Залежності — imports, calls до інших модулів і external services
3. Сховані звʼязки — globals, dynamic calls, reflection, cache pollution
4. 5-10 прикладів вхід → вихід через public methods
5. Підозріле — гіпотези «чому тут зроблено так дивно» (≥2 hypotheses!)
6. Що треба для тестів — mocks, fixtures, env

Обмеження: ≤2k токенів, без фрагментів коду довших за 5 рядків.
```

## Output: LEGACY/<module>.md

```markdown
# LEGACY/<module>.md

Стратегія розподілу: <entry-points|per-usecase|dependency-SCC>

## 1. Що модуль робить назовні
- ...

## 2. Залежності
- зовнішні: ...
- внутрішні: ...

## 3. Сховані звʼязки
- ...

## 4. Приклади вхід → вихід
1. ...
2. ...

## 5. Підозріле (гіпотези)
- ...
- ...

## 6. Що треба для тестів
- ...
```

## Acceptance criteria (skill валідовує перед записом)

- `LEGACY/<module>.md` ≤ 3k токенів (агрегат усіх subagent виходів)
- Усі 6 секцій присутні і непорожні
- Секція 5 має ≥2 гіпотези
- Секція 4 має 5-10 приклад-кейсів
- Активна сесія main agent НЕ містить сирого коду з `internal/users/*.py` — тільки subagent summaries

## Examples

```
/legacy-extract account
```

→ запускає 4 паралельні subagents (per-file для users-модуля), агрегує їхні виходи у `LEGACY/account.md` за 3-5 хв.

## Anti-patterns

- **Не запускай послідовно** — subagents працюють паралельно через Task tool, інакше витрачається 4× часу на дослідження.
- **Не передавай у промпт subagent деталі що тобі вже здається** («там точно є кеш») — це bias, subagent поверне підтвердження, не аналіз.
- **Не дозволяй subagent повертати >2k токенів** — обріж промпт жорстким лімітом, інакше main agent розпухає.
