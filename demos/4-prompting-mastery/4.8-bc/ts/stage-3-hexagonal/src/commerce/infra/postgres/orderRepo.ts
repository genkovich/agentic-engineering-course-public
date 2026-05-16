import type { DbPool } from "../../../shared/db.js";
import type { Order } from "../../domain/order.js";
import type { Repository } from "../../domain/repository.js";

export class PgOrderRepo implements Repository {
  constructor(private readonly db: DbPool) {}

  async create(o: Order): Promise<void> {
    await this.db.query(
      `INSERT INTO commerce_orders (id, user_id, total_cents, status, created_at)
       VALUES ($1, $2, $3, $4, $5)`,
      [o.id, o.userId, o.totalCents, o.status, o.createdAt],
    );
  }
}
