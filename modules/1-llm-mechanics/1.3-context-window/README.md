# Demo: Context Window

**Module:** 1 - LLM Mechanics
**Lectures:** 1.3, 1.7

## Що показує

Симулюємо довгу робочу сесію: messages array росте по 1 повідомленню, після кожного скрипт рахує накопичений токен-total через `messages.count_tokens()` і показує % від context window. Sonnet 4.6 має 1M tokens, але у Claude Code за замовчуванням 200K. Скрипт сигналить при 70% (попередження) і 90% (треба `/compact` або новий чат).

Ключове розуміння з lecture 1.7: **модель stateless**. Кожен наступний запит передає всю історію наново. Це означає, що токени не "залишаються у моделі", їх треба надсилати щоразу, і платити теж щоразу. Тому довгі сесії дорожчі експоненційно.

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

Покрокова прогресія: після 1, 5, 10, 20, 50 повідомлень - показує total tokens, % від 200K (Claude Code default) і % від 1M (Sonnet 4.6 max). Внизу прогноз: при цьому темпі сесія вичерпає 200K за приблизно X повідомлень. Demo пояснює коли тиснути `/compact`.

## Source

- Lecture 1.3, 1.7 у курсі "Agentic Engineering з Claude"
- Anthropic API: https://docs.claude.com/en/api/messages-count-tokens
- Claude Code context: https://docs.claude.com/en/docs/claude-code/memory
