// 8.2-mcp-primitives: крихітний READ-ONLY сервер, щоб ПОБАЧИТИ три примітиви MCP
// (tool / resource / prompt) у Inspector ще до того, як будувати власний сервер у 8.6.
//
// Кожен примітив тут - найпростіший представник своєї моделі контролю:
//   - word_count        TOOL     model-controlled: модель сама вирішує викликати
//   - primitives://...   RESOURCE app-controlled:  дані за URI, які читає додаток
//   - explain-primitive  PROMPT   user-controlled:  шаблон, який запускає людина
//
// Сервер нічого не змінює: жодного стану, жодного запису. Будувати повноцінний
// сервер з логікою і тестами - матеріал 8.6, не цього уроку.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { pathToFileURL } from "node:url";
import { z } from "zod";

const CHEATSHEET = [
  "Три примітиви MCP - три моделі контролю:",
  "- Tools     model-controlled: модель сама вирішує, коли викликати функцію.",
  "- Resources app-controlled:   дані за URI, які підкладає у контекст додаток.",
  "- Prompts   user-controlled:   готові шаблони, які запускає людина.",
].join("\n");

export function createServer(): McpServer {
  const server = new McpServer({ name: "primitives-demo", version: "1.0.0" });

  // ─── TOOL (model-controlled) ───
  // Чиста read-only функція: рахує слова. Модель сама вирішує, коли її викликати.
  server.registerTool(
    "word_count",
    {
      title: "Word count",
      description: "Рахує кількість слів у тексті. Read-only, нічого не змінює.",
      inputSchema: {
        text: z.string().describe("Текст, у якому рахуємо слова"),
      },
    },
    async ({ text }) => ({
      content: [
        {
          type: "text",
          text: String(text.trim().split(/\s+/).filter(Boolean).length),
        },
      ],
    }),
  );

  // ─── RESOURCE (app-controlled) ───
  // Статичні дані за вигаданою URI-схемою primitives://. Їх читають, а не викликають.
  server.registerResource(
    "cheatsheet",
    "primitives://cheatsheet",
    {
      title: "Primitives cheatsheet",
      description: "Шпаргалка: три примітиви і три моделі контролю.",
      mimeType: "text/plain",
    },
    async (uri) => ({
      contents: [{ uri: uri.href, mimeType: "text/plain", text: CHEATSHEET }],
    }),
  );

  // ─── PROMPT (user-controlled) ───
  // Шаблон з одним аргументом. Handler нічого не виконує - лише будує messages[].
  server.registerPrompt(
    "explain-primitive",
    {
      title: "Explain a primitive",
      description: "Готовий шаблон: поясни один з примітивів MCP простими словами.",
      argsSchema: {
        name: z.string().describe("Назва примітиву: tool, resource або prompt"),
      },
    },
    ({ name }) => ({
      messages: [
        {
          role: "user" as const,
          content: {
            type: "text" as const,
            text: `Поясни простими словами, що таке MCP-примітив "${name}" і хто вирішує, коли його використати.`,
          },
        },
      ],
    }),
  );

  return server;
}

// Запуск як окремого процесу: stdio-транспорт. Guard - щоб імпорт не піднімав сервер.
const isMain =
  process.argv[1] !== undefined &&
  import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMain) {
  const server = createServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // console.log заборонено: stdout зайнятий JSON-RPC. Діагностика - у stderr.
  console.error("primitives-demo MCP server running on stdio");
}
