// 01-list-and-call.ts: "hello world" власного MCP-клієнта.
//
// Мінімальний клієнт без жодного AI: підключаємось до будь-якого
// stdio MCP-сервера, дивимось список tools і (опційно) викликаємо один.
// Це той самий протокол, яким Claude Code говорить з MCP-серверами,
// тільки тут ми бачимо його руками.
//
// Запуск:
//   npx tsx src/01-list-and-call.ts <команда сервера> [аргументи...]
//   npx tsx src/01-list-and-call.ts <команда> [args...] --tool <name> --tool-args '<json>'
//
// Приклади:
//   npx tsx src/01-list-and-call.ts npx tsx test/fixtures/echo-server.ts
//   npx tsx src/01-list-and-call.ts npx tsx test/fixtures/echo-server.ts \
//     --tool echo --tool-args '{"message":"привіт"}'

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

interface CliArgs {
  serverCommand: string;
  serverArgs: string[];
  toolName?: string;
  toolArgs: Record<string, unknown>;
}

// Розбираємо argv: усе до --tool вважаємо командою сервера.
function parseArgs(argv: string[]): CliArgs {
  const toolFlag = argv.indexOf("--tool");
  const serverPart = toolFlag === -1 ? argv : argv.slice(0, toolFlag);

  if (serverPart.length === 0) {
    console.error(
      "Usage: tsx src/01-list-and-call.ts <server-command> [args...] " +
        "[--tool <name> --tool-args '<json>']",
    );
    process.exit(1);
  }

  let toolName: string | undefined;
  let toolArgs: Record<string, unknown> = {};

  if (toolFlag !== -1) {
    toolName = argv[toolFlag + 1];
    const argsFlag = argv.indexOf("--tool-args");
    if (argsFlag !== -1 && argv[argsFlag + 1]) {
      toolArgs = JSON.parse(argv[argsFlag + 1]);
    }
  }

  return {
    serverCommand: serverPart[0],
    serverArgs: serverPart.slice(1),
    toolName,
    toolArgs,
  };
}

async function main(): Promise<void> {
  const { serverCommand, serverArgs, toolName, toolArgs } = parseArgs(
    process.argv.slice(2),
  );

  // 1. Транспорт: клієнт сам запускає серверний процес
  //    і говорить з ним через stdin/stdout (JSON-RPC рядками).
  const transport = new StdioClientTransport({
    command: serverCommand,
    args: serverArgs,
  });

  // 2. Клієнт: представляємось серверу під час handshake.
  const client = new Client({ name: "demo-mcp-client", version: "1.0.0" });

  // 3. connect() робить initialize-handshake: клієнт і сервер
  //    обмінюються можливостями (capabilities) і версією протоколу.
  await client.connect(transport);
  console.log(`Connected to: ${serverCommand} ${serverArgs.join(" ")}`);

  // 4. listTools(): питаємо сервер, що він уміє.
  //    Це той самий запит tools/list, який робить Claude Code
  //    після підключення MCP-сервера.
  const { tools } = await client.listTools();
  console.log(`\nTools (${tools.length}):`);
  for (const tool of tools) {
    console.log(`  - ${tool.name}: ${tool.description ?? "(no description)"}`);
  }

  // 5. callTool(): викликаємо конкретний tool з аргументами.
  if (toolName) {
    console.log(`\nCalling tool "${toolName}" with`, toolArgs);
    const result = await client.callTool({
      name: toolName,
      arguments: toolArgs,
    });
    console.log("Result:");
    console.log(JSON.stringify(result.content, null, 2));
  }

  // 6. Закриваємо з'єднання: транспорт зупинить серверний процес.
  await client.close();
}

main().catch((error) => {
  console.error("Error:", error instanceof Error ? error.message : error);
  process.exit(1);
});
