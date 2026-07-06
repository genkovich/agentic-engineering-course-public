// Тести дзеркальних дієслів resources/prompts проти герметичної фікстури.
// InMemoryTransport: клієнт і сервер в одному процесі, без API-ключа.

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createResourceServer } from "./fixtures/resource-server.js";

describe("resources and prompts from the client side", () => {
  let client: Client;
  let server: McpServer;

  beforeEach(async () => {
    server = createResourceServer();
    client = new Client({ name: "resources-test", version: "1.0.0" });
    const [ct, st] = InMemoryTransport.createLinkedPair();
    await Promise.all([server.connect(st), client.connect(ct)]);
  });

  afterEach(async () => {
    await client.close();
    await server.close();
  });

  it("lists resources with their mimeType", async () => {
    const { resources } = await client.listResources();
    const byUri = Object.fromEntries(resources.map((r) => [r.uri, r.mimeType]));

    expect(byUri["demo://summary"]).toBe("text/plain");
    expect(byUri["demo://item/1"]).toBe("application/json");
  });

  it("reads a text/plain resource as-is", async () => {
    const result = await client.readResource({ uri: "demo://summary" });

    expect(result.contents[0].mimeType).toBe("text/plain");
    expect(result.contents[0].text).toBe("Відкритих задач: 2");
  });

  it("reads an application/json resource and parses it", async () => {
    const result = await client.readResource({ uri: "demo://item/1" });

    expect(result.contents[0].mimeType).toBe("application/json");
    const data = JSON.parse(result.contents[0].text as string);
    expect(data).toEqual({ id: 1, title: "Демо", priority: "high" });
  });

  it("lists prompts with their arguments", async () => {
    const { prompts } = await client.listPrompts();

    const greet = prompts.find((p) => p.name === "greet");
    expect(greet).toBeDefined();
    expect(greet?.arguments?.map((a) => a.name)).toEqual(["name"]);
  });

  it("gets a prompt as ready-to-send messages", async () => {
    const result = await client.getPrompt({
      name: "greet",
      arguments: { name: "Світ" },
    });

    expect(result.messages).toHaveLength(1);
    expect(result.messages[0].role).toBe("user");
    // Сервер уже зібрав текст - клієнт шле його у Messages API без трансформації.
    expect(result.messages[0].content).toMatchObject({
      type: "text",
      text: "Привітайся з Світ.",
    });
  });
});
