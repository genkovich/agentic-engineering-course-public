// Self-wiring entry point для Auth BC.
// src/index.ts викликає newModule(...) і отримує Module з готовим Handler.
import type { DbPool } from "../shared/db.js";
import type { EventBus } from "../shared/events/bus.js";

import { Service } from "./app/service.js";
import { Handler } from "./infra/http/handler.js";
import { PgUserRepo } from "./infra/postgres/userRepo.js";

export interface Module {
  service: Service;
  handler: Handler;
}

export function newModule(db: DbPool, bus: EventBus): Module {
  const repo = new PgUserRepo(db);
  const service = new Service(repo, bus);
  const handler = new Handler(service);
  return { service, handler };
}
