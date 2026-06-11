// server.buggy.ts: НАВМИСНО ЗЛАМАНА копія server.ts для лекції 8.7 (MCP Inspector).
//
// Баг: tool complete_task тихо ігнорує неіснуючий id
// і повертає success: true, ніби все добре.
// Зовні сервер виглядає здоровим: tools/list чистий, схеми валідні.
// Баг видно тільки коли викликаєш complete_task з фейковим id
// і дивишся на відповідь. Саме це робимо Inspector-ом у лекції 8.7.
//
// Тести цей файл НЕ покривають. Він зламаний навмисно.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { fileURLToPath, pathToFileURL } from "node:url";
import { z } from "zod";
import { TaskStore, type Task } from "./store.js";

const DATA_FILE = fileURLToPath(new URL("../data/tasks.json", import.meta.url));

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

export function createBuggyServer(store: TaskStore): McpServer {
  const server = new McpServer({
    name: "task-store",
    version: "1.0.0",
  });

  server.registerTool(
    "add_task",
    {
      title: "Add task",
      description: "Додає нову задачу у сховище. Повертає створену задачу з її id.",
      inputSchema: {
        title: z.string().min(1).describe("Назва задачі"),
        priority: z
          .enum(["low", "medium", "high"])
          .default("medium")
          .describe("Пріоритет задачі"),
      },
    },
    async ({ title, priority }) => {
      const task = store.addTask(title, priority);
      return textResult(task);
    },
  );

  server.registerTool(
    "complete_task",
    {
      title: "Complete task",
      description: "Позначає задачу виконаною за її id.",
      inputSchema: {
        id: z.string().min(1).describe("Ідентифікатор задачі, наприклад task-1"),
      },
    },
    async ({ id }) => {
      // 🐞 БАГ: ковтаємо TaskNotFoundError і рапортуємо успіх.
      // Правильна версія (див. server.ts) повертає isError: true
      // з поясненням, що такого id немає.
      try {
        store.completeTask(id);
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
        status: z
          .enum(["open", "done", "all"])
          .default("all")
          .describe("Фільтр: open, done або all"),
      },
    },
    async ({ status }) => {
      const tasks = store.listTasks(status);
      if (tasks.length === 0) {
        return textResult(`Задач зі статусом "${status}" немає.`);
      }
      return textResult(tasks);
    },
  );

  server.registerResource(
    "summary",
    "tasks://summary",
    {
      title: "Tasks summary",
      description: "Текстовий підсумок: скільки відкритих і закритих задач.",
      mimeType: "text/plain",
    },
    async (uri) => {
      const { open, done, oldestOpen } = store.summary();
      const lines = [
        `Відкритих задач: ${open}`,
        `Закритих задач: ${done}`,
      ];
      if (oldestOpen) {
        lines.push(
          `Найстаріша відкрита: ${oldestOpen.title} (${oldestOpen.id}, створена ${oldestOpen.createdAt})`,
        );
      }
      return {
        contents: [
          {
            uri: uri.href,
            mimeType: "text/plain",
            text: lines.join("\n"),
          },
        ],
      };
    },
  );

  server.registerPrompt(
    "plan-day",
    {
      title: "Plan the day",
      description: "Складає план дня з відкритих задач, з урахуванням фокусу.",
      argsSchema: {
        focus: z.string().describe("Головний фокус дня, наприклад 'код-рев'ю'"),
      },
    },
    ({ focus }) => {
      const open = store.listTasks("open");
      const taskList =
        open.length > 0
          ? open
              .map((task: Task) => `- [${task.priority}] ${task.title} (${task.id})`)
              .join("\n")
          : "- (відкритих задач немає)";
      return {
        messages: [
          {
            role: "user" as const,
            content: {
              type: "text" as const,
              text: [
                `Сплануй мій день. Головний фокус: ${focus}.`,
                "",
                "Мої відкриті задачі:",
                taskList,
                "",
                "Розстав їх у порядку виконання, врахуй пріоритети.",
                "Задачі, які не стосуються фокусу, запропонуй перенести.",
              ].join("\n"),
            },
          },
        ],
      };
    },
  );

  return server;
}

const isMain =
  process.argv[1] !== undefined &&
  import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMain) {
  const store = new TaskStore(DATA_FILE);
  store.load();

  const server = createBuggyServer(store);
  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error("task-store MCP server (BUGGY build) running on stdio");
}
