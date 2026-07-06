// server-advanced.ts: верхній поверх протоколу поверх task-store з 8.6 (лекція 8.10).
// Базовий сервер - той самий createServer з server.ts (3 tools + resource + prompt).
// Тут НЕ дублюємо нічого: беремо готовий McpServer і реєструємо поверх нього
// чотири tools, кожен демонструє одну client feature - можливість, де ролі
// міняються і вже сервер щось просить у клієнта:
//   - summarize_tasks   → sampling     (server.createMessage)   [депрекований SEP-2577]
//   - export_tasks      → roots        (server.listRoots)       [депрекований SEP-2577]
//   - add_task_guided   → elicitation  (server.elicitInput)     [лишається]
//   - reprioritize_all  → progress + logging notifications      [лишається]
//
// Це клієнтські capabilities, тож наш сервер їх лише ВИКЛИКАЄ. Відповідає на них
// клієнт - тому ПОВНИЙ демо живе у MCP Inspector (його UI дає форму, вкладку
// Sampling, конфіг Roots, панель Notifications). Сервер ставиться і в Claude Code
// (`claude mcp add task-store-adv -- node dist/server-advanced.js`): там наживо
// працюють elicitation і progress (ті, що лишаються), а sampling і roots грейсфул-
// дегрейдять у isError, бо Claude Code їх не підтримує. У CLI безпечний лише
// tools/list - відповісти на sampling/elicit CLI не вміє, це робота UI-клієнта.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { fileURLToPath, pathToFileURL } from "node:url";
import { z } from "zod";
import { createServer } from "./server.js";
import { TaskStore } from "./store.js";

const DATA_FILE = fileURLToPath(new URL("../data/tasks.json", import.meta.url));

// Той самий хелпер форми { content: [...] }, що у server.ts.
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

// Патерн isPathAllowed: roots - це розмітка на дорозі, а не паркан.
// Протокол не змушує сервер поважати корені (формулювання SHOULD), тому
// добропорядний сервер сам перевіряє, що пише в межах хоча б одного root.
function isPathAllowed(targetUri: string, roots: { uri: string }[]): boolean {
  return roots.some((root) => targetUri.startsWith(root.uri.replace(/\/$/, "")));
}

// Фабрика advanced-сервера: бере базовий сервер з 8.6 і добудовує 4 tools поверх.
// Підсумок: 7 tools (3 базові + 4 advanced), той самий resource і prompt.
export function createAdvancedServer(store: TaskStore): McpServer {
  // logging оголошуємо одразу при конструюванні (через options createServer):
  // тоді SDK сам реєструє обробник logging/setLevel, і sendLoggingMessage реально
  // шле нотифікації клієнту. (sampling/elicitation/roots оголошує КЛІЄНТ, тому їх
  // тут не реєструємо - сервер лише шле запити, а клієнт вирішує, чи вміє відповісти.)
  const server = createServer(store, { capabilities: { logging: {} } });

  // ─── TOOL 4: summarize_tasks ─── client feature: SAMPLING (депрекований) ───
  // Той самий приклад, що лекція згадує гіпотетично: підсумувати відкриті задачі
  // людською мовою. Без sampling серверу довелося б нести власний API-ключ;
  // з sampling він каже клієнту "згенеруй мені оце", а модель і білінг лишаються
  // у клієнта, людина бачить кожен запит.
  server.registerTool(
    "summarize_tasks",
    {
      title: "Summarize tasks (sampling)",
      description:
        "Просить клієнта згенерувати людський підсумок відкритих задач через sampling. " +
        "Демонструє client feature sampling: сервер позичає модель у клієнта без власного ключа.",
      inputSchema: {},
    },
    async () => {
      const open = store.listTasks("open");
      if (open.length === 0) {
        return textResult("Відкритих задач немає - нема чого підсумовувати.");
      }
      const taskLines = open
        .map((task) => `- [${task.priority}] ${task.title} (${task.id})`)
        .join("\n");
      try {
        // createMessage шле клієнту sampling/createMessage. Клієнт показує запит
        // людині, після схвалення викликає свою модель і повертає відповідь.
        const result = await server.server.createMessage({
          messages: [
            {
              role: "user",
              content: {
                type: "text",
                text:
                  `Ось мої відкриті задачі:\n${taskLines}\n\n` +
                  "Напиши короткий людський підсумок: де фокус, що горить, з чого почати.",
              },
            },
          ],
          systemPrompt:
            "Ти лаконічний асистент із планування. Відповідай 2-3 реченнями українською.",
          maxTokens: 300,
        });
        const summary =
          result.content.type === "text"
            ? result.content.text
            : "(клієнт повернув не-текстову відповідь)";
        return textResult(summary);
      } catch (error) {
        // Найімовірніша помилка - клієнт не оголосив capability sampling:
        // SDK відповідає -32601 (Method not found), той самий capability-mismatch.
        // Це НЕ криза: повертаємо isError з поясненням, що робити далі.
        return {
          ...textResult(
            [
              "Клієнт не підтримує sampling, тому згенерувати підсумок моделлю не вийшло.",
              "У MCP Inspector відкрий вкладку Sampling - там можна відповісти на запит вручну.",
              `Деталі: ${error instanceof Error ? error.message : String(error)}`,
            ].join("\n"),
          ),
          isError: true,
        };
      }
    },
  );

  // ─── TOOL 5: export_tasks ─── client feature: ROOTS (депрекований) ───
  // Питає у клієнта оголошені корені через roots/list і показує, КУДИ б експортував
  // задачі: <root>/tasks.md. Заодно демонструє патерн isPathAllowed - сервер сам
  // тримається в межах коренів, бо протокол його до цього не змушує.
  server.registerTool(
    "export_tasks",
    {
      title: "Export tasks (roots)",
      description:
        "Питає у клієнта оголошені корені (roots) і показує цільовий шлях експорту. " +
        "Демонструє client feature roots: клієнт повідомляє серверу межі робочої зони.",
      inputSchema: {},
    },
    async () => {
      let roots: { uri: string; name?: string }[];
      try {
        roots = (await server.server.listRoots()).roots;
      } catch (error) {
        return {
          ...textResult(
            [
              "Клієнт не оголосив capability roots, тому невідомо, у якій директорії працювати.",
              "У MCP Inspector додай Root у конфізі клієнта - і виклич tool ще раз.",
              `Деталі: ${error instanceof Error ? error.message : String(error)}`,
            ].join("\n"),
          ),
          isError: true,
        };
      }
      if (roots.length === 0) {
        return textResult(
          "Клієнт не оголосив жодного root. Додай директорію у конфізі клієнта і повтори виклик.",
        );
      }
      // Перший file:// корінь - ціль експорту.
      const target = roots.find((root) => root.uri.startsWith("file://")) ?? roots[0];
      const targetPath = `${target.uri.replace(/\/$/, "")}/tasks.md`;
      const allowed = isPathAllowed(targetPath, roots);
      const total = store.listTasks("all").length;
      return textResult(
        [
          `Клієнт оголосив ${roots.length} root(s):`,
          ...roots.map((root) => `  - ${root.name ?? "(без назви)"}: ${root.uri}`),
          "",
          `Експортував би ${total} задач(і) у: ${targetPath}`,
          `Перевірка меж (isPathAllowed): ${allowed ? "у межах roots ✓" : "поза roots ✗"}`,
          "",
          "Нагадування: roots - це розмітка на дорозі, а не паркан. Справжню ізоляцію",
          "дають права файлової системи і пісочниця ОС, а не ввічливість сервера.",
        ].join("\n"),
      );
    },
  );

  // ─── TOOL 6: add_task_guided ─── client feature: ELICITATION (лишається) ───
  // Додає задачу. Якщо priority не передали - сервер посеред операції розуміє, що
  // йому бракує даних, і питає їх формою через elicitation/create. Обробляє всі
  // три результати протоколу: accept, decline, cancel.
  server.registerTool(
    "add_task_guided",
    {
      title: "Add task with elicitation",
      description:
        "Додає задачу. Якщо не вказано priority - питає його у користувача формою (elicitation). " +
        "Демонструє client feature elicitation: сервер питає живу людину посеред операції.",
      inputSchema: {
        title: z.string().min(1).describe("Назва задачі"),
        priority: z
          .enum(["low", "medium", "high"])
          .optional()
          .describe("Пріоритет; якщо не вказати - сервер запитає його формою"),
      },
    },
    async ({ title, priority }) => {
      let chosen = priority;
      if (!chosen) {
        let result;
        try {
          // elicitInput шле elicitation/create: message (людське пояснення) +
          // requestedSchema (плаский об'єкт примітивних полів). Клієнт малює форму.
          result = await server.server.elicitInput({
            message: `Який пріоритет у задачі "${title}"?`,
            requestedSchema: {
              type: "object",
              properties: {
                priority: {
                  type: "string",
                  title: "Пріоритет",
                  description: "Оберіть пріоритет задачі",
                  enum: ["low", "medium", "high"],
                },
              },
              required: ["priority"],
            },
          });
        } catch (error) {
          return {
            ...textResult(
              [
                "Клієнт не підтримує elicitation, тому запитати пріоритет формою не вийшло.",
                "У MCP Inspector цей запит з'явиться як інтерактивна форма.",
                `Деталі: ${error instanceof Error ? error.message : String(error)}`,
              ].join("\n"),
            ),
            isError: true,
          };
        }
        // Три гілки протоколу - кожну обробляємо явно.
        if (result.action === "decline") {
          return textResult("Користувач відмовився вказати пріоритет. Задачу не створено.");
        }
        if (result.action === "cancel") {
          return textResult("Користувач закрив форму. Задачу не створено.");
        }
        const value = result.content?.priority;
        if (value !== "low" && value !== "medium" && value !== "high") {
          return {
            ...textResult(`Форма повернула неочікуваний пріоритет: ${String(value)}.`),
            isError: true,
          };
        }
        chosen = value;
      }
      const task = store.addTask(title, chosen);
      return textResult(task);
    },
  );

  // ─── TOOL 7: reprioritize_all ─── NOTIFICATIONS: progress + logging (лишається) ─
  // Проходить усі відкриті задачі і звітує про просування покроково:
  // notifications/progress (скільки кроків зі скількох) + log-повідомлення.
  // З'єднання перестає бути тишею до результату - довгий виклик розповідає про себе.
  server.registerTool(
    "reprioritize_all",
    {
      title: "Reprioritize all (progress + logging)",
      description:
        "Проходить усі відкриті задачі і звітує прогрес покроково через notifications/progress " +
        "та log-повідомлення. Демонструє нотифікації: з'єднання розповідає про себе по дорозі.",
      inputSchema: {},
    },
    async (_args, extra) => {
      const open = store.listTasks("open");
      if (open.length === 0) {
        return textResult("Відкритих задач немає - нема що переоцінювати.");
      }
      // progressToken приходить у _meta запиту, якщо клієнт хоче progress-звіти.
      const progressToken = extra._meta?.progressToken;
      await server.server.sendLoggingMessage({
        level: "info",
        data: `reprioritize_all: почав обробку ${open.length} задач(і)`,
      });
      let step = 0;
      for (const task of open) {
        step += 1;
        await sleep(400); // штучна пауза, щоб прогрес був видимий покроково в UI
        await server.server.sendLoggingMessage({
          level: "debug",
          data: `Оцінюю задачу ${task.id} (${task.priority})`,
        });
        if (progressToken !== undefined) {
          // notifications/progress: той самий progressToken, що прийшов у запиті.
          await extra.sendNotification({
            method: "notifications/progress",
            params: {
              progressToken,
              progress: step,
              total: open.length,
              message: `Оброблено ${step}/${open.length}: ${task.title}`,
            },
          });
        }
      }
      await server.server.sendLoggingMessage({
        level: "info",
        data: "reprioritize_all: готово",
      });
      return textResult(
        `Пройдено ${open.length} відкритих задач, прогрес відзвітовано покроково.`,
      );
    },
  );

  return server;
}

// Невелика пауза для видимого прогресу в Inspector.
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Запуск як окремого процесу на stdio - той самий guard, що у server.ts:
// дозволяє тестам імпортувати createAdvancedServer без побічного ефекту.
const isMain =
  process.argv[1] !== undefined &&
  import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMain) {
  const store = new TaskStore(DATA_FILE);
  store.load();

  const server = createAdvancedServer(store);
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // stdout зайнятий JSON-RPC: діагностика тільки у stderr.
  console.error("task-store advanced MCP server running on stdio (7 tools)");
}
