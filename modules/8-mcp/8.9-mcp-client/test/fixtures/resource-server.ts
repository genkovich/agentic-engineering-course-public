// resource-server.ts: крихітна фікстура з resources і prompt для тестів
// resources.ts. Self-contained: один text/plain resource, один
// application/json resource і один prompt - саме те, що читає клієнт.
//
// Чому не реальний task-store з 8.6: щоб тест 8.9 лишався герметичним
// (InMemoryTransport, жодних процесів, жодних крос-демо імпортів). Форма
// відповідей - та сама, що у task-store: contents[].mimeType + text,
// messages[] з ролями.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

export function createResourceServer(): McpServer {
  const server = new McpServer({ name: "resource-server", version: "1.0.0" });

  // Фіксований ресурс, text/plain - читається "як є".
  server.registerResource(
    "summary",
    "demo://summary",
    {
      title: "Summary",
      description: "Короткий текстовий підсумок",
      mimeType: "text/plain",
    },
    async (uri) => ({
      contents: [
        { uri: uri.href, mimeType: "text/plain", text: "Відкритих задач: 2" },
      ],
    }),
  );

  // Фіксований ресурс, application/json - читається з парсингом.
  server.registerResource(
    "item",
    "demo://item/1",
    {
      title: "Item 1",
      description: "Один елемент у JSON",
      mimeType: "application/json",
    },
    async (uri) => ({
      contents: [
        {
          uri: uri.href,
          mimeType: "application/json",
          text: JSON.stringify({ id: 1, title: "Демо", priority: "high" }),
        },
      ],
    }),
  );

  // Prompt: сервер сам збирає готовий масив messages.
  server.registerPrompt(
    "greet",
    {
      title: "Greet",
      description: "Збирає привітання за іменем",
      argsSchema: { name: z.string().describe("Кого вітати") },
    },
    ({ name }) => ({
      messages: [
        {
          role: "user" as const,
          content: { type: "text" as const, text: `Привітайся з ${name}.` },
        },
      ],
    }),
  );

  return server;
}
