// Self-wiring entry point для Notifications BC.
import type { DbPool } from "../shared/db.js";
import type { EventBus } from "../shared/events/bus.js";

import { Service } from "./app/service.js";
import { registerSubscribers } from "./infra/events/subscriber.js";
import { Handler } from "./infra/http/handler.js";
import { PgNotificationRepo } from "./infra/postgres/notificationRepo.js";
import { StubSender } from "./infra/stub/sender.js";

export interface Module {
  service: Service;
  handler: Handler;
}

export function newModule(db: DbPool, bus: EventBus): Module {
  const repo = new PgNotificationRepo(db);
  const sender = new StubSender();
  const service = new Service(repo, sender);
  registerSubscribers(bus, service);
  const handler = new Handler(service);
  return { service, handler };
}
