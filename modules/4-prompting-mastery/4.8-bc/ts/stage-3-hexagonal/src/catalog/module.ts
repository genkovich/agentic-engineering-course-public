// Self-wiring entry point для Catalog BC.
import type { DbPool } from "../shared/db.js";

import { Service } from "./app/service.js";
import { Handler } from "./infra/http/handler.js";
import { PgProductRepo } from "./infra/postgres/productRepo.js";

export interface Module {
  service: Service;
  handler: Handler;
}

export function newModule(db: DbPool): Module {
  const repo = new PgProductRepo(db);
  const service = new Service(repo);
  const handler = new Handler(service);
  return { service, handler };
}
