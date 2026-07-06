// slow-server.ts: фікстура з одним навмисно повільним tool.
// Потрібна, щоб показати таймаут і скасування запиту (utilities.ts):
// echo і add повертаються миттєво, на них таймаут не спрацює.
//
// Один tool:
//   slow(ms?)  чекає ms мілісекунд (за замовчуванням 2000) і відповідає.
//
// Дві ролі (як у echo-server.ts):
//   1. Імпорт у тестах: createSlowServer() + InMemoryTransport.
//   2. Прямий запуск (npx tsx test/fixtures/slow-server.ts): stdio,
//      щоб utilities.ts мав живий повільний сервер.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { pathToFileURL } from "node:url";
import { z } from "zod";

export function createSlowServer(): McpServer {
  const server = new McpServer({ name: "slow-server", version: "1.0.0" });

  server.registerTool(
    "slow",
    {
      description: "Чекає задану кількість мілісекунд, потім відповідає",
      inputSchema: {
        ms: z
          .number()
          .default(2000)
          .describe("Скільки мілісекунд 'працювати' перед відповіддю"),
      },
    },
    async ({ ms }) => {
      await new Promise((resolve) => setTimeout(resolve, ms));
      return { content: [{ type: "text", text: `Готово за ${ms}ms` }] };
    },
  );

  return server;
}

// Режим 2: файл запущено напряму, стаємо stdio-сервером.
const isMainModule =
  process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMainModule) {
  const server = createSlowServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("slow-server: running on stdio");
}
