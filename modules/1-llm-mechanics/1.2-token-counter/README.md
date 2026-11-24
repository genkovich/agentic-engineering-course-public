# Demo: Token Counter

**Module:** 1 - LLM Mechanics
**Lectures:** 1.1, 1.2

## Що показує

Скрипт рахує токени для тих самих текстів англійською і українською, для prose і для коду, і рахує орієнтовну ціну запиту. Три речі стають очевидними:

1. **Українська дорожча у токенах за англійську** приблизно у 2 рази при однаковому сенсі речення. Кириличні символи розбиваються на більше токенів.
2. **Output дорожчий за input.** Sonnet 4.6 коштує $3 за 1M input tokens і $15 за 1M output tokens. Чим краще ти питаєш і чим коротше просиш відповідати, тим дешевше.
3. **Код токенізується щільніше за prose.** Ключові слова мов (`function`, `import`, `def`) часто це 1 токен.

## Pre-requisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/): сам поставить потрібний Python
- `ANTHROPIC_API_KEY` у `.env` в корені репо (скопіюй з `.env.example`)

## Як запустити

Перший раз (один на весь курс): постав [uv](https://docs.astral.sh/uv/getting-started/installation/), у корені репо скопіюй `.env.example` у `.env` і впиши ключі. Далі з папки уроку:

```bash
uv run main.py
```

Перший `uv run` створює одне `.venv` у корені репо і ставить туди пакети для всіх уроків модулів 1-2, далі воно береться готовим. На Windows команди ті самі.

## Очікуваний output

Таблиця з 4-5 рядками: текст, мова/тип, кількість токенів, токенів-на-слово, орієнтовна ціна input. Внизу summary: скільки коштує запит на 1000 повідомлень середнього розміру і чому переклад UA коштує дорожче.

## Source

- Lecture 1.2 у курсі "Agentic Engineering з Claude"
- Anthropic API: https://docs.claude.com/en/api/messages-count-tokens
- Pricing: https://www.anthropic.com/pricing#api
