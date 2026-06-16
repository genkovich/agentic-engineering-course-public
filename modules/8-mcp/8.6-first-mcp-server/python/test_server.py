"""Тести Python-демо. Два рівні, як у TS-версії:

  - unit-тести TaskStore: чиста логіка, без MCP і без транспорту;
  - тести MCP-шару через in-memory клієнт SDK: справжній MCP-клієнт
    спілкується зі справжнім FastMCP-сервером, але без stdio і процесів
    (дзеркало InMemoryTransport зі server.test.ts).

Плюс один тест інтеропу: файл сховища байт-сумісний з TypeScript-версією.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager

import pytest
from mcp.shared.memory import (
    create_connected_server_and_client_session as client_session,
)

from server import build_server
from store import TaskNotFoundError, TaskStore


# ─────────────────────────── unit-тести TaskStore ───────────────────────────


def test_add_task_creates_open_task_with_sequential_id():
    store = TaskStore()  # без file_path: тільки пам'ять
    first = store.add_task("Write lecture", "high")
    second = store.add_task("Record screencast", "low")

    assert first.id == "task-1"
    assert second.id == "task-2"
    assert first.status == "open"
    assert first.priority == "high"
    assert first.createdAt


def test_complete_task_sets_status_and_completed_at():
    store = TaskStore()
    task = store.add_task("Ship demo", "medium")
    completed = store.complete_task(task.id)

    assert completed.status == "done"
    assert completed.completedAt
    assert len(store.list_tasks("done")) == 1


def test_complete_task_raises_for_missing_id():
    store = TaskStore()
    with pytest.raises(TaskNotFoundError) as exc:
        store.complete_task("task-999")
    assert "task-999" in str(exc.value)


def test_list_tasks_filters_by_status():
    store = TaskStore()
    store.add_task("A", "low")
    b = store.add_task("B", "high")
    store.complete_task(b.id)

    assert len(store.list_tasks("all")) == 2
    assert [t.title for t in store.list_tasks("open")] == ["A"]
    assert [t.title for t in store.list_tasks("done")] == ["B"]


def test_summary_counts_and_finds_oldest_open():
    store = TaskStore()
    a = store.add_task("Oldest open", "medium")
    store.add_task("Newer open", "medium")
    c = store.add_task("Closed", "medium")
    store.complete_task(c.id)

    summary = store.summary()
    assert summary.open == 2
    assert summary.done == 1
    assert summary.oldest_open is not None
    assert summary.oldest_open.id == a.id


def test_summary_without_open_has_no_oldest():
    store = TaskStore()
    summary = store.summary()
    assert summary.open == 0
    assert summary.oldest_open is None


def test_persistence_round_trip(tmp_path):
    file_path = tmp_path / "tasks.json"

    store = TaskStore(file_path)
    store.load()
    task = store.add_task("Survive restart", "high")
    store.complete_task(task.id)

    # "Перезапуск": новий інстанс читає той самий файл.
    reloaded = TaskStore(file_path)
    reloaded.load()

    tasks = reloaded.list_tasks("all")
    assert len(tasks) == 1
    assert tasks[0].title == "Survive restart"
    assert tasks[0].status == "done"

    # Лічильник id теж відновлюється: нова задача не конфліктує зі старою.
    nxt = reloaded.add_task("After restart", "low")
    assert nxt.id == "task-2"


def test_load_without_file_does_not_crash(tmp_path):
    store = TaskStore(tmp_path / "tasks.json")
    store.load()  # перший запуск: файлу ще немає
    assert store.list_tasks("all") == []


def test_file_format_is_byte_compatible_with_typescript(tmp_path):
    """Файл, який пише Python-сервер, має ту саму форму, що й TS-версія,
    і Python читає файл, записаний TS-сервером (спільний домен)."""
    file_path = tmp_path / "tasks.json"
    store = TaskStore(file_path)
    store.load()
    done = store.add_task("Done one", "high")
    store.complete_task(done.id)
    store.add_task("Open one", "low")

    raw = json.loads(file_path.read_text(encoding="utf-8"))
    assert raw["nextId"] == 3
    # camelCase-ключі, як у TS
    assert set(raw["tasks"][0]) == {
        "id",
        "title",
        "priority",
        "status",
        "createdAt",
        "completedAt",
    }
    # completedAt присутній тільки для закритих (для open поле відсутнє)
    assert "completedAt" not in raw["tasks"][1]

    # Зворотний бік: читаємо файл у форматі TS-сервера.
    ts_file = tmp_path / "from-ts.json"
    ts_file.write_text(
        json.dumps(
            {
                "nextId": 2,
                "tasks": [
                    {
                        "id": "task-1",
                        "title": "From TS",
                        "priority": "medium",
                        "status": "open",
                        "createdAt": "2026-06-13T10:00:00.000Z",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    from_ts = TaskStore(ts_file)
    from_ts.load()
    assert [t.title for t in from_ts.list_tasks("all")] == ["From TS"]
    assert from_ts.add_task("After TS", "low").id == "task-2"


# ─────────────────────── тести MCP-шару (in-memory) ─────────────────────────


@asynccontextmanager
async def connected(store: TaskStore):
    """Піднімає FastMCP-сервер на даному store і повертає під'єднаний
    in-memory клієнт — без stdio і зовнішніх процесів."""
    mcp = build_server(store)
    async with client_session(mcp._mcp_server) as client:
        yield client


async def test_list_tools_returns_all_three_with_generated_schema():
    async with connected(TaskStore()) as client:
        tools = (await client.list_tools()).tools
        names = sorted(t.name for t in tools)
        assert names == ["add_task", "complete_task", "list_tasks"]

        add = next(t for t in tools if t.name == "add_task")
        # type hints стали JSON Schema, видимою клієнту.
        assert "title" in add.inputSchema["properties"]
        assert "priority" in add.inputSchema["properties"]
        priority = add.inputSchema["properties"]["priority"]
        assert priority["enum"] == ["low", "medium", "high"]
        assert priority["default"] == "medium"
        # анотація повернення -> Task дала structured output (outputSchema).
        assert add.outputSchema is not None
        assert "createdAt" in add.outputSchema["properties"]


async def test_add_task_creates_task_and_returns_it_with_id():
    store = TaskStore()
    async with connected(store) as client:
        result = await client.call_tool(
            "add_task", {"title": "Prepare slides", "priority": "high"}
        )
        assert not result.isError
        assert result.structuredContent["id"] == "task-1"
        assert result.structuredContent["title"] == "Prepare slides"
        assert len(store.list_tasks("open")) == 1


async def test_add_task_without_priority_defaults_to_medium():
    async with connected(TaskStore()) as client:
        result = await client.call_tool("add_task", {"title": "Default priority"})
        assert result.structuredContent["priority"] == "medium"


async def test_add_task_rejects_invalid_priority_at_schema_level():
    # Валідацію робить SDK за згенерованою схемою, до handler-а виклик не доходить.
    store = TaskStore()
    async with connected(store) as client:
        result = await client.call_tool(
            "add_task", {"title": "Bad", "priority": "urgent"}
        )
        assert result.isError
        assert "priority" in result.content[0].text
        assert len(store.list_tasks("all")) == 0  # handler не виконався


async def test_complete_task_closes_existing_task():
    store = TaskStore()
    task = store.add_task("Close me", "low")
    async with connected(store) as client:
        result = await client.call_tool("complete_task", {"id": task.id})
        assert not result.isError
        assert result.structuredContent["status"] == "done"


async def test_complete_task_missing_id_returns_iserror_not_crash():
    async with connected(TaskStore()) as client:
        result = await client.call_tool("complete_task", {"id": "task-999"})
        assert result.isError
        text = result.content[0].text
        assert "task-999" in text
        assert "list_tasks" in text  # підказка моделі, що робити далі


async def test_list_tasks_filters_by_status():
    store = TaskStore()
    store.add_task("Open one", "medium")
    done = store.add_task("Done one", "medium")
    store.complete_task(done.id)
    async with connected(store) as client:
        open_result = await client.call_tool("list_tasks", {"status": "open"})
        titles = [t["title"] for t in open_result.structuredContent["result"]]
        assert "Open one" in titles
        assert "Done one" not in titles

        all_result = await client.call_tool("list_tasks", {})
        all_titles = [t["title"] for t in all_result.structuredContent["result"]]
        assert {"Open one", "Done one"} <= set(all_titles)


async def test_resource_summary_returns_overview():
    store = TaskStore()
    async with connected(store) as client:
        resources = (await client.list_resources()).resources
        assert "tasks://summary" in [str(r.uri) for r in resources]

        store.add_task("Oldest", "high")
        done = store.add_task("Finished", "low")
        store.complete_task(done.id)

        result = await client.read_resource("tasks://summary")
        text = result.contents[0].text
        assert "Відкритих задач: 1" in text
        assert "Закритих задач: 1" in text
        assert "Oldest" in text


async def test_prompt_plan_day_injects_focus_and_open_tasks():
    store = TaskStore()
    async with connected(store) as client:
        prompts = (await client.list_prompts()).prompts
        assert "plan_day" in [p.name for p in prompts]

        store.add_task("Review PR", "high")
        done = store.add_task("Old chore", "low")
        store.complete_task(done.id)

        result = await client.get_prompt("plan_day", {"focus": "deep work"})
        message = result.messages[0]
        assert message.role == "user"
        text = message.content.text
        assert "deep work" in text
        assert "Review PR" in text  # відкрита потрапила у шаблон
        assert "Old chore" not in text  # закрита ні
