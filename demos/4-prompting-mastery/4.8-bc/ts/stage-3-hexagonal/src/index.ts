// Bootstrap: wires modules through ports/registrar.
// Per BC isolation contract: жоден BC не імпортує іншого. Тільки index.ts і shared/events.
import Fastify from "fastify";

import * as auth from "./auth/module.js";
import * as billing from "./billing/module.js";
import * as catalog from "./catalog/module.js";
import * as commerce from "./commerce/module.js";
import * as notifications from "./notifications/module.js";
import { newPool } from "./shared/db.js";
import { newBus } from "./shared/events/bus.js";

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
  const bus = newBus();

  const authMod = auth.newModule(pool, bus);
  const catalogMod = catalog.newModule(pool);
  const commerceMod = commerce.newModule(pool, bus);
  const billingMod = billing.newModule(pool, bus);
  const notificationsMod = notifications.newModule(pool, bus);

  const app = Fastify({ logger: true });

  authMod.handler.register(app);
  catalogMod.handler.register(app);
  commerceMod.handler.register(app);
  billingMod.handler.register(app);
  notificationsMod.handler.register(app);

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
