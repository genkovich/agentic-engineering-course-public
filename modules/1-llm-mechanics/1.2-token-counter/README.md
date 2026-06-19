# Demo: Token Counter

**Module:** 1 - LLM Mechanics
**Lectures:** 1.1, 1.2

## Що показує

Скрипт рахує токени для тих самих текстів англійською і українською, для prose і для коду, і рахує орієнтовну ціну запиту. Три речі стають очевидними:

1. **Українська дорожча у токенах за англійську** приблизно у 2 рази при однаковому сенсі речення. Кириличні символи розбиваються на більше токенів.
2. **Output дорожчий за input.** Sonnet 4.6 коштує $3 за 1M input tokens і $15 за 1M output tokens. Чим краще ти питаєш і чим коротше просиш відповідати, тим дешевше.
3. **Код токенізується щільніше за prose.** Ключові слова мов (`function`, `import`, `def`) часто це 1 токен.

## Pre-requisites

- Python 3.10+
- `ANTHROPIC_API_KEY` у `.env` (скопіюй з `.env.example`)

## Як запустити

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Додай свій ANTHROPIC_API_KEY у .env
make run
```

## Очікуваний output

Таблиця з 4-5 рядками: текст, мова/тип, кількість токенів, токенів-на-слово, орієнтовна ціна input. Внизу summary: скільки коштує запит на 1000 повідомлень середнього розміру і чому переклад UA коштує дорожче.

## Source

- Lecture 1.2 у курсі "Agentic Engineering з Claude"
- Anthropic API: https://docs.claude.com/en/api/messages-count-tokens
- Pricing: https://www.anthropic.com/pricing#api
