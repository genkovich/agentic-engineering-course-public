// utilities.ts: службовий шар протоколу з боку клієнта.
//
// Поруч з tools/resources/prompts специфікація описує utilities -
// допоміжні механізми, спільні для обох сторін. Три з них стосуються
// автора клієнта напряму, і всі три показані тут наживо:
//
//   1. ping         перевірка, що з'єднання живе (keepalive).
//   2. timeout      кожен запит має дефолтний таймаут 60 с; на таймаут SDK
//      + cancel     сам шле серверу notifications/cancelled. Override -
//                   третім аргументом callTool({ timeout }).
//   3. pagination   tools/list може приходити сторінками; клієнт МУСИТЬ
//                   крутити цикл по nextCursor, інакше мовчки втратить
//                   tools великого сервера.
//
// Жодного API-ключа: працюємо проти локальних фікстур по stdio.
//
// Запуск:
//   npx tsx src/utilities.ts

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";

// Невелика обгортка: підняти клієнт до stdio-сервера-фікстури.
async function connect(name: string, serverArgs: string[]): Promise<Client> {
  const transport = new StdioClientTransport({
    command: serverArgs[0],
    args: serverArgs.slice(1),
  });
  const client = new Client({ name, version: "1.0.0" });
  await client.connect(transport);
  return client;
}

// ─── 1. PING ───
// Запит без параметрів, на який друга сторона зобов'язана відповісти
// одразу порожнім результатом. Довгоживучому клієнту (бот, дашборд) ping
// дає keepalive: відрізнити "сервер живий, просто мовчить" від "з'єднання
// давно померло". Немає відповіді - перепідключайся.
async function demoPing(): Promise<void> {
  console.log("── ping ──");
  const client = await connect("ping-demo", [
    "npx",
    "tsx",
    "test/fixtures/slow-server.ts",
  ]);

  const start = Date.now();
  await client.ping();
  console.log(`  ping -> pong за ${Date.now() - start}ms (з'єднання живе)\n`);

  await client.close();
}

// ─── 2. TIMEOUT + CANCELLATION ───
// slow(2000) проти таймауту 500ms падає з RequestTimeout, і SDK у цей
// момент шле серверу notifications/cancelled - сервер може зупинити
// нікому не потрібну роботу. Піднімаємо таймаут до 5000ms - той самий
// виклик проходить.
async function demoTimeout(): Promise<void> {
  console.log("── timeout + cancellation ──");
  const client = await connect("timeout-demo", [
    "npx",
    "tsx",
    "test/fixtures/slow-server.ts",
  ]);

  // Спроба 1: tool працює 2000ms, таймаут 500ms -> падіння.
  console.log("  callTool slow(2000ms) з timeout=500ms ...");
  try {
    await client.callTool({ name: "slow", arguments: { ms: 2000 } }, undefined, {
      timeout: 500,
    });
    console.log("  (несподівано: таймаут не спрацював)");
  } catch (error) {
    const timedOut =
      error instanceof McpError && error.code === ErrorCode.RequestTimeout;
    console.log(
      `  -> ${timedOut ? "RequestTimeout" : "помилка"}: ${error instanceof Error ? error.message : String(error)}`,
    );
    console.log("     (SDK надіслав серверу notifications/cancelled)");
  }

  // Спроба 2: піднімаємо таймаут до 5000ms -> той самий виклик проходить.
  console.log("\n  callTool slow(2000ms) з timeout=5000ms ...");
  const result = await client.callTool(
    { name: "slow", arguments: { ms: 2000 } },
    undefined,
    { timeout: 5000 },
  );
  const text = (result.content as Array<{ type: string; text?: string }>)
    .map((b) => b.text ?? "")
    .join("");
  console.log(`  -> успіх: ${text}\n`);

  await client.close();
}

// ─── 3. PAGINATION ───
// tools/list не зобов'язаний віддати весь каталог одразу: сервер повертає
// сторінку і nextCursor. Курсор непрозорий - повертаємо його як є. Є
// nextCursor - є наступна сторінка; зник - список закінчився. Без цього
// циклу клієнт МОВЧКИ втрачає tools з наступних сторінок.
async function demoPagination(): Promise<void> {
  console.log("── pagination ──");
  const client = await connect("pagination-demo", [
    "npx",
    "tsx",
    "test/fixtures/paginated-server.ts",
  ]);

  const allTools: string[] = [];
  let cursor: string | undefined;
  let page = 0;

  // Обов'язковий цикл: чотири рядки do/while по nextCursor.
  do {
    const result = await client.listTools(cursor ? { cursor } : undefined);
    page += 1;
    allTools.push(...result.tools.map((tool) => tool.name));
    console.log(
      `  сторінка ${page}: +${result.tools.length} tools` +
        (result.nextCursor ? ` (nextCursor: ${result.nextCursor})` : " (кінець)"),
    );
    cursor = result.nextCursor;
  } while (cursor);

  console.log(
    `  -> разом ${allTools.length} tools за ${page} сторінки: ${allTools[0]} … ${allTools[allTools.length - 1]}\n`,
  );

  await client.close();
}

async function main(): Promise<void> {
  await demoPing();
  await demoTimeout();
  await demoPagination();
  console.log("Готово. Усі три utilities - без жодного API-ключа.");
}

main().catch((error) => {
  console.error("Error:", error instanceof Error ? error.message : error);
  process.exit(1);
});
