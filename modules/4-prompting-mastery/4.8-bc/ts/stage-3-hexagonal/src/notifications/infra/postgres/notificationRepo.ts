import type { DbPool } from "../../../shared/db.js";
import type { Notification } from "../../domain/notification.js";
import type { Repository } from "../../domain/repository.js";

export class PgNotificationRepo implements Repository {
  constructor(private readonly db: DbPool) {}

  async save(n: Notification): Promise<void> {
    await this.db.query(
      `INSERT INTO notifications_messages (id, user_id, channel, payload, sent_at)
       VALUES ($1, $2, $3, $4, $5)`,
      [n.id, n.userId, n.channel, n.payload, n.sentAt],
    );
  }
}
