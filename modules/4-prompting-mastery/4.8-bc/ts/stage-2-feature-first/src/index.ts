import Fastify from "fastify";

import { newPool } from "./shared/db.js";

import * as auth from "./features/auth/index.js";
import * as catalog from "./features/catalog/index.js";
import * as commerce from "./features/commerce/index.js";
import * as billing from "./features/billing/index.js";
import * as notifications from "./features/notifications/index.js";

function envOr(key: string, fallback: string): string {
  const v = process.env[key];
  return v && v.length > 0 ? v : fallback;
}

function parseAddr(addr: string): { host: string; port: number } {
  if (addr.startsWith(":")) {
    return { host: "0.0.0.0", port: Number(addr.slice(1)) };
  }
  const idx = addr.lastIndexOf(":");
  if (idx === -1) return { host: "0.0.0.0", port: Number(addr) };
  return {
    host: addr.slice(0, idx) || "0.0.0.0",
    port: Number(addr.slice(idx + 1)),
  };
}

async function main(): Promise<void> {
  const dsn = envOr(
    "DATABASE_URL",
    "postgres://demo:demo@localhost:5432/demo",
  );
  const addr = envOr("HTTP_ADDR", ":8080");
  const { host, port } = parseAddr(addr);

  const pool = newPool(dsn);

  const authH = new auth.Handler(new auth.Service(new auth.Repository(pool)));
  const catalogH = new catalog.Handler(
    new catalog.Service(new catalog.Repository(pool)),
  );
  const commerceH = new commerce.Handler(
    new commerce.Service(new commerce.Repository(pool)),
  );
  const billingH = new billing.Handler(
    new billing.Service(new billing.Repository(pool)),
  );
  const notificationsH = new notifications.Handler(
    new notifications.Service(new notifications.Repository(pool)),
  );

  const app = Fastify({ logger: true });

  authH.register(app);
  catalogH.register(app);
  commerceH.register(app);
  billingH.register(app);
  notificationsH.register(app);

  app.get("/healthz", async (_req, reply) => reply.code(200).send({ ok: true }));

  const closeAndExit = async (): Promise<void> => {
    try {
      await app.close();
      await pool.end();
    } finally {
      process.exit(0);
    }
  };
  process.on("SIGINT", closeAndExit);
  process.on("SIGTERM", closeAndExit);

  await app.listen({ host, port });
  app.log.info(`listening on ${addr}`);
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error("fatal:", err);
  process.exit(1);
});
