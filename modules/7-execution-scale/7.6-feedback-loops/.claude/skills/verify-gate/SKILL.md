---
name: verify-gate
description: Implement a story behind a DETERMINISTIC gate — run `tsc --noEmit` + `vitest run`, and do NOT say DONE until both are green, pasting the command output as evidence. Triggers on '/verify-gate <story-id>' (e.g. '/verify-gate story-28'), or 'детермінований гейт', 'доказ перед DONE', 'не кажи готово поки тести червоні'. Reads tasks/<story-id>.md for AC, iterates on the implementation using the failing test output as feedback, refuses completion while red.
argument-hint: <story-id> (e.g. story-28)
allowed-tools: Read, Glob, Edit, Write, Bash(npm test:*), Bash(npx tsc:*), Bash(npm run typecheck:*), Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*)
disable-model-invocation: false
---

# verify-gate — реалізувати story за детермінованим гейтом

Канал зворотного зв'язку #1 лекції 7.6: **детермінований гейт**. Машина дає однозначний
pass/fail, і «готово» вирішує не модель, а зелений набір перевірок. Skill бере story з AC,
реалізує її, **ганяючи гейт на кожній ітерації**, і **не завершує**, поки гейт червоний —
а наприкінці вставляє вивід команди як доказ (evidence-before-assertion).

Канонічна story — **`story-28`** (`sortQueue` review-order): тест `queue-sort.test.ts` ЧЕРВОНИЙ
на старті (test-first), бо функція — стаб. Гейт не дасть «закрити» задачу, поки тест не зелений.

## Гейт (що саме перевіряємо)

```bash
npx tsc --noEmit && npm test
```

`&&` — продовжуй, тільки якщо попереднє пройшло. Перша ж червона перевірка зупиняє ланцюжок.
Це той самий набір, що його ганяє pre-commit hook (`scripts/pre-commit`) і Stop-hook
(`.claude/hooks/verify.sh`) — гейт один, точок входу кілька.

## Кроки

1. **Read** `tasks/<story-id>.md` — витягни AC (Given/When/Then) і Doneness.
2. **Прогнати гейт як baseline:** `npx tsc --noEmit && npm test`. Зафіксуй, що саме червоне
   (який assert, очікував/отримав) — це твій сигнал.
3. **Реалізувати** мінімальну зміну, що закриває червоний assert (для story-28 — `sortQueue` у
   `src/lib/queue.ts`). Пам'ятай пастку: `queue.sort()` мутує вхід → тест чистоти впаде; треба
   `[...queue].sort()`.
4. **Прогнати гейт знову.** Якщо червоний — читай конкретний assert, виправляй, повторюй. **Не
   переходь далі, поки не зелено.**
5. **Доказ перед DONE:** коли гейт зелений — вистав `git status`/`git diff`, встав вивід
   `npm test` (рядок «N passed») прямо у відповідь, тоді `git add -A && git commit`.

## Завершальне правило (вписується явно, не на добру волю моделі)

> Перш ніж сказати DONE: виконай `npx tsc --noEmit && npm test`, переконайся, що ОБИДВА зелені,
> і встав вивід тесту у відповідь. Якщо хоч щось червоне — це НЕ done; читай падіння й виправляй.
> Якщо не можеш перевірити — не відправляй.

## Acceptance criteria цього skill-а

- Гейт (`tsc --noEmit` + `vitest run`) зелений перед будь-яким «готово».
- Вивід команди вставлено у відповідь як доказ (не словесна гарантія).
- Кожна ітерація спирається на конкретний червоний assert, не на здогад.

## Anti-patterns

- **Не кажи DONE без вставленого виводу** — це найдешевший сигнал нечесності.
- **Не «підганяй тест під код»** — якщо впав assert порядку/чистоти, виправляй `sortQueue`, а не тест
  (тест описує намір зі story, не поточну поведінку стабу).
- **Не вимикай і не `.skip` червоний тест**, щоб «пройшов» гейт — це і є обхід дисципліни.
- **Не коміть червоне** «щоб не загубити» — гейт існує саме щоб цього не сталося.
