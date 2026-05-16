// Billing feature — service: підписки.
import { randomUUID } from "node:crypto";

import type { Subscription } from "./model.js";
import type { Repository } from "./repository.js";

export class Service {
  constructor(private readonly repo: Repository) {}

  async subscribe(userId: string, plan: string): Promise<Subscription> {
    const now = new Date();
    const next = new Date(now);
    next.setMonth(next.getMonth() + 1);
    const sub: Subscription = {
      id: randomUUID(),
      userId,
      plan,
      nextChargeAt: next,
      createdAt: now,
    };
    await this.repo.create(sub);
    return sub;
  }
}
