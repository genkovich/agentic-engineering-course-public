// Один Express-процес, два призначення:
// 1. POST /webhook  - приймає CI/CD події GitHub/GitLab, нормалізує і кладе у чергу
// 2. /mcp           - MCP endpoint через Streamable HTTP, tools читають ту саму чергу
//
// Транспорт працює у stateless режимі (sessionIdGenerator: undefined):
// на кожен POST /mcp створюємо новий McpServer + transport, обробляємо запит, прибираємо.
// Стан живе у черзі (EventQueue), а не у MCP-сесії, тому сесії тут не потрібні.

import { createHmac, timingSafeEqual } from "node:crypto";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import express, { type Express, type Request, type Response } from "express";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { buildMcpServer } from "./mcp.js";
import { normalizeGithub, normalizeGitlab } from "./normalize.js";
import { EventQueue } from "./queue.js";
import type { TelegramConfig } from "./telegram.js";

export interface AppConfig {
  dataDir: string;
  webhookSecret?: string;
  telegramBotToken?: string;
  telegramChatId?: string;
}

// Перевірка підпису GitHub: X-Hub-Signature-256 = "sha256=" + HMAC SHA-256 від raw body
function verifyGithubSignature(secret: string, rawBody: Buffer, header: string | undefined): boolean {
  if (!header) return false;
  const expected = Buffer.from(`sha256=${createHmac("sha256", secret).update(rawBody).digest("hex")}`);
  const actual = Buffer.from(header);
  // timingSafeEqual кидає помилку на буферах різної довжини, тому перевіряємо довжину окремо
  return expected.length === actual.length && timingSafeEqual(expected, actual);
}

export function createApp(config: AppConfig): { app: Express; queue: EventQueue } {
  const queue = new EventQueue(join(config.dataDir, "events.json"));
  const telegram: TelegramConfig = {
    botToken: config.telegramBotToken,
    chatId: config.telegramChatId,
    sentFile: join(config.dataDir, "sent.json"),
  };

  if (!config.webhookSecret) {
    console.warn("[webhook] WEBHOOK_SECRET not set: accepting webhooks WITHOUT signature verification");
  }
  if (!telegram.botToken || !telegram.chatId) {
    console.warn("[telegram] TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID not set: send_notification works in dry-run mode");
  }

  const app = express();
  // Зберігаємо raw body: HMAC-підпис рахується від байтів запиту, а не від розпарсеного JSON
  app.use(
    express.json({
      verify: (req, _res, buf) => {
        (req as Request & { rawBody?: Buffer }).rawBody = buf;
      },
    }),
  );

  // ---------- Webhook receiver ----------

  app.post("/webhook", (req: Request, res: Response) => {
    const githubEvent = req.header("x-github-event");
    const gitlabEvent = req.header("x-gitlab-event");

    if (!githubEvent && !gitlabEvent) {
      res.status(400).json({ error: "Expected X-GitHub-Event or X-Gitlab-Event header" });
      return;
    }

    if (config.webhookSecret) {
      if (githubEvent) {
        const rawBody = (req as Request & { rawBody?: Buffer }).rawBody ?? Buffer.alloc(0);
        if (!verifyGithubSignature(config.webhookSecret, rawBody, req.header("x-hub-signature-256"))) {
          res.status(401).json({ error: "Invalid X-Hub-Signature-256" });
          return;
        }
      } else {
        // GitLab шле секрет як plain token, без HMAC
        if (req.header("x-gitlab-token") !== config.webhookSecret) {
          res.status(401).json({ error: "Invalid X-Gitlab-Token" });
          return;
        }
      }
    }

    const event = githubEvent
      ? normalizeGithub(githubEvent, req.body ?? {})
      : normalizeGitlab(gitlabEvent!, req.body ?? {});
    queue.add(event);
    console.log(`[webhook] stored ${event.source}/${event.kind}: ${event.title}`);
    res.status(202).json({ ok: true, id: event.id, kind: event.kind });
  });

  // Допоміжний endpoint для швидкої перевірки черги через curl (не частина MCP)
  app.get("/events", (_req: Request, res: Response) => {
    res.json(queue.list("all"));
  });

  app.get("/health", (_req: Request, res: Response) => {
    res.json({ ok: true, events: queue.size() });
  });

  // Liveness-проба для балансувальника/оркестратора: дешева, без MCP-протоколу.
  // Окремий шлях /healthz - конвенція k8s-стилю, відповідає миттєво і не тягне initialize
  app.get("/healthz", (_req: Request, res: Response) => {
    res.json({ ok: true, events: queue.size() });
  });

  // ---------- MCP endpoint (Streamable HTTP, stateless) ----------

  app.post("/mcp", async (req: Request, res: Response) => {
    // Trace-кореляція: клієнт кладе W3C traceparent у params._meta свого запиту,
    // сервер пише його у лог - виклик клієнта зв'язується з логами сервера одним id
    const traceparent = req.body?.params?._meta?.traceparent;
    if (typeof traceparent === "string") {
      console.log(`[mcp] trace=${traceparent} method=${req.body?.method} tool=${req.body?.params?.name ?? "-"}`);
    }
    // Новий server + transport на кожен запит: жодного спільного стану між запитами,
    // отже жодних session id і race conditions. Це документований stateless-патерн SDK.
    const server = buildMcpServer(queue, telegram);
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
    });
    res.on("close", () => {
      void transport.close();
      void server.close();
    });
    try {
      await server.connect(transport);
      await transport.handleRequest(req, res, req.body);
    } catch (err) {
      console.error("[mcp] request failed:", err);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: { code: -32603, message: "Internal server error" },
          id: null,
        });
      }
    }
  });

  // У stateless режимі GET (server-initiated SSE stream) і DELETE (закриття сесії) не мають сенсу
  const methodNotAllowed = (_req: Request, res: Response) => {
    res.status(405).json({
      jsonrpc: "2.0",
      error: { code: -32000, message: "Method not allowed." },
      id: null,
    });
  };
  app.get("/mcp", methodNotAllowed);
  app.delete("/mcp", methodNotAllowed);

  return { app, queue };
}

// Запуск сервера тільки коли файл виконано напряму (tsx src/server.ts або node dist/server.js),
// при імпорті з тестів сервер не стартує
const isMain = process.argv[1] !== undefined && fileURLToPath(import.meta.url) === resolve(process.argv[1]);

if (isMain) {
  await import("dotenv/config");
  const port = Number(process.env.PORT ?? 3334);
  const { app } = createApp({
    dataDir: process.env.DATA_DIR ?? join(process.cwd(), "data"),
    webhookSecret: process.env.WEBHOOK_SECRET || undefined,
    telegramBotToken: process.env.TELEGRAM_BOT_TOKEN || undefined,
    telegramChatId: process.env.TELEGRAM_CHAT_ID || undefined,
  });
  app.listen(port, () => {
    console.log(`notify-hub listening on http://localhost:${port}`);
    console.log(`  webhook receiver: POST http://localhost:${port}/webhook`);
    console.log(`  MCP endpoint:     POST http://localhost:${port}/mcp`);
  });
}
