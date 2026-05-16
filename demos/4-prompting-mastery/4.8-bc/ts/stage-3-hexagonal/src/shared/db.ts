// shared/db — спільний Postgres pool. Cross-cutting infra-утиліта.
import pg from "pg";

const { Pool } = pg;

export type DbPool = pg.Pool;

export function newPool(connectionString: string): DbPool {
  return new Pool({ connectionString });
}
