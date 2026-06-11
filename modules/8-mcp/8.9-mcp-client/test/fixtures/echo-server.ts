// echo-server.ts: крихітний MCP-сервер для тестів і смоук-демо.
//
// Два tools:
//   echo(message)  повертає "Echo: <message>"
//   add(a, b)      повертає суму чисел
//
// Файл працює у двох режимах:
//   1. Імпорт у тестах: createEchoServer() + InMemoryTransport,
//      жодних процесів і мережі, усе в одному процесі vitest.
//   2. Прямий запуск (npx tsx test/fixtures/echo-server.ts):
//      піднімає stdio-транспорт, щоб приклади 01 і 02 мали
//      живий сервер без зовнішніх залежностей.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { pathToFileURL } from "node:url";
import { z } from "zod";

export function createEchoServer(): McpServer {
  const server = new McpServer({ name: "echo-server", version: "1.0.0" });

  server.registerTool(
    "echo",
    {
      description: "Echoes the message back",
      inputSchema: { message: z.string().describe("Text to echo back") },
    },
    async ({ message }) => ({
      content: [{ type: "text", text: `Echo: ${message}` }],
    }),
  );

  server.registerTool(
    "add",
    {
      description: "Adds two numbers",
      inputSchema: {
        a: z.number().describe("First number"),
        b: z.number().describe("Second number"),
      },
    },
    async ({ a, b }) => ({
      content: [{ type: "text", text: String(a + b) }],
    }),
  );

  return server;
}

// Режим 2: файл запущено напряму, стаємо stdio-сервером.
const isMainModule =
  process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMainModule) {
  const server = createEchoServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // console.log тут заборонено: stdout зайнятий JSON-RPC повідомленнями.
  console.error("echo-server: running on stdio");
}
