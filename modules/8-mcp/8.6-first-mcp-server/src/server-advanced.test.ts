// Інтеграційні тести advanced-сервера (лекція 8.10) через InMemoryTransport.
// Тут клієнт грає роль, яку у реальному демо грає MCP Inspector: оголошує
// client capabilities (sampling, elicitation, roots) і відповідає на запити
// сервера мок-обробниками. Так happy-path кожної client feature перевіряється
// без UI - те, чого CLI Inspector зробити не може.
import { beforeEach, describe, expect, it } from "vitest";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import {
  CreateMessageRequestSchema,
  ElicitRequestSchema,
  ListRootsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { createAdvancedServer } from "./server-advanced.js";
import { TaskStore } from "./store.js";

function firstText(result: { content?: unknown }): string {
  const content = result.content as Array<{ type: string; text: string }>;
  expect(content[0].type).toBe("text");
  return content[0].text;
}

describe("task-store advanced MCP server", () => {
  let client: Client;
  let store: TaskStore;

  beforeEach(async () => {
    store = new TaskStore(); // in-memory, без файлу

    // Клієнт оголошує всі три client features, які демонструє сервер.
    client = new Client(
      { name: "test-client", version: "1.0.0" },
      { capabilities: { sampling: {}, elicitation: {}, roots: {} } },
    );

    // Мок sampling: замість справжньої моделі повертаємо фіксований підсумок.
    client.setRequestHandler(CreateMessageRequestSchema, async () => ({
      role: "assistant",
      content: { type: "text", text: "Фокус на релізі; почни з найвищого пріоритету." },
      model: "mock-model",
      stopReason: "endTurn",
    }));

    // Мок elicitation: користувач "обрав" high і підтвердив форму.
    client.setRequestHandler(ElicitRequestSchema, async () => ({
      action: "accept",
      content: { priority: "high" },
    }));

    // Мок roots: клієнт оголошує одну робочу директорію.
    client.setRequestHandler(ListRootsRequestSchema, async () => ({
      roots: [{ uri: "file:///tmp/project", name: "project" }],
    }));

    const server = createAdvancedServer(store);
    const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
    await Promise.all([
      server.connect(serverTransport),
      client.connect(clientTransport),
    ]);
  });

  it("tools/list повертає всі 7 tools (3 базові + 4 advanced)", async () => {
    const { tools } = await client.listTools();
    const names = tools.map((tool) => tool.name).sort();
    expect(names).toEqual([
      "add_task",
      "add_task_guided",
      "complete_task",
      "export_tasks",
      "list_tasks",
      "reprioritize_all",
      "summarize_tasks",
    ]);
  });

  it("summarize_tasks через sampling повертає згенерований підсумок", async () => {
    store.addTask("Підготувати реліз", "high");

    const result = await client.callTool({ name: "summarize_tasks", arguments: {} });

    expect(result.isError).toBeFalsy();
    expect(firstText(result)).toContain("Фокус на релізі");
  });

  it("add_task_guided з явним priority не питає форму", async () => {
    const result = await client.callTool({
      name: "add_task_guided",
      arguments: { title: "Прямий шлях", priority: "low" },
    });

    expect(result.isError).toBeFalsy();
    expect(firstText(result)).toContain('"priority": "low"');
    expect(store.listTasks("open")).toHaveLength(1);
  });

  it("add_task_guided без priority питає форму (elicitation) і бере відповідь", async () => {
    const result = await client.callTool({
      name: "add_task_guided",
      arguments: { title: "Через форму" },
    });

    // Мок elicitation повернув accept + priority=high.
    expect(result.isError).toBeFalsy();
    expect(firstText(result)).toContain('"priority": "high"');
    expect(store.listTasks("open")[0].priority).toBe("high");
  });

  it("export_tasks читає roots і показує цільовий шлях у межах кореня", async () => {
    store.addTask("Будь-що", "medium");

    const result = await client.callTool({ name: "export_tasks", arguments: {} });

    const text = firstText(result);
    expect(text).toContain("file:///tmp/project");
    expect(text).toContain("file:///tmp/project/tasks.md");
    expect(text).toContain("у межах roots");
  });
});
