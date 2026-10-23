# Промпти до уроку «Як писати промпти»

Копіюйте промпти звідси, щоб не набирати вручну. Яку теку відкривати для кожного, написано в README.md.

---

## Промпт 1 - Vague vs Explicit refactor

Тека `01-refactor`.

### 1A. Vague

```
Зроби refactor цієї функції parseUser в src/auth/parser.ts
```

### 1B. Explicit

```
Зроби refactor parseUser у src/auth/parser.ts: розділи на validateInput і mapToDomain, збережи поведінку, додай unit-тести для обох у parser.test.ts. Поверни тільки змінений код, без коментарів про те, що ти зробив.
```

---

## Промпт 2 - Few-shot: 1 vs 3 приклади

Тека `02-few-shot` (порожня, просто робоча тека для сесії).

### 2A. Один приклад

```
Перетвори технічні error-коди у повідомлення для UI.

Приклад:
Input: ECONNREFUSED on db:5432
Output: Сервіс тимчасово недоступний. Спробуй за хвилину

Тепер так само:
Input: 401 Unauthorized: Token expired
Output: ?
```

### 2B. Три приклади

```
Перетвори технічні error-коди у повідомлення для UI.

Приклади:
Input: ECONNREFUSED on db:5432
Output: Сервіс тимчасово недоступний. Спробуй за хвилину

Input: 500 Internal Server Error
Output: Щось пішло не так на нашому боці. Ми вже розбираємось — спробуй за пару хвилин або напиши в підтримку якщо терміново.

Input: 422 Validation failed: email format
Output: Неправильний формат email

Тепер так само:
Input: 401 Unauthorized: Token expired
Output: ?
```

---

## Промпт 3 - Race condition: перелік кроків і перевірка

Тека `03-race-condition`. Міркування в тегах не просимо: Claude Code думає перед відповіддю сам, а прохання виписати міркування в тексті відповіді модель може відхилити.

```
Знайди і виправ race condition у counter.go.
Спершу перерахуй усі точки доступу до спільного стану, визнач, де саме
конфлікт, і коротко поясни чому. Потім виправлення.
Публічні методи Counter не змінюй.
Перевір через go run -race counter.go і покажи вивід.
```

---

## Промпт 4 - Verification loop

Тека `04-verification`.

```
У src/api/users.js додай Express handler POST /users.

Вимоги:
- body schema: { email: string, name: string }
- валідація: email мусить містити "@", name не порожній
- 400 з { error: "validation_failed" } якщо невалідно
- 201 з { id: <uuid v4>, email, name } якщо успішно
- використай вбудований crypto.randomUUID() для id

Потім напиши тести у src/api/users.test.js (Vitest + supertest), які покривають:
- 201 happy path
- 400 на порожньому email
- 400 на email без "@"
- 400 на порожньому name

Після того, як напишеш код і тести — запусти npm test src/api/users.test.js і покажи мені вивід. Якщо хоч один тест упав — виправ і запусти ще раз. Зупиняйся тільки коли всі зелені.
```
