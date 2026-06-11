// Тести MCP-клієнта проти fixture-сервера через InMemoryTransport.
// Без зовнішніх процесів: клієнт і сервер живуть в одному процесі
// і з'єднані парою зв'язаних транспортів.

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createEchoServer } from "./fixtures/echo-server.js";

describe("MCP client against echo-server", () => {
  let client: Client;
  let server: McpServer;

  beforeEach(async () => {
    server = createEchoServer();
    client = new Client({ name: "test-client", version: "1.0.0" });

    // Пара зв'язаних транспортів: що пишеться в один, читається з іншого.
    const [clientTransport, serverTransport] =
      InMemoryTransport.createLinkedPair();

    await Promise.all([
      server.connect(serverTransport),
      client.connect(clientTransport),
    ]);
  });

  afterEach(async () => {
    await client.close();
    await server.close();
  });

  it("sees both tools via listTools", async () => {
    const { tools } = await client.listTools();

    const names = tools.map((t) => t.name).sort();
    expect(names).toEqual(["add", "echo"]);

    const echo = tools.find((t) => t.name === "echo");
    expect(echo?.description).toBe("Echoes the message back");
    expect(echo?.inputSchema.type).toBe("object");
    expect(echo?.inputSchema.properties).toHaveProperty("message");
  });

  it("calls echo tool and receives the result", async () => {
    const result = await client.callTool({
      name: "echo",
      arguments: { message: "привіт" },
    });

    expect(result.isError).toBeFalsy();
    expect(result.content).toEqual([{ type: "text", text: "Echo: привіт" }]);
  });

  it("calls add tool with numeric arguments", async () => {
    const result = await client.callTool({
      name: "add",
      arguments: { a: 21, b: 21 },
    });

    expect(result.content).toEqual([{ type: "text", text: "42" }]);
  });
});
