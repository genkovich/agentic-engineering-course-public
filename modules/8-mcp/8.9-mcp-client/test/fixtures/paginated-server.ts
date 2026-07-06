// paginated-server.ts: фікстура великого MCP-сервера, чий tools/list
// віддає каталог СТОРІНКАМИ. Потрібна, щоб показати клієнтський цикл по
// nextCursor (utilities.ts) - на echo-фікстурі з двома tools пагінації не
// видно: усе вміщається в одну сторінку.
//
// 25 tools, розмір сторінки 10 -> три сторінки: 10 + 10 + 5.
//
// Чому кастомний обробник: високорівневий McpServer НЕ пагінує tools/list -
// він завжди віддає весь каталог одним масивом. Тому ми дотягуємось до
// внутрішнього low-level server (`server.server`) і ставимо власний
// обробник tools/list, який ріже список на сторінки за курсором.
//
// Курсор у MCP - непрозорий маркер: клієнт повертає його як є, не парсячи.
// Тут ми кодуємо в нього просто зсув у масиві ("10", "20"), але клієнту
// про це знати не треба - він лише перевіряє, є nextCursor чи ні.
//
// Дві ролі (як у echo-server.ts):
//   1. Імпорт у тестах: createPaginatedServer() + InMemoryTransport.
//   2. Прямий запуск (npx tsx test/fixtures/paginated-server.ts): stdio,
//      щоб utilities.ts мав живий багатосторінковий сервер.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { pathToFileURL } from "node:url";

export const TOTAL_TOOLS = 25;
export const PAGE_SIZE = 10;

// Каталог tools у форматі дроту (JSON Schema, не zod): саме його віддає
// tools/list. Імітуємо великий корпоративний сервер.
const ALL_TOOLS = Array.from({ length: TOTAL_TOOLS }, (_, i) => {
  const n = String(i + 1).padStart(2, "0");
  return {
    name: `report_${n}`,
    description: `Згенерувати звіт №${n} з великого каталогу`,
    inputSchema: { type: "object" as const, properties: {} },
  };
});

export function createPaginatedServer(): McpServer {
  const server = new McpServer({
    name: "paginated-server",
    version: "1.0.0",
  });

  // Оголошуємо tools-capability вручну: без жодного registerTool
  // McpServer не вмикає tools/list, а нам потрібен лише власний обробник.
  server.server.registerCapabilities({ tools: {} });

  // Власний tools/list: ріжемо ALL_TOOLS на сторінки по PAGE_SIZE.
  // request.params.cursor - зсув з минулої відповіді (або undefined на першій).
  server.server.setRequestHandler(ListToolsRequestSchema, (request) => {
    const start = request.params?.cursor ? Number(request.params.cursor) : 0;
    const page = ALL_TOOLS.slice(start, start + PAGE_SIZE);
    const next = start + PAGE_SIZE;

    // nextCursor є тільки якщо попереду ще є tools. Зник nextCursor -
    // список закінчився: саме на цю ознаку дивиться клієнтський цикл.
    return {
      tools: page,
      ...(next < ALL_TOOLS.length ? { nextCursor: String(next) } : {}),
    };
  });

  return server;
}

// Режим 2: прямий запуск -> stdio-сервер.
const isMainModule =
  process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;

if (isMainModule) {
  const server = createPaginatedServer();
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(
    `paginated-server: ${TOTAL_TOOLS} tools, page size ${PAGE_SIZE}, running on stdio`,
  );
}
