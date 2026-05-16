# analytics-server

Mock receiver для observability hooks (slide 8). Stdlib-only HTTP server. Друкує кожен POST у термінал як pretty JSON.

## Запуск

```bash
python3 server.py
# або:
uv run server.py
# слухає на http://127.0.0.1:8090/events
```

Або через Make:

```bash
make analytics
```

## Перевірка

```bash
echo '{"ts":"2026-05-07T10:00:00Z","tool":"Edit","ok":true}' \
  | curl -fsS -X POST http://127.0.0.1:8090/events \
      -H 'Content-Type: application/json' --data @-
```

У вікні сервера зʼявиться pretty JSON.

## Як це використовує `analytics-send.sh`

```
PostToolUse → analytics-send.sh
  ↓ stdin (hook payload)
secrets-strip.py
  ↓ sanitized JSON
curl -X POST $ANALYTICS_URL  (default → http://localhost:8090/events)
```

Фейл сервера → `analytics-send.sh` мовчки помирає (`|| true`), Claude нічого не помічає. Це навмисно: telemetry не повинна валити основний workflow (slide 9).
