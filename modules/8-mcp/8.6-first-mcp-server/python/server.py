"""server.py: MCP-шар (FastMCP) поверх TaskStore.

Дзеркало server.ts мовою Python. Ті самі три примітиви протоколу на одному
домені, та сама жорстка межа між шарами:
  - Tools (add_task, complete_task, list_tasks) — дії, які модель викликає сама
  - Resource (tasks://summary) — дані, які додаток підкладає у контекст
  - Prompt (plan_day) — готовий шаблон, який юзер обирає явно

Що у TS робить зв'язка zod + registerTool, тут робить сама сигнатура функції:
type hints + Field(description=...) стають JSON Schema, а анотація повернення
дає structured output без окремого outputSchema.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from store import Priority, Task, TaskNotFoundError, TaskStore

# Persistence-файл лежить поруч з демо: <demo-root>/data/tasks.json — той самий
# файл, що й у TS-версії (server.ts), тому стан спільний. Шлях рахуємо від
# цього модуля, а не від cwd: MCP-клієнт може запустити сервер з будь-якої
# директорії.
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


def build_server(store: TaskStore) -> FastMCP:
    """Фабрика сервера приймає store ззовні (dependency injection).
    Завдяки цьому тести підкладають in-memory store без файлу на диску —
    дзеркало createServer(store) зі server.ts."""
    mcp = FastMCP("task-store")

    # ─── TOOL 1: add_task ───
    # Окремий inputSchema писати не треба: type hints на параметрах +
    # Field(description=...) самі стають JSON Schema, а docstring — description
    # tool-а. Анотація повернення `-> Task` вмикає structured output: FastMCP
    # згенерує outputSchema і покладе structuredContent у відповідь автоматично
    # (те, що у TS вимагало явного outputSchema + ручного structuredContent).
    @mcp.tool()
    def add_task(
        title: Annotated[str, Field(description="Назва задачі", min_length=1)],
        priority: Annotated[
            Priority, Field(description="Пріоритет задачі")
        ] = "medium",
    ) -> Task:
        """Додає нову задачу у сховище. Повертає створену задачу з її id."""
        return store.add_task(title, priority)

    # ─── TOOL 2: complete_task ───
    # Ключовий момент демо: error handling. Неіснуючий id це НЕ краш.
    # Шар сховища кидає типізовану TaskNotFoundError, а MCP-шар ловить саме її
    # і кидає ValueError зі зрозумілим текстом. FastMCP сам перетворює виключення
    # у відповідь з isError: true, тож модель прочитає підказку і виправиться.
    @mcp.tool()
    def complete_task(
        id: Annotated[
            str, Field(description="Ідентифікатор задачі, наприклад task-1")
        ],
    ) -> Task:
        """Позначає задачу виконаною за її id."""
        try:
            return store.complete_task(id)
        except TaskNotFoundError as error:
            raise ValueError(
                f'Задачі з id "{id}" не існує. '
                "Виклич list_tasks, щоб побачити актуальні id."
            ) from error

    # ─── TOOL 3: list_tasks ───
    @mcp.tool()
    def list_tasks(
        status: Annotated[
            Literal["open", "done", "all"],
            Field(description="Фільтр: open, done або all"),
        ] = "all",
    ) -> list[Task]:
        """Повертає список задач. Можна відфільтрувати за статусом."""
        return store.list_tasks(status)

    # ─── RESOURCE: tasks://summary ───
    # Resource це READ-канал: модель (або юзер через @-mention) читає дані,
    # але нічого не змінює. URI-схему `tasks://` вигадуємо самі.
    @mcp.resource(
        "tasks://summary",
        title="Tasks summary",
        description="Текстовий підсумок: скільки відкритих і закритих задач.",
        mime_type="text/plain",
    )
    def tasks_summary() -> str:
        result = store.summary()
        lines = [
            f"Відкритих задач: {result.open}",
            f"Закритих задач: {result.done}",
        ]
        if result.oldest_open is not None:
            oldest = result.oldest_open
            lines.append(
                f"Найстаріша відкрита: {oldest.title} "
                f"({oldest.id}, створена {oldest.createdAt})"
            )
        return "\n".join(lines)

    # ─── PROMPT: plan_day ───
    # Prompt це шаблон, який юзер викликає явно. Сервер сам підставляє у текст
    # актуальні відкриті задачі, тож модель одразу отримує і інструкцію, і дані.
    @mcp.prompt(
        title="Plan the day",
        description="Складає план дня з відкритих задач, з урахуванням фокусу.",
    )
    def plan_day(
        focus: Annotated[
            str, Field(description="Головний фокус дня, наприклад 'код-рев'ю'")
        ],
    ) -> str:
        open_tasks = store.list_tasks("open")
        if open_tasks:
            task_list = "\n".join(
                f"- [{task.priority}] {task.title} ({task.id})" for task in open_tasks
            )
        else:
            task_list = "- (відкритих задач немає)"
        return "\n".join(
            [
                f"Сплануй мій день. Головний фокус: {focus}.",
                "",
                "Мої відкриті задачі:",
                task_list,
                "",
                "Розстав їх у порядку виконання, врахуй пріоритети.",
                "Задачі, які не стосуються фокусу, запропонуй перенести.",
            ]
        )

    return mcp


def main() -> None:
    store = TaskStore(DATA_FILE)
    store.load()

    mcp = build_server(store)

    # ВАЖЛИВО: stdout належить JSON-RPC повідомленням протоколу. Будь-який
    # зайвий рядок у stdout ламає парсер клієнта. Для діагностики — тільки stderr.
    print("task-store MCP server (Python/FastMCP) running on stdio", file=sys.stderr)

    # mcp.run() за замовчуванням слухає stdio-транспорт.
    mcp.run()


if __name__ == "__main__":
    main()
