# Demo: Data Privacy (Claude Code Telemetry Toggles)

**Module:** 2 - Ecosystem
**Lectures:** 2.7

## Що показує

Скрипт читає поточні значення environment variables які контролюють що Claude Code відправляє на сервери Anthropic, і показує таблицю "що зараз увімкнено / що вимкнено". Жодних реальних запитів до Anthropic скрипт не робить, тільки інспектує локальне середовище.

Контрольовані змінні (з лекції 2.7):

- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` - master switch який вимикає одразу телеметрію, error reporting, /feedback, опитування якості і автооновлення.
- `DISABLE_TELEMETRY` - тільки статистика використання.
- `DISABLE_ERROR_REPORTING` - тільки звіти про збої.
- `DISABLE_FEEDBACK_COMMAND` - тільки команда /feedback (вона зберігає повну історію 5 років).
- `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY` - тільки опитування якості сесії.
- `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` - прибирає API ключі і паролі з environment subprocess викликів. Захист від prompt injection що намагається витягти секрети через shell.

Скрипт також показує три канали даних з лекції (основний запит, телеметрія, фідбек), що з них завжди іде, а що можна вимкнути, і дає рекомендований set для роботи з кодом компанії.

## Контекст з лекції

Samsung у квітні 2023 заборонив працівникам ChatGPT після того як інженери тричі за місяць злили конфіденційний код. На платних тарифах Anthropic, OpenAI і Google не навчають моделі на твоїх даних, але стандартний retention 30 днів для перевірки на abuse. Zero Data Retention доступний у Claude через API всім, у OpenAI тільки після погодження з sales.

`/feedback` команда зберігає повну історію розмови 5 років. Не використовуй її якщо в контексті є чутливий код.

## Pre-requisites

- Python 3.10+ (тільки stdlib, нічого ставити не треба)

## Як запустити

```bash
make run
```

Опційно скопіюй `.env.example` у `.env` щоб expериментувати зі значеннями локально:

```bash
cp .env.example .env
# відредагуй .env
make run
```

Або тестуй прямо у shell:

```bash
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 python3 main.py
```

## Очікуваний output

Три секції:

1. **Поточний стан 6 змінних.** Таблиця з ім'ям, значенням з env (або `<not set>`), і ефектом ON/OFF.
2. **Що це означає для трьох каналів даних.** Канал 1 (запит/відповідь) завжди шифрується, канал 2 (телеметрія) і канал 3 (фідбек) показуються як включені або відключені на основі поточного env.
3. **Рекомендований setup для коду компанії.** Конкретні рядки для `.zshrc`/`.bashrc` або `settings.json` `env` блок.

## Source

- Lecture 2.7 у курсі "Agentic Engineering з Claude"
- Claude Code privacy docs: https://docs.claude.com/en/docs/claude-code/data-usage
- Anthropic data usage policy: https://www.anthropic.com/legal/commercial-terms
- Anthropic ZDR: https://docs.claude.com/en/api/zero-data-retention
