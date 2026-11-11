# Demo: Token Counter і калькулятор вартості

**Module:** 1 - LLM Mechanics
**Lectures:** 1.1, 1.2

> Це демо до уроку: його можна запустити й подивитись код. Домашнє завдання описане в уроці в Kwiga, запускати демо для нього не обов'язково, якщо в завданні не сказано інакше.

## Що показує

Скрипт рахує токени для тих самих текстів англійською і українською, для prose і для коду, і рахує орієнтовну ціну запиту. Три речі стають очевидними:

1. **Українська дорожча у токенах за англійську** приблизно у 2 рази при однаковому сенсі речення. Кириличні символи розбиваються на більше токенів.
2. **Output дорожчий за input.** Sonnet 5.5 коштує $2 за 1M input tokens і $10 за 1M output tokens. Чим краще ти питаєш і чим коротше просиш відповідати, тим дешевше.
3. **Код токенізується щільніше за prose.** Ключові слова мов (`function`, `import`, `def`) часто це 1 токен.

## Калькулятор вартості (сценарій домашки 1.2)

`cost_calc.py` рахує той самий сценарій, що й завдання уроку 1.2: системний prompt на 5 000 токенів, запит на 300, thinking 2 000 і відповідь 800, разом 1000 запитів. Три варіанти: без кешу, з кешованим системним prompt і з кешем через Batch API. API-ключ не потрібен, це просто арифметика.

Спершу порахуй домашку руками, потім звір:

```bash
python3 cost_calc.py                            # Sonnet 5.5
python3 cost_calc.py --model claude-opus-5-5
python3 cost_calc.py --input 3 --output 15 --cache-write 3.75 --cache-read 0.3   # свої ціни
python3 cost_calc.py --batch-discount 0         # модель без batch
```

Ціни в скрипті звірені з https://platform.claude.com/docs/en/about-claude/pricing на 2026-11-11. Для домашки бери ціни зі сторінки «Актуальний стан» у Kwiga і, якщо вони інші, передай їх флагами.

## Pre-requisites

- Python 3.10+
- `ANTHROPIC_API_KEY` у `.env` (скопіюй з `.env.example`), лише для `main.py`

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
- Pricing: https://platform.claude.com/docs/en/about-claude/pricing
