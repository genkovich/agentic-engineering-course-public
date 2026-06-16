// 8.7-mcp-inspector buggy server: НАВМИСНО ЗЛАМАНА копія server.ts.
//
// Баг: complete_task на неіснуючий id ковтає TaskNotFoundError ПОРОЖНІМ catch і
// повертає success: true. Зовні сервер виглядає здоровим: tools/list чистий, схеми
// валідні, happy-path працює. Баг видно ТІЛЬКИ на виклику complete_task з фейковим
// id - саме це робимо Inspector-ом.
//
// Не «лагодь» цей файл поза складним рівнем завдання: баг там за сценарієм лекції 8.7
// (у складному рівні ти якраз повертаєш сюди чесний контракт із server.ts).

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { pathToFileURL } from "node:url";
import { z } from "zod";

type Priority = "low" | "medium" | "high";
type Task = { id: string; title: string; priority: Priority; status: "open" | "done" };

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

export function createBuggyServer(): McpServer {
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
      // 🐞 БАГ: порожній catch ковтає TaskNotFoundError, а нижче рапортуємо успіх.
      // Чесна версія (server.ts) повертає isError: true з підказкою.
      try {
        const task = tasks.find((t) => t.id === id);
        if (!task) throw new TaskNotFoundError(id);
        task.status = "done";
      } catch {
        // тихо ігноруємо: задачі немає, але нікому про це не кажемо
      }
      return textResult({ success: true, id });
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
  const server = createBuggyServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("task-store (BUGGY build) running on stdio");
}
