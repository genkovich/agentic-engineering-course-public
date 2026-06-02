---
name: code-reviewer-subagent
description: Spin up a clean-context subagent reviewer that sees ONLY the git diff plus a story's AC, and returns a discrete ACCEPT/WARN/PARTIAL/REJECT verdict with rationale. Triggers on '/code-review-subagent <story-id>' (e.g. '/code-review-subagent story-27'). NOT the built-in '/code-review'. Use when the user asks to 'дай рев'юера в чистому контексті', 'субагент має оцінити diff проти AC', 'review this diff with fresh eyes'.
argument-hint: <story-id> (e.g. story-27)
allowed-tools: Read, Glob, Bash, Task
disable-model-invocation: false
---

# code-reviewer-subagent — рев'юер у чистому контексті

Канал зворотного зв'язку #3 для лекції 7.6: баг, який не видно ні юніт-тестом
(`saveQueue` сама по собі коректна), ні скриншотом (до reload усе виглядає правильно).
Ловить його рев'юер, що дивиться на `git diff` + AC і помічає, що збереження ніде
не викликається.

Ключова ідея — **чистий контекст**: субагент НЕ бачить ні нашого діалогу, ні решти
кодбази, тільки `git diff` і AC story. Це усуває упередження «я ж щойно це писав» і
дає чесний, відтворюваний вердикт. Не плутати з вбудованим `/code-review` — тут ми
явно піднімаємо ізольований субагент через `Task`.

Канонічна story — `story-27` (localStorage-регресія): перший прогін → REJECT,
після фіксу → ACCEPT.

## Аргументи

- `<story-id>` — story з полем `channel: code-reviewer-subagent` (напр. `story-27`).

## Кроки

1. **Read** `tasks/<story-id>.md` → витягнути AC (Given/When/Then) і Doneness.
2. `Bash`: зібрати diff — `git diff` (або `git diff HEAD` / staged), обмежити
   релевантними файлами (для story-27: `src/App.tsx`, `src/lib/storage.ts`).
3. `Task`: підняти субагент із **чистим контекстом**. У промпт кладемо РІВНО дві речі:
   - повний текст AC story;
   - текст diff.
   Жодного іншого контексту проєкту субагенту не даємо.
4. Субагент повертає один із чотирьох вердиктів і обґрунтування:
   - **ACCEPT** — diff виконує всі AC.
   - **WARN** — виконує, але є зауваження (стиль, дрібний ризик).
   - **PARTIAL** — частина AC виконана, частина ні.
   - **REJECT** — ключова AC не виконана.

## Output

```
story-27 · code-reviewer-subagent
  Вердикт: REJECT
  Обґрунтування:
    - AC-1/AC-2 вимагають, щоб стан переживав reload через localStorage.
    - У diff App.tsx читає loadQueue() при старті, але saveQueue НІДЕ не
      викликається — useEffect порожній. Тож збереження не відбувається.
    - Reload скине стан на сід → AC-1 не виконується.
  Що зробити: викликати saveQueue(queue) в ефекті при зміні queue.
```

Після фіксу — повторний прогін має дати `Вердикт: ACCEPT`.

## Acceptance criteria

- Субагент бачить ТІЛЬКИ diff + AC (чистий контекст, без іншого).
- Вердикт — рівно один із ACCEPT / WARN / PARTIAL / REJECT.
- Обґрунтування прив'язане до конкретних AC, не загальні слова.

## Anti-patterns

- **Не годуй субагенту весь репозиторій** — суть у вузькому, неупередженому контексті.
- **Не повертай розмитих «ну майже»** — вердикт дискретний.
- **Не плутай із вбудованим `/code-review`** — тут явний ізольований субагент через `Task`.
