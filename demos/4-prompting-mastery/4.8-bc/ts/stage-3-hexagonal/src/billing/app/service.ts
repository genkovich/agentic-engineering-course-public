// Billing use case — оформлення підписки.
import { randomUUID } from "node:crypto";

import type { EventBus } from "../../shared/events/bus.js";
import { InvalidPlanError } from "../domain/errors.js";
import type { Repository } from "../domain/repository.js";
import {
  SubscriptionCreated,
  type Subscription,
} from "../domain/subscription.js";

const VALID_PLANS = new Set(["basic", "pro", "enterprise"]);

export class Service {
  constructor(
    private readonly repo: Repository,
    private readonly bus: EventBus,
  ) {}

  async subscribe(userId: string, plan: string): Promise<Subscription> {
    if (!VALID_PLANS.has(plan)) throw new InvalidPlanError();

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
    await this.bus.publish(
      new SubscriptionCreated(sub.id, sub.userId, sub.plan, sub.createdAt),
    );
    return sub;
  }
}
