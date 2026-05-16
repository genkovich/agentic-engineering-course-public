// Notifications use case — головний Send. Викликається і HTTP handler-ом,
// і event subscriber-ами.
import { randomUUID } from "node:crypto";

import type {
  Channel,
  Notification,
  Sender,
} from "../domain/notification.js";
import type { Repository } from "../domain/repository.js";

export class Service {
  constructor(
    private readonly repo: Repository,
    private readonly sender: Sender,
  ) {}

  async send(
    userId: string,
    channel: Channel,
    payload: string,
  ): Promise<Notification> {
    const n: Notification = {
      id: randomUUID(),
      userId,
      channel,
      payload,
      sentAt: null,
    };
    await this.sender.send(n);
    n.sentAt = new Date();
    await this.repo.save(n);
    return n;
  }
}
