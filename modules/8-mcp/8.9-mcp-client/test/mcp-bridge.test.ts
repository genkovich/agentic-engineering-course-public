// Тести mcp-bridge: конверсія схем, виконання tool_use
// і повний loop із замоканим Anthropic-клієнтом.
// Жодного реального Claude API і жодних зовнішніх процесів.

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import type Anthropic from "@anthropic-ai/sdk";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createEchoServer } from "./fixtures/echo-server.js";
import {
  mcpToolsToAnthropic,
  executeToolUse,
  runToolLoop,
  type McpToolDefinition,
  type MessagesApi,
} from "../src/mcp-bridge.js";

// Допоміжна збірка Anthropic.Message без реального API.
function fakeMessage(
  content: Anthropic.ContentBlock[],
  stopReason: Anthropic.StopReason,
): Anthropic.Message {
  return {
    id: "msg_test",
    type: "message",
    role: "assistant",
    model: "claude-sonnet-4-6",
    content,
    stop_reason: stopReason,
    stop_sequence: null,
    usage: { input_tokens: 1, output_tokens: 1 },
  } as Anthropic.Message;
}

describe("mcpToolsToAnthropic", () => {
  it("converts MCP inputSchema (camelCase) to Claude input_schema (snake_case)", () => {
    const mcpTools: McpToolDefinition[] = [
      {
        name: "echo",
        description: "Echoes the message back",
        inputSchema: {
          type: "object",
          properties: { message: { type: "string" } },
          required: ["message"],
        },
      },
    ];

    const tools = mcpToolsToAnthropic(mcpTools);

    expect(tools).toHaveLength(1);
    expect(tools[0].name).toBe("echo");
    expect(tools[0].description).toBe("Echoes the message back");
    // Ключова перевірка: схема перенесена як є, поле перейменоване.
    expect(tools[0].input_schema).toEqual({
      type: "object",
      properties: { message: { type: "string" } },
      required: ["message"],
    });
    expect(tools[0]).not.toHaveProperty("inputSchema");
  });

  it("falls back to empty description when MCP tool has none", () => {
    const tools = mcpToolsToAnthropic([
      { name: "bare", inputSchema: { type: "object" } },
    ]);
    expect(tools[0].description).toBe("");
  });
});

describe("executeToolUse against a real in-memory MCP server", () => {
  let client: Client;
  let server: McpServer;

  beforeEach(async () => {
    server = createEchoServer();
    client = new Client({ name: "bridge-test", version: "1.0.0" });
    const [ct, st] = InMemoryTransport.createLinkedPair();
    await Promise.all([server.connect(st), client.connect(ct)]);
  });

  afterEach(async () => {
    await client.close();
    await server.close();
  });

  it("turns a tool_use block into a matching tool_result", async () => {
    const toolUse: Anthropic.ToolUseBlock = {
      type: "tool_use",
      id: "toolu_123",
      name: "echo",
      input: { message: "ping" },
    };

    const result = await executeToolUse(client, toolUse);

    expect(result.type).toBe("tool_result");
    expect(result.tool_use_id).toBe("toolu_123"); // id мусить збігатися
    expect(result.content).toBe("Echo: ping");
    expect(result.is_error).toBeUndefined();
  });

  it("marks the result as error when the tool does not exist", async () => {
    const toolUse: Anthropic.ToolUseBlock = {
      type: "tool_use",
      id: "toolu_404",
      name: "no-such-tool",
      input: {},
    };

    const result = await executeToolUse(client, toolUse);

    expect(result.tool_use_id).toBe("toolu_404");
    expect(result.is_error).toBe(true);
  });
});

describe("runToolLoop with a mocked Anthropic client", () => {
  let client: Client;
  let server: McpServer;

  beforeEach(async () => {
    server = createEchoServer();
    client = new Client({ name: "loop-test", version: "1.0.0" });
    const [ct, st] = InMemoryTransport.createLinkedPair();
    await Promise.all([server.connect(st), client.connect(ct)]);
  });

  afterEach(async () => {
    await client.close();
    await server.close();
  });

  it("runs one tool_use round and finishes on end_turn", async () => {
    // Сценарій мока:
    //   1-й виклик: Claude просить echo("hello")  -> stop_reason: tool_use
    //   2-й виклик: Claude віддає фінальний текст -> stop_reason: end_turn
    const create = vi
      .fn<MessagesApi["messages"]["create"]>()
      .mockResolvedValueOnce(
        fakeMessage(
          [
            {
              type: "tool_use",
              id: "toolu_1",
              name: "echo",
              input: { message: "hello" },
            },
          ],
          "tool_use",
        ),
      )
      .mockResolvedValueOnce(
        fakeMessage(
          [{ type: "text", text: "Сервер відповів: Echo: hello", citations: null }],
          "end_turn",
        ),
      );

    const mockAnthropic: MessagesApi = { messages: { create } };

    const toolUses: string[] = [];
    const answer = await runToolLoop({
      anthropic: mockAnthropic,
      mcp: client,
      model: "claude-sonnet-4-6",
      userMessage: "Передай hello через echo",
      onToolUse: (name) => toolUses.push(name),
    });

    expect(answer).toBe("Сервер відповів: Echo: hello");
    expect(toolUses).toEqual(["echo"]);
    expect(create).toHaveBeenCalledTimes(2);

    // Перший запит: tools з MCP-сервера у форматі Claude API.
    const firstParams = create.mock.calls[0][0];
    expect(firstParams.tools?.map((t) => t.name).sort()).toEqual([
      "add",
      "echo",
    ]);
    expect(firstParams.messages).toEqual([
      { role: "user", content: "Передай hello через echo" },
    ]);

    // Другий запит: історія містить відповідь асистента з tool_use
    // і user-повідомлення з tool_result (id збігається, результат від
    // СПРАВЖНЬОГО fixture-сервера).
    const secondParams = create.mock.calls[1][0];
    expect(secondParams.messages).toHaveLength(3);
    expect(secondParams.messages[1].role).toBe("assistant");
    expect(secondParams.messages[2]).toEqual({
      role: "user",
      content: [
        {
          type: "tool_result",
          tool_use_id: "toolu_1",
          content: "Echo: hello",
          is_error: undefined,
        },
      ],
    });
  });

  it("throws when the loop exceeds maxIterations", async () => {
    // Claude "завис" і нескінченно просить той самий tool.
    const create = vi.fn<MessagesApi["messages"]["create"]>().mockResolvedValue(
      fakeMessage(
        [
          {
            type: "tool_use",
            id: "toolu_loop",
            name: "echo",
            input: { message: "again" },
          },
        ],
        "tool_use",
      ),
    );

    await expect(
      runToolLoop({
        anthropic: { messages: { create } },
        mcp: client,
        model: "claude-sonnet-4-6",
        userMessage: "loop forever",
        maxIterations: 3,
      }),
    ).rejects.toThrow(/did not finish in 3 iterations/);

    expect(create).toHaveBeenCalledTimes(3);
  });
});
