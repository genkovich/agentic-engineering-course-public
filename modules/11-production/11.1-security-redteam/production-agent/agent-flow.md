# Цикл GitHub issue-worker

```mermaid
flowchart TD
    A[GitHub Actions запускає worker] --> B{Є open issue<br/>з agent-ready?}
    B -->|Ні| Z[Завершити запуск]
    B -->|Так| T{Вхід містить<br/>небезпечну інструкцію?}
    T -->|Так| X[Додати agent-blocked<br/>агента не запускати]
    T -->|Ні| C[Прибрати agent-ready<br/>додати agent-in-progress]
    C --> D[Агент готує зміну<br/>в новій гілці]
    D --> E{Перевірки пройшли?}
    E -->|Ні| F[Додати agent-failed]
    E -->|Так| G[Створити draft PR<br/>з Closes issue]
    G --> H[Додати посилання в issue<br/>поставити agent-pr-open]
    H --> A
```

Ключові моменти:

- шкідливий issue зупиняється до checkout і запуску моделі;
- для безпечного issue worker одразу прибирає `agent-ready`, тому наступний
  запуск не може взяти ту саму задачу повторно.
