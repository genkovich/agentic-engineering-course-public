// 02-claude-loop.ts: повний tool-use loop. Центральний код лекції 8.9.
//
// Ось що відбувається, коли ти питаєш щось у Claude Code і він
// викликає MCP-інструмент. Ми збираємо цей механізм самі:
//
//   ┌─────────┐  messages + tools   ┌────────────┐
//   │  Claude  │ <────────────────── │  наш код   │
//   │   API    │                     │  (клієнт)  │
//   │          │  stop_reason:       │            │   callTool   ┌─────────┐
//   │          │  "tool_use"         │            │ ───────────> │   MCP   │
//   │          │ ──────────────────> │            │ <─────────── │  сервер │
//   │          │  tool_result        │            │    result    └─────────┘
//   │          │ <────────────────── │            │
//   └─────────┘  ...і так по колу,  └────────────┘
//                 поки stop_reason !== "end_turn"
//
// Claude НЕ викликає MCP-сервер сам. Він лише каже, ЩО викликати.
// Виконує завжди наш код. Це і є робота MCP-клієнта (host application).
//
// Запуск (потрібен ANTHROPIC_API_KEY у .env):
//   npx tsx src/02-claude-loop.ts "<запит>" -- <команда сервера> [args...]
//
// Приклад:
//   npx tsx src/02-claude-loop.ts "Додай 21 і 21, а відповідь продублюй через echo" \
//     -- npx tsx test/fixtures/echo-server.ts

import "dotenv/config";
import Anthropic from "@anthropic-ai/sdk";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { runToolLoop } from "./mcp-bridge.js";

// Sonnet: достатньо розумний для tool use і дешевший за Opus для демо.
const MODEL = "claude-sonnet-4-6";

const DEFAULT_PROMPT =
  "Додай числа 21 і 21 інструментом add, а потім продублюй результат через echo.";
const DEFAULT_SERVER = ["npx", "tsx", "test/fixtures/echo-server.ts"];

async function main(): Promise<void> {
  // Без ключа падаємо одразу зі зрозумілим повідомленням,
  // а не стек-трейсом з надр SDK.
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error(
      "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key.",
    );
    process.exit(1);
  }

  // Розбираємо argv: до "--" запит, після "--" команда сервера.
  const argv = process.argv.slice(2);
  const separator = argv.indexOf("--");
  const prompt =
    (separator === -1 ? argv.join(" ") : argv.slice(0, separator).join(" ")) ||
    DEFAULT_PROMPT;
  const serverCmd =
    separator === -1 ? DEFAULT_SERVER : argv.slice(separator + 1);

  // 1. Підключаємось до MCP-сервера (як у прикладі 01).
  const transport = new StdioClientTransport({
    command: serverCmd[0],
    args: serverCmd.slice(1),
  });
  const mcp = new Client({ name: "claude-loop-demo", version: "1.0.0" });
  await mcp.connect(transport);
  console.log(`MCP server: ${serverCmd.join(" ")}`);

  // 2. Клієнт Claude API. Ключ підхоплюється з ANTHROPIC_API_KEY.
  const anthropic = new Anthropic();

  console.log(`User: ${prompt}\n`);

  // 3. Запускаємо цикл. Вся логіка живе у mcp-bridge.ts,
  //    тут ми лише підписуємось на події, щоб бачити хід думки.
  const answer = await runToolLoop({
    anthropic,
    mcp,
    model: MODEL,
    userMessage: prompt,
    onText: (text) => console.log(`Claude: ${text}`),
    onToolUse: (name, input) =>
      console.log(`  [tool_use]    ${name}(${JSON.stringify(input)})`),
    onToolResult: (result) =>
      console.log(
        `  [tool_result] ${typeof result.content === "string" ? result.content : JSON.stringify(result.content)}`,
      ),
  });

  console.log(`\nFinal answer: ${answer}`);

  await mcp.close();
}

main().catch((error) => {
  console.error("Error:", error instanceof Error ? error.message : error);
  process.exit(1);
});
