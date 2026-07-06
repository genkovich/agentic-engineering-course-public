// Тести службового шару протоколу: ping, таймаут/cancellation, pagination.
// InMemoryTransport, без API-ключа і зовнішніх процесів.

import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createSlowServer } from "./fixtures/slow-server.js";
import {
  createPaginatedServer,
  TOTAL_TOOLS,
  PAGE_SIZE,
} from "./fixtures/paginated-server.js";

describe("ping", () => {
  it("resolves while the connection is alive", async () => {
    const server = createSlowServer();
    const client = new Client({ name: "ping-test", version: "1.0.0" });
    const [ct, st] = InMemoryTransport.createLinkedPair();
    await Promise.all([server.connect(st), client.connect(ct)]);

    // ping не повертає даних - сам факт резолву означає "з'єднання живе".
    await expect(client.ping()).resolves.toBeDefined();

    await client.close();
    await server.close();
  });
});

describe("timeout and cancellation", () => {
  let client: Client;
  let server: McpServer;

  beforeEach(async () => {
    server = createSlowServer();
    client = new Client({ name: "timeout-test", version: "1.0.0" });
    const [ct, st] = InMemoryTransport.createLinkedPair();
    await Promise.all([server.connect(st), client.connect(ct)]);
  });

  afterEach(async () => {
    await client.close();
    await server.close();
  });

  it("rejects with RequestTimeout when the tool is slower than the timeout", async () => {
    // slow(500ms) проти таймауту 50ms -> RequestTimeout.
    // SDK у цей момент шле серверу notifications/cancelled.
    const call = client.callTool(
      { name: "slow", arguments: { ms: 500 } },
      undefined,
      { timeout: 50 },
    );

    await expect(call).rejects.toBeInstanceOf(McpError);
    await call.catch((error: McpError) => {
      expect(error.code).toBe(ErrorCode.RequestTimeout);
    });
  });

  it("succeeds when the timeout is raised above the tool duration", async () => {
    // Той самий tool, але таймаут більший за тривалість -> успіх.
    const result = await client.callTool(
      { name: "slow", arguments: { ms: 20 } },
      undefined,
      { timeout: 2000 },
    );

    const text = (result.content as Array<{ text?: string }>)
      .map((b) => b.text ?? "")
      .join("");
    expect(text).toContain("Готово");
  });
});

describe("pagination", () => {
  it("collects every tool by following nextCursor to the end", async () => {
    const server = createPaginatedServer();
    const client = new Client({ name: "pagination-test", version: "1.0.0" });
    const [ct, st] = InMemoryTransport.createLinkedPair();
    await Promise.all([server.connect(st), client.connect(ct)]);

    const all: string[] = [];
    const pageSizes: number[] = [];
    let cursor: string | undefined;

    do {
      const result = await client.listTools(cursor ? { cursor } : undefined);
      pageSizes.push(result.tools.length);
      all.push(...result.tools.map((t) => t.name));
      cursor = result.nextCursor;
    } while (cursor);

    // Усі 25 tools зібрані за три сторінки 10 + 10 + 5.
    expect(all).toHaveLength(TOTAL_TOOLS);
    expect(new Set(all).size).toBe(TOTAL_TOOLS);
    expect(pageSizes).toEqual([PAGE_SIZE, PAGE_SIZE, TOTAL_TOOLS - 2 * PAGE_SIZE]);

    await client.close();
    await server.close();
  });

  it("a single listTools call sees only the first page", async () => {
    // Суть пастки: без циклу клієнт МОВЧКИ бачить лише першу сторінку.
    const server = createPaginatedServer();
    const client = new Client({ name: "pagination-naive", version: "1.0.0" });
    const [ct, st] = InMemoryTransport.createLinkedPair();
    await Promise.all([server.connect(st), client.connect(ct)]);

    const { tools, nextCursor } = await client.listTools();

    expect(tools).toHaveLength(PAGE_SIZE); // лише 10 з 25
    expect(nextCursor).toBeDefined(); // сигнал "є ще", який наївний клієнт ігнорує

    await client.close();
    await server.close();
  });
});
