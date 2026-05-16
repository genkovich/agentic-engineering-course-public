import { randomUUID } from "node:crypto";

import type { Notification } from "../model/notification.js";
import type { NotificationRepository } from "../repository/notification.js";

export class NotificationService {
  constructor(private readonly repo: NotificationRepository) {}

  async sendTest(
    userId: string,
    channel: string,
    payload: string,
  ): Promise<Notification> {
    const now = new Date();
    const n: Notification = {
      id: randomUUID(),
      userId,
      channel,
      payload,
      sentAt: now,
    };
    // eslint-disable-next-line no-console
    console.log(
      `[stub-sender] ${channel} -> user=${userId} payload=${JSON.stringify(payload)}`,
    );
    await this.repo.create(n);
    return n;
  }
}
