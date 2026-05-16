import Fastify from "fastify";

import { newPool } from "./db.js";
import { mountUser } from "./handler/user.js";
import { mountProduct } from "./handler/product.js";
import { mountOrder } from "./handler/order.js";
import { mountSubscription } from "./handler/subscription.js";
import { mountNotification } from "./handler/notification.js";
import { UserRepository } from "./repository/user.js";
import { ProductRepository } from "./repository/product.js";
import { OrderRepository } from "./repository/order.js";
import { SubscriptionRepository } from "./repository/subscription.js";
import { NotificationRepository } from "./repository/notification.js";
import { UserService } from "./service/user.js";
import { ProductService } from "./service/product.js";
import { OrderService } from "./service/order.js";
import { SubscriptionService } from "./service/subscription.js";
import { NotificationService } from "./service/notification.js";

function envOr(key: string, fallback: string): string {
  const v = process.env[key];
  return v && v.length > 0 ? v : fallback;
}

function parseAddr(addr: string): { host: string; port: number } {
  // ":8080" → { host: "0.0.0.0", port: 8080 }
  // "127.0.0.1:8080" → { host: "127.0.0.1", port: 8080 }
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

  const userRepo = new UserRepository(pool);
  const productRepo = new ProductRepository(pool);
  const orderRepo = new OrderRepository(pool);
  const subscriptionRepo = new SubscriptionRepository(pool);
  const notificationRepo = new NotificationRepository(pool);

  const userSvc = new UserService(userRepo);
  const productSvc = new ProductService(productRepo);
  const orderSvc = new OrderService(orderRepo);
  const subscriptionSvc = new SubscriptionService(subscriptionRepo);
  const notificationSvc = new NotificationService(notificationRepo);

  const app = Fastify({ logger: true });

  mountUser(app, userSvc);
  mountProduct(app, productSvc);
  mountOrder(app, orderSvc);
  mountSubscription(app, subscriptionSvc);
  mountNotification(app, notificationSvc);

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
