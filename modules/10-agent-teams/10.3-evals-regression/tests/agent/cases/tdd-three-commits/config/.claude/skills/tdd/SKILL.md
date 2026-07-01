---
name: tdd
description: Провести задачу через RED → GREEN → REFACTOR з рівно 3 атомарними комітами (test/feat/refactor) на стеку node:test. Порт оркестратора 7.7. Tests — незмінний контракт після RED.
allowed-tools: Read, Glob, Edit, Write, Bash(node:*), Bash(git add:*), Bash(git commit:*), Bash(git log:*), Bash(git diff:*)
---

# /tdd — RED → GREEN → REFACTOR за 3 коміти (node:test)

Порт TDD-оркестратора 7.7 на вбудований `node --test`. Дисципліна: тести пишуться
ПЕРШИМИ, лишаються незмінними після RED, і кожна фаза — окремий атомарний коміт.

## Прочитай AC

`tasks/story.md` — Given/When/Then і Definition of Done.

## Фаза RED — спочатку тест

1. Напиши `test/slug.test.js` (вбудований `node:test` + `node:assert`) під усі AC.
2. Прожени `node --test` — має бути ЧЕРВОНО (стаб кидає `not implemented`).
3. Коміт: `git add -A && git commit -m "test(slug): add failing tests for slugify"`.

## Фаза GREEN — мінімальна реалізація

1. Реалізуй `slugify` у `src/slug.js`, доки `node --test` не позеленіє.
2. **НЕ редагуй `test/`** — тести вже зафіксували намір.
3. Коміт: `git add -A && git commit -m "feat(slug): implement slugify"`.

## Фаза REFACTOR — чистка без зміни поведінки

1. Прибери дублювання/магічні значення; `node --test` лишається зеленим.
2. **`test/` не чіпай.**
3. Коміт: `git add -A && git commit -m "refactor(slug): tidy slugify"`.

## Інваріанти (їх перевіряє eval)

- Рівно 3 коміти: `test(` → `feat(` → `refactor(` у цьому порядку.
- `git diff` по `test/` між RED і HEAD — порожній.
- `node --test` зелений на HEAD.
