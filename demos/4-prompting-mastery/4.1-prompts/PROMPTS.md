# Промпти для скринкастів лекції 4.1

Копіюй з цього файлу під час запису — не друкуй від руки.

---

## Скринкаст 1 — Vague vs Explicit refactor

### 1A. Vague

```
Зроби refactor цієї функції parseUser в src/auth/parser.ts
```

### 1B. Explicit

```
Зроби refactor parseUser у src/auth/parser.ts: розділи на validateInput і mapToDomain, збережи поведінку, додай unit-тести для обох у parser.test.ts. Поверни тільки змінений код, без коментарів про те, що ти зробив.
```

---

## Скринкаст 2 — Few-shot: 1 vs 3 приклади

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

## Скринкаст 3 — Chain of Thought з тегами

```
Прочитай counter.go. У цьому файлі є race condition.

Спочатку напиши свій аналіз у тегу <thinking>...</thinking>:
- перерахуй усі точки, де goroutines звертаються до спільного стану
- визнач, де саме конфлікт
- поясни, чому це race

Потім — конкретне виправлення у тегу <answer>...</answer>: який код змінити і на що.
```

---

## Скринкаст 4 — Verification loop

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
