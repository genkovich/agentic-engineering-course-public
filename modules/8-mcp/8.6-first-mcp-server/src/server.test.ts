// Інтеграційні тести MCP-шару через InMemoryTransport з SDK.
// Справжній MCP-клієнт спілкується зі справжнім сервером,
// але без зовнішніх процесів і stdio: транспорт живе у пам'яті тесту.
import { beforeEach, describe, expect, it } from "vitest";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { createServer } from "./server.js";
import { TaskStore } from "./store.js";

// Текст першого text-блоку відповіді: у цьому демо всі результати текстові.
function firstText(result: { content?: unknown }): string {
  const content = result.content as Array<{ type: string; text: string }>;
  expect(content[0].type).toBe("text");
  return content[0].text;
}

describe("task-store MCP server", () => {
  let client: Client;
  let store: TaskStore;

  beforeEach(async () => {
    store = new TaskStore(); // in-memory, без файлу
    const server = createServer(store);
    client = new Client({ name: "test-client", version: "1.0.0" });

    // Пара зв'язаних транспортів: що сервер пише, те клієнт читає, і навпаки.
    const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
    await Promise.all([
      server.connect(serverTransport),
      client.connect(clientTransport),
    ]);
  });

  it("tools/list повертає всі три tools зі схемами", async () => {
    const { tools } = await client.listTools();
    const names = tools.map((tool) => tool.name).sort();

    expect(names).toEqual(["add_task", "complete_task", "list_tasks"]);

    const addTask = tools.find((tool) => tool.name === "add_task")!;
    // zod-схема конвертована у JSON Schema, видиму клієнту.
    expect(addTask.inputSchema.properties).toHaveProperty("title");
    expect(addTask.inputSchema.properties).toHaveProperty("priority");
  });

  it("add_task створює задачу і повертає її з id", async () => {
    const result = await client.callTool({
      name: "add_task",
      arguments: { title: "Prepare slides", priority: "high" },
    });

    const text = firstText(result);
    expect(text).toContain("task-1");
    expect(text).toContain("Prepare slides");
    expect(store.listTasks("open")).toHaveLength(1);
  });

  it("add_task без priority бере default medium", async () => {
    const result = await client.callTool({
      name: "add_task",
      arguments: { title: "Default priority" },
    });

    expect(firstText(result)).toContain('"priority": "medium"');
  });

  it("add_task відхиляє невалідний priority ще на рівні схеми", async () => {
    // Валідацію робить SDK за zod-схемою, до нашого handler-а виклик не доходить.
    // Сервер відповідає протокольною помилкою -32602 (Invalid params),
    // клієнт загортає її у результат з isError: true.
    const result = await client.callTool({
      name: "add_task",
      arguments: { title: "Bad", priority: "urgent" },
    });

    expect(result.isError).toBe(true);
    const text = firstText(result);
    expect(text).toContain("-32602");
    expect(text).toContain("priority");
    expect(store.listTasks("all")).toHaveLength(0); // handler не виконався
  });

  it("complete_task закриває існуючу задачу", async () => {
    const task = store.addTask("Close me", "low");

    const result = await client.callTool({
      name: "complete_task",
      arguments: { id: task.id },
    });

    expect(result.isError).toBeFalsy();
    expect(firstText(result)).toContain('"status": "done"');
  });

  it("complete_task з неіснуючим id повертає isError, а не краш", async () => {
    const result = await client.callTool({
      name: "complete_task",
      arguments: { id: "task-999" },
    });

    expect(result.isError).toBe(true);
    const text = firstText(result);
    expect(text).toContain("task-999");
    expect(text).toContain("list_tasks"); // підказка моделі, що робити далі
  });

  it("list_tasks фільтрує за статусом", async () => {
    store.addTask("Open one", "medium");
    const done = store.addTask("Done one", "medium");
    store.completeTask(done.id);

    const openResult = await client.callTool({
      name: "list_tasks",
      arguments: { status: "open" },
    });
    const openText = firstText(openResult);
    expect(openText).toContain("Open one");
    expect(openText).not.toContain("Done one");

    const allResult = await client.callTool({
      name: "list_tasks",
      arguments: {},
    });
    const allText = firstText(allResult);
    expect(allText).toContain("Open one");
    expect(allText).toContain("Done one");
  });

  it("resource tasks://summary повертає підсумок", async () => {
    const { resources } = await client.listResources();
    expect(resources.map((resource) => resource.uri)).toContain("tasks://summary");

    store.addTask("Oldest", "high");
    const done = store.addTask("Finished", "low");
    store.completeTask(done.id);

    const result = await client.readResource({ uri: "tasks://summary" });
    const text = (result.contents[0] as { text: string }).text;

    expect(text).toContain("Відкритих задач: 1");
    expect(text).toContain("Закритих задач: 1");
    expect(text).toContain("Oldest");
  });

  it("prompt plan-day підставляє focus і відкриті задачі", async () => {
    const { prompts } = await client.listPrompts();
    expect(prompts.map((prompt) => prompt.name)).toContain("plan-day");

    store.addTask("Review PR", "high");
    const done = store.addTask("Old chore", "low");
    store.completeTask(done.id);

    const result = await client.getPrompt({
      name: "plan-day",
      arguments: { focus: "deep work" },
    });

    const message = result.messages[0];
    expect(message.role).toBe("user");
    const text = (message.content as { type: string; text: string }).text;

    expect(text).toContain("deep work");
    expect(text).toContain("Review PR"); // відкрита потрапила у шаблон
    expect(text).not.toContain("Old chore"); // закрита ні
  });
});
