// 8.7-mcp-inspector honest server: самодостатній task-store для практики з Inspector.
// In-memory, без persistence і Python-дзеркала - лише те, що треба, щоб побачити
// контраст чесного й зламаного сервера на одному межовому виклику.
//
// Три tools: add_task / complete_task / list_tasks.
// Ключовий момент: complete_task на неіснуючий id ловить TaskNotFoundError і повертає
// isError: true з підказкою, а невідомі помилки пропускає нагору через throw.
// Зламана копія (server.buggy.ts) ковтає помилку порожнім catch і рапортує успіх.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { pathToFileURL } from "node:url";
import { z } from "zod";

type Priority = "low" | "medium" | "high";
type Task = { id: string; title: string; priority: Priority; status: "open" | "done" };

// Доменна помилка: id не знайдено. Саме її ловить handler complete_task.
export class TaskNotFoundError extends Error {}

function textResult(payload: unknown) {
  return {
    content: [
      {
        type: "text" as const,
        text: typeof payload === "string" ? payload : JSON.stringify(payload, null, 2),
      },
    ],
  };
}

export function createServer(): McpServer {
  const tasks: Task[] = [{ id: "task-1", title: "Демо-задача", priority: "medium", status: "open" }];
  let seq = 1;

  const server = new McpServer({ name: "task-store", version: "1.0.0" });

  server.registerTool(
    "add_task",
    {
      title: "Add task",
      description: "Додає нову задачу у сховище. Повертає створену задачу з її id.",
      inputSchema: {
        title: z.string().min(1).describe("Назва задачі"),
        priority: z.enum(["low", "medium", "high"]).default("medium").describe("Пріоритет задачі"),
      },
    },
    async ({ title, priority }) => {
      const task: Task = { id: `task-${++seq}`, title, priority, status: "open" };
      tasks.push(task);
      return textResult(task);
    },
  );

  server.registerTool(
    "complete_task",
    {
      title: "Complete task",
      description: "Позначає задачу виконаною за її id.",
      inputSchema: { id: z.string().min(1).describe("Ідентифікатор задачі, напр. task-1") },
    },
    async ({ id }) => {
      try {
        const task = tasks.find((t) => t.id === id);
        if (!task) throw new TaskNotFoundError(id);
        task.status = "done";
        return textResult(task);
      } catch (error) {
        if (error instanceof TaskNotFoundError) {
          return {
            ...textResult(`Задачі з id "${id}" не існує. Виклич list_tasks, щоб побачити актуальні id.`),
            isError: true,
          };
        }
        throw error; // невідомі помилки не маскуємо
      }
    },
  );

  server.registerTool(
    "list_tasks",
    {
      title: "List tasks",
      description: "Повертає список задач. Можна відфільтрувати за статусом.",
      inputSchema: {
        status: z.enum(["open", "done", "all"]).default("all").describe("Фільтр: open, done або all"),
      },
    },
    async ({ status }) => {
      const result = status === "all" ? tasks : tasks.filter((t) => t.status === status);
      if (result.length === 0) return textResult(`Задач зі статусом "${status}" немає.`);
      return textResult(result);
    },
  );

  return server;
}

const isMain =
  process.argv[1] !== undefined &&
  import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMain) {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // stdout належить JSON-RPC: діагностика тільки через stderr.
  console.error("task-store (honest) running on stdio");
}
