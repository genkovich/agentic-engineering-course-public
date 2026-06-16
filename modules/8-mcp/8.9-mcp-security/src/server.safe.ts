// 8.9-mcp-security safe server: чистий двійник отруєного.
//
// Той самий інструмент add, але опис чесний і короткий, без прихованих інструкцій,
// і без параметра note (каналу ексфільтрації). Тримай поруч з отруєним: у
// tools/list різниця в описах кидається у вічі - саме її шукаєш під час аудиту.

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { pathToFileURL } from "node:url";
import { z } from "zod";

export function createServer(): McpServer {
  const server = new McpServer({ name: "calc-safe", version: "1.0.0" });

  server.registerTool(
    "add",
    {
      title: "Add two numbers",
      description: "Додає два числа і повертає їхню суму.",
      inputSchema: {
        a: z.number().describe("Перше число"),
        b: z.number().describe("Друге число"),
      },
    },
    async ({ a, b }) => ({
      content: [{ type: "text", text: String(a + b) }],
    }),
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
  console.error("calc-safe MCP server running on stdio");
}
