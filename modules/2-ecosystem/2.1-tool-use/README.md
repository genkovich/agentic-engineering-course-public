# Demo: Tool Use

**Module:** 2 - Ecosystem
**Lectures:** 2.1, 2.2

## Що показує

Найпростіший tool use цикл з Anthropic SDK. Визначаємо два tools (`get_weather`, `calculator`), задаємо питання моделі, ловимо `tool_use` блок у відповіді, виконуємо його локально, повертаємо `tool_result` назад моделі, отримуємо фінальну відповідь.

Ключове розуміння: модель сама не виконує функції. Вона просить тебе їх виконати і чекає результат. Tool use це структурований спосіб попросити "виконай і поверни мені дані".

### Три типи tools (з лекції 2.1)

1. **Інформаційні** (read-only): дають моделі дані. `get_weather`, `search_docs`, `read_file`. Низький ризик, бо не міняють стан світу.
2. **Дієві** (actions): міняють стан або викликають побічні ефекти. `send_email`, `create_pr`, `delete_record`. Потребують дозволів і логування.
3. **Верифікаційні**: підтверджують гіпотезу або перевіряють факт. `run_tests`, `lint`, `count_records`. Корисні в agentic loop для self-correction.

### П'ять кроків циклу tool use (з лекції 2.1)

1. Клієнт відправляє повідомлення з масивом `tools` (JSON Schema definitions).
2. Модель повертає або текст, або `tool_use` блок з ім'ям tool і аргументами.
3. Клієнт локально виконує функцію.
4. Клієнт відправляє назад `tool_result` блок з тим самим `tool_use_id`.
5. Модель або викликає наступний tool, або повертає фінальну текстову відповідь.

JSON Schema це універсальний стандарт для tool definitions: працює у Claude API, MCP (Model Context Protocol), OpenAPI 3.0. Описав tool один раз і він плагається у будь-який ecosystem.

## Pre-requisites

- Python 3.10+
- `ANTHROPIC_API_KEY` у `.env`

## Як запустити

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make run
```

## Очікуваний output

Покрокова трасування: запит, що модель попросила (tool name + аргументи), результат локального виконання, фінальна відповідь моделі. Запускає 2 сценарії - погода і калькулятор.

## Source

- Lecture 2.1, 2.2 у курсі "Agentic Engineering з Claude"
- Anthropic tool use docs: https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview
