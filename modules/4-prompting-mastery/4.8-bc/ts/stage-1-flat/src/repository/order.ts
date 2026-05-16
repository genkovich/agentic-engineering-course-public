import type { DbPool } from "../db.js";
import type { Order } from "../model/order.js";

export class OrderRepository {
  constructor(private readonly db: DbPool) {}

  async create(o: Order): Promise<void> {
    await this.db.query(
      `INSERT INTO orders (id, user_id, total_cents, status, created_at)
       VALUES ($1, $2, $3, $4, $5)`,
      [o.id, o.userId, o.totalCents, o.status, o.createdAt],
    );
  }
}
