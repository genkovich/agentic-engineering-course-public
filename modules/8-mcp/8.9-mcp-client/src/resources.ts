// resources.ts: клієнт читає не тільки tools.
//
// Приклад 01 говорив з одним примітивом - tools. Але сервер може віддавати
// ще два: resources (дані для читання) і prompts (готові шаблони). У SDK для
// них є такі самі дзеркальні дієслова, як listTools/callTool:
//
//   listResources()                 які URI сервер готовий віддати
//   readResource({ uri })           прочитати конкретний (розгалуження за mimeType)
//   listPrompts()                   доступні шаблони з аргументами
//   getPrompt({ name, arguments })  готовий масив messages для Messages API
//
// Сервером тут виступає task-store з лекції 8.6 - той самий, що ми збудували:
// у нього вже є resource tasks://summary і prompt plan-day. Нового сервера
// писати не треба, бо клієнт говорить з будь-яким MCP-сервером.
//
// Спершу кладемо пару задач (callTool add_task), щоб resource і prompt мали
// що показати, далі - чотири read-дієслова. Жодного API-ключа.
//
// Запуск (task-store з 8.6 піднімається автоматично через tsx):
//   npx tsx src/resources.ts

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// Команда запуску task-store з 8.6. Клієнт сам стартує цей процес по stdio,
// як у прикладі 01. Сервер пише свій стан у ../8.6-first-mcp-server/data/
// (gitignored) - тому для чистого прогону той файл можна видалити заздалегідь.
const TASK_STORE = ["npx", "tsx", "../8.6-first-mcp-server/src/server.ts"];

async function main(): Promise<void> {
  const transport = new StdioClientTransport({
    command: TASK_STORE[0],
    args: TASK_STORE.slice(1),
  });
  const client = new Client({ name: "resources-demo", version: "1.0.0" });
  await client.connect(transport);
  console.log(`MCP server: ${TASK_STORE.join(" ")}\n`);

  // Кладемо пару задач через tool, щоб було що читати у resource/prompt.
  await client.callTool({
    name: "add_task",
    arguments: { title: "Записати демо 8.9", priority: "high" },
  });
  await client.callTool({
    name: "add_task",
    arguments: { title: "Зробити рев'ю PR", priority: "low" },
  });

  // ─── listResources: каталог даних ───
  // Сервер каже, які URI він готовий віддати. tasks://summary - фіксований
  // ресурс, tasks://task/{id} - по одному на кожну задачу.
  const { resources } = await client.listResources();
  console.log(`listResources (${resources.length}):`);
  for (const resource of resources) {
    console.log(`  - ${resource.uri}  [${resource.mimeType ?? "?"}]`);
  }

  // ─── readResource: text/plain гілка ───
  // Перше, що робить клієнт - дивиться на mimeType першого contents
  // і розгалужується. text/plain віддаємо як є.
  console.log("\nreadResource tasks://summary  (text/plain -> як є):");
  const summary = await client.readResource({ uri: "tasks://summary" });
  console.log(indent(textOf(summary.contents[0])));

  // ─── readResource: application/json гілка ───
  // Той самий виклик, інший mimeType: application/json -> парсимо у структуру.
  const taskUri = resources.find((r) => r.uri.startsWith("tasks://task/"))?.uri;
  if (taskUri) {
    console.log(`\nreadResource ${taskUri}  (application/json -> парсимо):`);
    const task = await client.readResource({ uri: taskUri });
    const data = JSON.parse(textOf(task.contents[0]));
    console.log(`  ${data.title} - пріоритет ${data.priority}, статус ${data.status}`);
  }

  // ─── listPrompts: доступні шаблони ───
  const { prompts } = await client.listPrompts();
  console.log(`\nlistPrompts (${prompts.length}):`);
  for (const prompt of prompts) {
    const args = (prompt.arguments ?? []).map((a) => a.name).join(", ");
    console.log(`  - ${prompt.name}(${args}): ${prompt.description ?? ""}`);
  }

  // ─── getPrompt: готові messages ───
  // Сервер сам зібрав промпт з ролями і вмістом - цей масив можна слати
  // у Messages API без жодної трансформації.
  console.log('\ngetPrompt plan-day { focus: "демо до запису" }:');
  const planDay = await client.getPrompt({
    name: "plan-day",
    arguments: { focus: "демо до запису" },
  });
  for (const message of planDay.messages) {
    console.log(indent(`[${message.role}] ${textOf(message.content)}`));
  }

  await client.close();
}

// MCP-контент буває масивом блоків або одним блоком; нам потрібен текст.
function textOf(block: unknown): string {
  if (block && typeof block === "object" && "text" in block) {
    return String((block as { text: unknown }).text);
  }
  return JSON.stringify(block);
}

function indent(text: string): string {
  return text
    .split("\n")
    .map((line) => `  ${line}`)
    .join("\n");
}

main().catch((error) => {
  console.error("Error:", error instanceof Error ? error.message : error);
  process.exit(1);
});
