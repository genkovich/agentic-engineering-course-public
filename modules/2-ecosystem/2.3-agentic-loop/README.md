# Demo: Agentic Loop

**Module:** 2 - Ecosystem
**Lectures:** 2.3

## Що показує

Явна реалізація observe → think → act loop без SDK helpers. Це той самий патерн, що під капотом у Claude Code, Cursor, Aider, всіх "AI coding assistants". Скрипт показує, що сам по собі агент це 30 рядків коду: while-loop з max_iterations, набір tools, stop condition (assistant без tool_use means done).

Задача для агента: дослідити фейкову файлову систему (in-memory dict), знайти конкретний файл, прочитати його. Доступні tools: `list_files(dir)`, `read_file(path)`, `grep(pattern)`. Агент сам вирішує послідовність викликів.

### Цитата з лекції 2.3

> 15 рядків Python вирішують більше задач ніж складні agentic фреймворки.

Сама ідея агента це while-loop. Все інше (memory, planning, multi-agent orchestration) це опційні шари які додаються коли реально потрібні.

### Шість умов завершення agentic loop

1. **end_turn**: модель повернула фінальну текстову відповідь без `tool_use`. Стандартний happy path.
2. **max_tokens**: відповідь обрізана бо досягла ліміту. Loop має продовжити з підказкою "продовжуй".
3. **max_turns**: пройшли N ітерацій без завершення. Захист від зациклення (наприклад, 25 turns).
4. **max_budget_usd**: витратили $X на запити. Захист від експоненційно дорогих сесій.
5. **human_interruption**: користувач натиснув Ctrl+C або відправив stop signal.
6. **clarification_request**: модель попросила уточнення яке потребує human input.

Demo нижче зупиняється тільки за умовою #1 і #3. У production треба обробляти всі шість.

### Agents vs Workflows (Anthropic, "Building effective agents")

- **Workflow**: захардкоджена послідовність LLM викликів. Передбачуваність, дешево.
- **Agent**: модель сама вирішує наступний крок з доступних tools. Гнучкість, дорожче.

Більшість продакшен-задач це workflows з одним або двома agentic steps усередині, не повноцінний agent.

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

Покрокова трасування ітерацій loop: на кожному кроці видно, що Claude думає (text) і що викликає (tool_use). Видно як агент будує hypothesis → перевіряє → coригує. Завершується коли модель повертає текстову відповідь без tool_use.

## Source

- Lecture 2.3 у курсі "Agentic Engineering з Claude"
- Anthropic blog "Building effective agents": https://www.anthropic.com/engineering/building-effective-agents
