import type { DbPool } from "../db.js";
import type { Notification } from "../model/notification.js";

export class NotificationRepository {
  constructor(private readonly db: DbPool) {}

  async create(n: Notification): Promise<void> {
    await this.db.query(
      `INSERT INTO notifications (id, user_id, channel, payload, sent_at)
       VALUES ($1, $2, $3, $4, $5)`,
      [n.id, n.userId, n.channel, n.payload, n.sentAt],
    );
  }
}
