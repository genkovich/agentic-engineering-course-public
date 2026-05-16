---
name: legacy-plan
description: Use when running Step 3 of legacy refactoring protocol — generates PLAN.md for module migration. Two phases — skeleton (3 sections only) and finalize (full plan from green tests). Triggers on '/legacy-plan <module> --phase=skeleton', '/legacy-plan <module> --phase=finalize', or when user asks to 'написати скелет плану', 'дописати план з тестів'.
argument-hint: <module-name> --phase=skeleton|finalize
allowed-tools: Read, Write, Bash
disable-model-invocation: false
---

# legacy-plan — Step 3.1 (skeleton) і 3.3 (finalize)

Один skill з двома фазами. Між ними — `/legacy-tests` (окремий skill). Skeleton має тільки те, що Step 3 знає до тестів. Finalize заповнюється з зелених тестів, не зі здогадок.

## Аргументи

- `<module-name>` — імʼя нового модуля
- `--phase=skeleton` — фаза 3.1 (5-10 хв у Plan mode)
- `--phase=finalize` — фаза 3.3 (після зелених тестів)

## Phase 1: skeleton

### Inputs

- `SPIKE.md` (з Step 1)
- `LEGACY/<module>.md` (з Step 2.1)
- `CRITIC.md` (з Step 2.2)

### Output: PLAN.md з 3 заповненими + 3 порожніми секціями

```markdown
# PLAN — <module-name>

## 1. Чому цей модуль  ✅ (з SPIKE.md)
- module: <module-name>
- критерії: churn=<X>, debt=<Y>, isolation=<Z>, spike verdict=<YES/RISKY>
- скільки часу: <1-2 тижні>

## 2. Що будуємо  ✅
internal/<module-name>/
  ├── domain/      <list of entities + sentinel errors>
  ├── app/         <list of UseCases>
  ├── infra/       <list of Adapters>
  └── ports/       handler.py · dto.py · errors.py

Public interface (без змін, з LEGACY/<module>.md секція 1):
- <signature>
- <signature>

## 3. Що НЕ чіпаємо у цьому циклі  ✅ (з CRITIC.md "невизначені" + LEGACY секція 5)
- <item> — причина: <hypothesis>, окремий цикл
- <item> — причина: <hypothesis>

## 4. Поведінка яку зберігаємо
TBD — заповнюється у --phase=finalize з зелених тестів

## 5. Шматки міграції
TBD — заповнюється у --phase=finalize з блоків параметризованих тестів

## 6. Відкат
TBD — заповнюється у --phase=finalize
```

## Phase 2: finalize

### Inputs

- `PLAN.md` skeleton (з Phase 1)
- `tests/<module>/{contract,characterization,architecture}/` (з `/legacy-tests`)
- Результат `pytest tests/<module>` (має бути зелений)

### Output: PLAN.md повний

Доповнює секції 4-6:

```markdown
## 4. Поведінка яку зберігаємо  ✅ (з зелених тестів)
- 1 параметризований кейс = 1 пункт
- ...

## 5. Шматки міграції  ✅
- [ ] Register · 1 коміт · domain.User + RegisterUseCase + UsersRepo.Insert + EmailSender.SendWelcome
- [ ] VerifyEmail · 1 коміт · ...
- [ ] ResetPassword · 1 коміт · ...

(або інша стратегія chunking — див. лекцію 4.9 секція Step 4)

## 6. Відкат  ✅
- Register cutover зламається → `git revert <hash>` + один рядок у container.py
- VerifyEmail зламається → теж
- ResetPassword зламається → теж
```

## Acceptance criteria

### Skeleton

- 3 заповнені + 3 порожні секції
- Секція 3 («Що не чіпаємо») має ≥2 пункти з причиною
- Секція 2 має повний public interface

### Finalize

- Усі 6 секцій заповнені
- «Поведінка» = 1-в-1 з зелених тестів (кожен parametrize-кейс окремий пункт)
- «Шматки міграції» — checklist `- [ ]` для кожного use case
- pytest зелений перед finalize (skill попереджає, якщо ні)

## Examples

```
/legacy-plan account --phase=skeleton
/legacy-tests account
pytest tests/account/
/legacy-plan account --phase=finalize
```

## Anti-patterns

- **Не заповнюй «Поведінка» зі здогадок** — тільки з зелених тестів. Помилка тут стає silent — рефакторинг проходить, але «зберігає» поведінку, якої немає.
- **Не пропускай skeleton перед тестами** — без скелета тести генеруються «на все», розпухають у 50+ кейсів і втрачають фокус.
- **Не міксуй «Що не чіпаємо» зі справжніми bugs** — bugs у «Що не чіпаємо» з позначкою `known bug, fix after cutover`. Не «правь план щоб виглядав красивіше за тести».
