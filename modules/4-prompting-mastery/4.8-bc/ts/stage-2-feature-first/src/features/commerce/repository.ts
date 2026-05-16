import type { DbPool } from "../../shared/db.js";
import type { Order } from "./model.js";

export class Repository {
  constructor(private readonly db: DbPool) {}

  async create(o: Order): Promise<void> {
    await this.db.query(
      `INSERT INTO commerce_orders (id, user_id, total_cents, status, created_at)
       VALUES ($1, $2, $3, $4, $5)`,
      [o.id, o.userId, o.totalCents, o.status, o.createdAt],
    );
  }
}
