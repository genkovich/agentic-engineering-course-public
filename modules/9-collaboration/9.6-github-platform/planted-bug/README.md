# Planted-bug PR fixture

Короткий файл із одним навмисним дефектом, щоб лектор відкрив на ньому PR і
подивився, як Claude / Codex / Copilot його ловлять на платформі GitHub.

## Дефект

`src/lookup.py` → `find_user`: **SQL injection**. Параметр `email` —
недовірений ввід — конкатенується прямо в SQL-рядок. Ввід `' OR '1'='1`
поверне всі рядки; підготовлений payload може дропнути таблицю.

Очікуваний фікс від рев'юерів — параметризований запит:

```python
cur.execute("SELECT id, email FROM users WHERE email = ?", (email,))
```

## Як інсценувати PR (лектор)

1. У робочому GitHub-репо (з установленими App/Codex/Copilot) створи гілку:
   `git checkout -b feat/user-lookup`.
2. Додай `src/lookup.py` із цього каталогу, закоміть, запуш, відкрий PR.
3. Спостерігай рев'ю від кожного рушія (див. `../screencast-prompts.md`).

Це **fixture**, не частина runnable-демо: GitHub-інтеграція вимагає живого
репо й установлених застосунків, тому 9.6 — шаблони конфігів + runbook, а не
`make sandbox`.
