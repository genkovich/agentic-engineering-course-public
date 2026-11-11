# Demo: Стохастичність (Temperature)

**Module:** 1 - LLM Mechanics
**Lectures:** 1.4

## Що показує

Один і той самий промпт через Anthropic API з трьома значеннями temperature (0.0, 0.5, 1.0), кожне по 3 запуски. Видно три речі:

1. При **temperature=0.0** результат майже стабільний між запусками (модель завжди бере найвірогідніший токен).
2. При **temperature=1.0** виходи різні (модель семплить з повного розподілу).
3. **Промпт як "ручка temperature"**: дуже специфічний промпт з форматом дає стабільний вихід навіть при T=1.0. Це важливо тому що у Claude.ai і Claude Code немає прямого доступу до temperature, але через формулювання промпту можна досягти потрібної детермінованості.

Ключова теза з лекції: temperature не гарантує і не виключає різні відповіді. Це лише змінює ймовірність. Навіть T=0 не дає 100% ідентичності через GPU floating-point precision (Anthropic мали публічний postmortem про bf16 vs fp32).

## Pre-requisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/): сам поставить потрібний Python
- `ANTHROPIC_API_KEY` у `.env` в корені репо

## Як запустити

Перший раз (один на весь курс): постав [uv](https://docs.astral.sh/uv/getting-started/installation/), у корені репо скопіюй `.env.example` у `.env` і впиши ключі. Далі з папки уроку:

```bash
uv run main.py
```

Перший `uv run` створює одне `.venv` у корені репо і ставить туди пакети для всіх уроків модулів 1-2, далі воно береться готовим. На Windows команди ті самі.

## Очікуваний output

Дві секції:

1. **"Open-ended prompt"** (`Перелічи переваги мікросервісів`) запускається тричі при T=0, T=0.5, T=1.0. Видно що при T=1.0 виходи різні (різні пункти, різний порядок, інше формулювання). При T=0 виходи близькі або ідентичні.
2. **"Constrained prompt"** (`Перелічи рівно 3 переваги мікросервісів у форматі: 1. Назва, одне речення.`) запускається при T=1.0 тричі. Видно що структура стабільна попри T=1.0, бо промпт сам обмежив варіативність.

Кожен запуск показує перші 200 символів output. Внизу є таблиця "char-level diff between runs" що показує наскільки запуски відрізняються.

## Source

- Lecture 1.4 у курсі "Agentic Engineering з Claude"
- Anthropic temperature docs: https://docs.claude.com/en/api/messages
- Increase Output Consistency: https://docs.claude.com/en/docs/test-and-evaluate/strengthen-guardrails/increase-consistency
