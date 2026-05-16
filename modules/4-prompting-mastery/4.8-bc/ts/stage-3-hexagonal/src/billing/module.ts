// Self-wiring entry point для Billing BC.
import type { DbPool } from "../shared/db.js";
import type { EventBus } from "../shared/events/bus.js";

import { Service } from "./app/service.js";
import { Handler } from "./infra/http/handler.js";
import { PgSubscriptionRepo } from "./infra/postgres/subscriptionRepo.js";

export interface Module {
  service: Service;
  handler: Handler;
}

export function newModule(db: DbPool, bus: EventBus): Module {
  const repo = new PgSubscriptionRepo(db);
  const service = new Service(repo, bus);
  const handler = new Handler(service);
  return { service, handler };
}
