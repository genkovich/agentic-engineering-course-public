// Notifications feature — service: відправка email/push.
import { randomUUID } from "node:crypto";

import type { Notification } from "./model.js";
import type { Repository } from "./repository.js";

export class Service {
  constructor(private readonly repo: Repository) {}

  async send(
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
    await this.repo.save(n);
    return n;
  }
}
