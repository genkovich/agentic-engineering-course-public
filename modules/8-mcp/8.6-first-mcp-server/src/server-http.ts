// server-http.ts: той самий task-store, інший транспорт (лекція 8.8).
// Уся логіка сервера - createServer з server.ts: секції registerTool /
// registerResource / registerPrompt лишаються без жодних змін.
// Міняється тільки wiring нижче: stdio → Streamable HTTP.
//
// Stateless режим (sessionIdGenerator: undefined): на кожен POST /mcp
// створюємо свіжу пару McpServer + transport, обробляємо запит, прибираємо.
// Стан живе у TaskStore (data/tasks.json), а не у MCP-сесії.

import { fileURLToPath } from "node:url";
import express, { type Request, type Response } from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createServer } from "./server.js";
import { TaskStore } from "./store.js";

const DATA_FILE = fileURLToPath(new URL("../data/tasks.json", import.meta.url));
const PORT = Number(process.env.PORT ?? 3335);

const store = new TaskStore(DATA_FILE);
store.load();

const app = express();
app.use(express.json());

// Liveness/readiness-проба для балансувальника чи оркестратора: дешева, без
// MCP-протоколу. Окремий шлях /healthz (конвенція k8s-стилю) відповідає миттєво
// і не тягне MCP initialize. tasks - скільки задач у сховищі: проба заразом
// підтверджує, що дані з data/tasks.json реально піднялись (лекція 8.12).
app.get("/healthz", (_req: Request, res: Response) => {
  res.json({ ok: true, tasks: store.listTasks("all").length });
});

app.post("/mcp", async (req: Request, res: Response) => {
  // Trace-кореляція (лекція 8.12): клієнт кладе W3C traceparent у params._meta
  // свого запиту, сервер пише його у лог - виклик клієнта зв'язується з логами
  // сервера одним id. Читання _meta і прикріплення id до логів - робота автора
  // сервера; у проді цю роль бере на себе інтеграція з OpenTelemetry SDK.
  const traceparent = req.body?.params?._meta?.traceparent;
  if (typeof traceparent === "string") {
    console.log(
      `[mcp] trace=${traceparent} method=${req.body?.method} tool=${req.body?.params?.name ?? "-"}`,
    );
  }
  const server = createServer(store);
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
  });
  res.on("close", () => {
    void transport.close();
    void server.close();
  });
  await server.connect(transport);
  await transport.handleRequest(req, res, req.body);
});

// У stateless-режимі GET (SSE-стрім сесії) і DELETE (закриття сесії) сенсу не мають
const methodNotAllowed = (_req: Request, res: Response) => {
  res.status(405).json({
    jsonrpc: "2.0",
    error: { code: -32000, message: "Method not allowed: stateless server" },
    id: null,
  });
};
app.get("/mcp", methodNotAllowed);
app.delete("/mcp", methodNotAllowed);

app.listen(PORT, () => {
  // Тут stdout вільний: JSON-RPC їде через HTTP, а не через стандартні потоки
  console.log(`task-store MCP server (Streamable HTTP): http://localhost:${PORT}/mcp`);
});
