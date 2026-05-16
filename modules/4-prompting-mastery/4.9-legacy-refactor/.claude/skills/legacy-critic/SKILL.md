---
name: legacy-critic
description: Use when running Step 2.2 of legacy refactoring protocol — independent critic subagent verifies LEGACY/<module>.md against random source files, claim-by-claim. Triggers on '/legacy-critic <module>' or when user asks for 'перевірка протиріч', 'critic pass', 'verify legacy summary'.
argument-hint: <module-name>
allowed-tools: Read, Grep, Glob, Bash, Task
disable-model-invocation: false
---

# legacy-critic — Step 2.2 незалежна перевірка протиріч

Перебирає **кожне твердження** у `LEGACY/<module>.md` і перевіряє його проти 2-3 випадково взятих файлів модуля. Повертає список з трьома статусами: підтверджено / спростовано / невизначено.

## Аргументи

- `<module-name>` — імʼя модуля, для якого вже існує `LEGACY/<module>.md`.

## Inputs

- `LEGACY/<module>.md` — артефакт з `/legacy-extract`
- 2-3 випадкових файли з `internal/users/` (отриманих через `ls internal/users/*.py | shuf -n 3`)

## Промпт для critic subagent

```
Read LEGACY/<module>.md та $RANDOM_FILES.

Для КОЖНОГО твердження у LEGACY (включно з пунктами секцій 1, 2, 3):
- Підтверди фактом з файлів (цитата у 1-2 рядки) → confirmed
- Або спростуй (як насправді) → contradicted
- Або не зміг визначити → undetermined

Поверни Markdown:

## Підтверджені (N)
- <claim> · <file>:<line>

## Спростовані (M)
- <claim> · реальність: <як насправді у file:line>

## Невизначені (K)
- <claim> · причина: <чому не вдалося перевірити>

Не аргументуй, лише факти. Не пиши «можливо».
```

## Output: CRITIC.md

Той самий формат, що й вихід critic subagent, з шапкою:

```markdown
# CRITIC — <module-name>

Перевірено файлів: <N>
Дата: <YYYY-MM-DD>

## Підтверджені (N)
...

## Спростовані (M)
...

## Невизначені (K)
...

## Verdict
- M = 0 → переходимо до Step 3 ✅
- M ≥ 1 → доповнюємо `LEGACY/<module>.md`, перезапускаємо `/legacy-extract` для проблемних файлів, потім повторно `/legacy-critic`
```

## Acceptance criteria

- `CRITIC.md` ≤ 2k токенів
- Кожне твердження з `LEGACY/<module>.md` має статус
- Verdict line присутня
- Якщо `M ≥ 1` — skill виводить попередження «Step 2 не закритий, спочатку доповни LEGACY»

## Examples

```
/legacy-critic account
```

→ читає `LEGACY/account.md` + 2-3 файли з `internal/users/`, видає `CRITIC.md` зі списком тверджень.

## Anti-patterns

- **Не пропускай** critic-pass. Без перевірки незалежним subagent кожна прихована залежність може випливти у Step 4 як runtime-помилка.
- **Не дай critic-агенту читати `LEGACY/<module>.md` довше за raw файли** — це індикатор що critic не зайшов у код.
- **Не маркуй «undetermined» як «confirmed»** під тиском часу — undetermined → доводить ще одне коло витягу для проблемних файлів.
