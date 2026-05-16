import { randomUUID } from "node:crypto";

import type { Subscription } from "../model/subscription.js";
import type { SubscriptionRepository } from "../repository/subscription.js";

export class SubscriptionService {
  constructor(private readonly repo: SubscriptionRepository) {}

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
