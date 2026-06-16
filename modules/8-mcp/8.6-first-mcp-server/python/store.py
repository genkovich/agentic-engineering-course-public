"""store.py: логіка сховища задач, повністю відокремлена від MCP-шару.

Тут немає жодного import з MCP SDK. Це звичайний Python-модуль, який можна
тестувати без транспорту і протоколу — точне дзеркало store.ts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

Priority = Literal["low", "medium", "high"]
Status = Literal["open", "done"]


class Task(BaseModel):
    """Одна задача.

    Поля навмисно у camelCase (createdAt/completedAt): так data/tasks.json
    лишається байт-сумісним з TypeScript-версією демо, і обидва сервери
    читають та пишуть один і той самий файл.
    """

    id: str
    title: str
    priority: Priority
    status: Status
    createdAt: str  # ISO-дата створення
    completedAt: str | None = None  # ISO-дата закриття, тільки для status=done


class TaskNotFoundError(Exception):
    """Окремий клас помилки: MCP-шар ловить саме її і перетворює на
    зрозумілу відповідь для моделі (дзеркало TaskNotFoundError зі store.ts)."""

    def __init__(self, task_id: str) -> None:
        super().__init__(f'Task with id "{task_id}" not found')
        self.id = task_id


@dataclass
class Summary:
    """Дані для resource tasks://summary."""

    open: int
    done: int
    oldest_open: Task | None = None


def _now_iso() -> str:
    # Формат як у new Date().toISOString() з TS: мілісекунди + суфікс Z.
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace(
        "+00:00", "Z"
    )


class TaskStore:
    # file_path опціональний: без нього сховище живе тільки в пам'яті.
    # Це зручно для тестів, їм не потрібен файл на диску (як у store.ts:41).
    def __init__(self, file_path: str | Path | None = None) -> None:
        self._file_path = Path(file_path) if file_path is not None else None
        self._tasks: dict[str, Task] = {}
        self._next_id = 1

    # Читає data/tasks.json якщо він є. Відсутність файлу не помилка,
    # це просто перший запуск сервера.
    def load(self) -> None:
        if self._file_path is None or not self._file_path.exists():
            return
        data = json.loads(self._file_path.read_text(encoding="utf-8"))
        self._next_id = data["nextId"]
        self._tasks = {item["id"]: Task.model_validate(item) for item in data["tasks"]}

    # Після кожної зміни скидаємо стан на диск.
    # Для демо це найпростіша робоча persistence-стратегія.
    def _persist(self) -> None:
        if self._file_path is None:
            return
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "nextId": self._next_id,
            "tasks": [
                task.model_dump(exclude_none=True) for task in self._tasks.values()
            ],
        }
        self._file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def add_task(self, title: str, priority: Priority) -> Task:
        task = Task(
            id=f"task-{self._next_id}",
            title=title,
            priority=priority,
            status="open",
            createdAt=_now_iso(),
        )
        self._next_id += 1
        self._tasks[task.id] = task
        self._persist()
        return task

    # Кидає TaskNotFoundError для неіснуючого id.
    # Рішення "що з цим робити" приймає шар вище (MCP handler).
    def complete_task(self, task_id: str) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        completed = task.model_copy(
            update={"status": "done", "completedAt": _now_iso()}
        )
        self._tasks[task_id] = completed
        self._persist()
        return completed

    # "all" повертає все, інакше фільтруємо за статусом.
    def list_tasks(self, status: Status | Literal["all"] = "all") -> list[Task]:
        tasks = list(self._tasks.values())
        if status == "all":
            return tasks
        return [task for task in tasks if task.status == status]

    # Дані для resource tasks://summary:
    # кількість відкритих і закритих, найстаріша відкрита задача.
    def summary(self) -> Summary:
        open_tasks = self.list_tasks("open")
        done_tasks = self.list_tasks("done")
        oldest_open = (
            sorted(open_tasks, key=lambda task: task.createdAt)[0]
            if open_tasks
            else None
        )
        return Summary(
            open=len(open_tasks), done=len(done_tasks), oldest_open=oldest_open
        )
