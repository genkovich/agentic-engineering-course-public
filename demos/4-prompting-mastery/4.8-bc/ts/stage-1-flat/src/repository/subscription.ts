import type { DbPool } from "../db.js";
import type { Subscription } from "../model/subscription.js";

export class SubscriptionRepository {
  constructor(private readonly db: DbPool) {}

  async create(s: Subscription): Promise<void> {
    await this.db.query(
      `INSERT INTO subscriptions (id, user_id, plan, next_charge_at, created_at)
       VALUES ($1, $2, $3, $4, $5)`,
      [s.id, s.userId, s.plan, s.nextChargeAt, s.createdAt],
    );
  }
}
