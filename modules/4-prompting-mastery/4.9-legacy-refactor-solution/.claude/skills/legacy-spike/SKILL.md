---
name: legacy-spike
description: Use when starting Step 1 of legacy refactoring protocol — runs a 2-4 hour feasibility spike for one Bounded Context. Triggers on '/legacy-spike <module>' or when user asks for a feasibility check, BC scope decision, or 'чи злітає переписування цього модуля'.
argument-hint: <module-name> (e.g. account, orders, billing)
allowed-tools: Read, Grep, Glob, Bash
disable-model-invocation: false
---

# legacy-spike — Step 1 feasibility spike

Запускає 2-4-годинну розвідку перед основною роботою. Перевіряє чотири критерії: churn, debt, isolation, feasibility.

## Аргументи

- `<module-name>` (обовʼязково) — імʼя нового модуля у `internal/`. Має бути нейтральним (наприклад `account`, не `users-v2`).

## Inputs

- `git log` за останні 3 місяці у legacy-папках
- Кількість LOC у модулі (через `find` + `wc -l`)
- Імпорти з модуля назовні (через `grep -r "from internal.<old>"`)
- Список public functions модуля (через `grep -E "^def [a-z]"`)

## Output: SPIKE.md (формат)

```markdown
# SPIKE — <module-name>

## 1. Churn (3 місяці)
| File | commits | last touched |
| ---  | ---     | ---          |
| ...  | ...     | ...          |

## 2. Debt indicators
- LOC у legacy: <число>
- # public functions: <число>
- Тестове покриття: <%, через grep на pytest файли>
- TODO/FIXME у модулі: <число>

## 3. Isolation
- Імпортується ззовні: <список модулів які тягнуть legacy>
- Глобальні змінні / singletons: <список>
- Прихована логіка (магічні числа, хардкоди): <короткий список>

## 4. Feasibility verdict
- **Climbs in 1-2 weeks?** YES / NO / RISKY
- Якщо NO/RISKY — який зв'язок заважає, як його розплутати окремим циклом
- Якщо YES — rough Bounded Context boundaries (public interface)

## Rough plan
1. Step 2 — extract <N> файлів через subagents
2. Step 3 — <X> use cases для test plan
3. Step 4 — <Y> chunks (1 use case = 1 коміт за замовчуванням)

## Гіпотези для Step 2 critic
- ...
```

## Acceptance criteria

- SPIKE.md ≤ 2k токенів
- Усі 4 секції присутні
- Verdict (YES/NO/RISKY) присутній
- Якщо verdict = NO — rough plan **відсутній** (це сигнал що Bounded Context невірний, повертайся у пошук іншого модуля)
- Якщо verdict = YES — public interface намічений у форматі `name(args) → result`

## Examples

```
/legacy-spike account
```

→ створює `SPIKE.md` у корені проекту з висновком чи можна переписати users-модуль на account за 1-2 тижні.

## Anti-patterns

- **Не описуй промпт-шляхом «там точно є глобальний кеш»** — main agent не передає здогадки у subagents. Subagents мають знаходити самі.
- **Не запускай spike на 30+ хвилин у одній сесії** — це індикатор що модуль занадто великий. Спайк має бути 2-4 години людського часу для аналізу + 2-3 промпти Claude.
- **Не пиши `users-v2` у rough plan** — нейтральне доменне імʼя у `<module-name>`, інакше тягнеш лабораторні артефакти у прод-код.
