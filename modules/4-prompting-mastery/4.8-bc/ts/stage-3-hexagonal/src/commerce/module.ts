// Self-wiring entry point для Commerce BC.
import type { DbPool } from "../shared/db.js";
import type { EventBus } from "../shared/events/bus.js";

import { Service } from "./app/service.js";
import { Handler } from "./infra/http/handler.js";
import { PgOrderRepo } from "./infra/postgres/orderRepo.js";

export interface Module {
  service: Service;
  handler: Handler;
}

export function newModule(db: DbPool, bus: EventBus): Module {
  const repo = new PgOrderRepo(db);
  const service = new Service(repo, bus);
  const handler = new Handler(service);
  return { service, handler };
}
