import type { DbPool } from "../../shared/db.js";
import type { Subscription } from "./model.js";

export class Repository {
  constructor(private readonly db: DbPool) {}

  async create(s: Subscription): Promise<void> {
    await this.db.query(
      `INSERT INTO billing_subscriptions (id, user_id, plan, next_charge_at, created_at)
       VALUES ($1, $2, $3, $4, $5)`,
      [s.id, s.userId, s.plan, s.nextChargeAt, s.createdAt],
    );
  }
}
