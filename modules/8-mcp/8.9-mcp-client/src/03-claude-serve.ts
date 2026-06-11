// 03-claude-serve.ts: кульмінація. Claude Code як MCP-сервер.
//
// У лекції 8.5 ми бачили `claude mcp serve`: Claude Code вивертається
// навиворіт і віддає свої інструменти (Read, Write, Bash, Glob, Grep...)
// будь-якому MCP-клієнту. Тут цим клієнтом стає НАШ код з прикладу 02.
//
// Виходить цікава конструкція:
//
//   наш код ──> Claude API (мозок, вирішує ЩО робити)
//      │
//      └─────> claude mcp serve (руки, MCP-сервер з Read/Write/Bash)
//
// Тобто твій скрипт через Claude API керує інструментами Claude Code.
// Жодного нового коду циклу: той самий runToolLoop з mcp-bridge.ts,
// помінялась лише команда запуску сервера.
//
// УВАГА, БЕЗПЕКА: `claude mcp serve` дає клієнту інструменти з доступом
// до твоєї файлової системи БЕЗ підтверджень. Запускай тільки із
// запитами, яким довіряєш. Деталі у README.
//
// Запуск (потрібні ANTHROPIC_API_KEY і встановлений Claude Code CLI):
//   npx tsx src/03-claude-serve.ts
//   npx tsx src/03-claude-serve.ts "Прочитай package.json і скажи, які там scripts"

import "dotenv/config";
import Anthropic from "@anthropic-ai/sdk";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { runToolLoop } from "./mcp-bridge.js";

const MODEL = "claude-sonnet-4-6";

// Сценарій демо: Claude має сам здогадатись викликати Read tool
// сервера, прочитати файл і порахувати рядки.
const DEFAULT_PROMPT =
  "Прочитай файл README.md у поточній директорії і скажи, скільки в ньому рядків.";

async function main(): Promise<void> {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error(
      "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.",
    );
    process.exit(1);
  }

  const prompt = process.argv.slice(2).join(" ") || DEFAULT_PROMPT;

  // Єдина відмінність від прикладу 02: сервером тепер є Claude Code.
  // Команда "claude mcp serve" піднімає MCP-сервер на stdio.
  const transport = new StdioClientTransport({
    command: "claude",
    args: ["mcp", "serve"],
  });
  const mcp = new Client({ name: "claude-serve-demo", version: "1.0.0" });

  try {
    await mcp.connect(transport);
  } catch (error) {
    console.error(
      "Failed to start `claude mcp serve`. Is Claude Code CLI installed?\n" +
        "Install: npm install -g @anthropic-ai/claude-code",
    );
    throw error;
  }

  // Подивимось, які інструменти віддає Claude Code.
  const { tools } = await mcp.listTools();
  console.log(
    `claude mcp serve tools (${tools.length}): ${tools.map((t) => t.name).join(", ")}\n`,
  );

  const anthropic = new Anthropic();
  console.log(`User: ${prompt}\n`);

  // Той самий цикл, що й у 02. Claude через tool_use викличе Read tool
  // сервера, отримає вміст файлу і порахує рядки.
  const answer = await runToolLoop({
    anthropic,
    mcp,
    model: MODEL,
    userMessage: prompt,
    system:
      "You are a helpful assistant. Use the available tools to inspect files " +
      "when the user asks about them. Answer in the language of the question.",
    onText: (text) => console.log(`Claude: ${text}`),
    onToolUse: (name, input) =>
      console.log(`  [tool_use]    ${name}(${JSON.stringify(input)})`),
    onToolResult: (result) => {
      const text =
        typeof result.content === "string"
          ? result.content
          : JSON.stringify(result.content);
      // Вміст файлів буває довгим, обрізаємо для логу.
      console.log(
        `  [tool_result] ${text.length > 200 ? text.slice(0, 200) + "..." : text}`,
      );
    },
  });

  console.log(`\nFinal answer: ${answer}`);

  await mcp.close();
}

main().catch((error) => {
  console.error("Error:", error instanceof Error ? error.message : error);
  process.exit(1);
});
