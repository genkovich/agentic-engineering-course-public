// server.ts: MCP-шар поверх TaskStore.
// Один сервер, три примітиви протоколу:
//   - Tools (add_task, complete_task, list_tasks) - дії, які модель викликає сама
//   - Resource (tasks://summary) - дані, які додаток підкладає у контекст
//   - Prompt (plan-day) - готовий шаблон, який юзер обирає явно

import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { ServerOptions } from "@modelcontextprotocol/sdk/server/index.js";
import { completable } from "@modelcontextprotocol/sdk/server/completable.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { fileURLToPath, pathToFileURL } from "node:url";
import { z } from "zod";
import { TaskStore, TaskNotFoundError, type Task } from "./store.js";

// Persistence-файл лежить поруч з проектом: data/tasks.json.
// Шлях рахуємо від поточного модуля, а не від cwd:
// MCP-клієнт може запустити сервер з будь-якої директорії.
const DATA_FILE = fileURLToPath(new URL("../data/tasks.json", import.meta.url));

// Хелпер: усі tool-результати у MCP мають форму { content: [...] }.
// Найпростіший тип контенту - text.
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

// Фабрика сервера приймає store ззовні (dependency injection).
// Завдяки цьому тести підкладають in-memory store без файлу на диску.
// options - необов'язковий: надбудовам (лекція 8.10, server-advanced.ts) він дає
// оголосити додаткові server-capabilities (наприклад logging) уже при конструюванні,
// і тоді SDK сам реєструє відповідні обробники. Для 8.6 options не передають.
export function createServer(store: TaskStore, options?: ServerOptions): McpServer {
  const server = new McpServer(
    {
      name: "task-store",
      version: "1.0.0",
    },
    options,
  );

  // ─── TOOL 1: add_task ───
  // inputSchema це об'єкт zod-схем. SDK сам:
  //   1) конвертує його у JSON Schema для tools/list
  //   2) валідує вхідні аргументи перед викликом handler-а
  // Тобто у handler title і priority вже гарантовано правильних типів.
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

  // ─── TOOL 2: complete_task ───
  // Ключовий момент демо: error handling.
  // Неіснуючий id це НЕ криза і НЕ криваво-червоний exception у клієнта.
  // Повертаємо isError: true з зрозумілим текстом,
  // і модель сама вирішить що робити далі (наприклад, перепитати список).
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
      try {
        const task = store.completeTask(id);
        return textResult(task);
      } catch (error) {
        if (error instanceof TaskNotFoundError) {
          return {
            ...textResult(
              `Задачі з id "${id}" не існує. Виклич list_tasks, щоб побачити актуальні id.`,
            ),
            isError: true,
          };
        }
        throw error; // невідомі помилки не маскуємо
      }
    },
  );

  // ─── TOOL 3: list_tasks ───
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

  // ─── RESOURCE: tasks://summary ───
  // Resource це READ-канал: модель (або юзер через @-mention)
  // читає дані, але нічого не змінює. URI-схему вигадуємо самі.
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

  // ─── RESOURCE TEMPLATE: tasks://task/{id} ─── (лекція 8.11)
  // Один шаблон за RFC 6570 обслуговує всі задачі одразу.
  // list callback робить шаблон каталогом: клієнт бачить живий список
  // конкретних задач у resources/list. complete-callback для {id}
  // відповідає на completion/complete - підказує id під час введення.
  server.registerResource(
    "task",
    new ResourceTemplate("tasks://task/{id}", {
      list: () => ({
        resources: store.listTasks("all").map((task) => ({
          uri: `tasks://task/${task.id}`,
          name: task.title,
          description: `[${task.priority}] ${task.status}`,
          mimeType: "application/json",
        })),
      }),
      complete: {
        id: (value) =>
          store
            .listTasks("all")
            .map((task) => task.id)
            .filter((id) => id.startsWith(value)),
      },
    }),
    {
      title: "Task by id",
      description: "Одна задача за її id у форматі JSON.",
      mimeType: "application/json",
    },
    async (uri, variables) => {
      const id = String(variables.id);
      const task = store.listTasks("all").find((item) => item.id === id);
      if (!task) {
        throw new Error(`Задачі з id "${id}" не існує.`);
      }
      return {
        contents: [
          {
            uri: uri.href,
            mimeType: "application/json",
            text: JSON.stringify(task, null, 2),
          },
        ],
      };
    },
  );

  // ─── PROMPT: plan-day ───
  // Prompt це шаблон, який юзер викликає явно (у Claude Code це /mcp__... команда).
  // Сервер сам підставляє у текст актуальні відкриті задачі,
  // тож модель одразу отримує і інструкцію, і дані.
  server.registerPrompt(
    "plan-day",
    {
      title: "Plan the day",
      description: "Складає план дня з відкритих задач, з урахуванням фокусу.",
      argsSchema: {
        focus: z.string().describe("Головний фокус дня, наприклад 'код-рев'ю'"),
        // completable() (лекція 8.11): навішує на аргумент complete-callback.
        // Клієнт шле completion/complete з тим, що юзер уже набрав,
        // сервер повертає підказки: "hi" -> ["high"].
        priority: completable(
          z
            .string()
            .optional()
            .describe("Опціональний фільтр пріоритету: low, medium або high"),
          (value) =>
            ["low", "medium", "high"].filter((p) => p.startsWith(value ?? "")),
        ),
      },
    },
    ({ focus, priority }) => {
      const open = store
        .listTasks("open")
        .filter((task) => !priority || task.priority === priority);
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

// Запуск як окремого процесу: підключаємо stdio-транспорт.
// Guard потрібен, щоб тести могли імпортувати createServer
// без побічного ефекту "сервер раптом слухає stdin".
const isMain =
  process.argv[1] !== undefined &&
  import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMain) {
  const store = new TaskStore(DATA_FILE);
  store.load();

  const server = createServer(store);
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // ВАЖЛИВО: console.log тут заборонений.
  // stdout зайнятий JSON-RPC повідомленнями протоколу,
  // будь-який зайвий рядок у stdout ламає парсер клієнта.
  // Для діагностики використовуємо stderr.
  console.error("task-store MCP server running on stdio");
}
