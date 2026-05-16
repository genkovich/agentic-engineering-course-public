// Billing Bounded Context, доменні типи й event.
import type { DomainEvent } from "../../shared/events/bus.js";

export interface Subscription {
  id: string;
  userId: string;
  plan: string;
  nextChargeAt: Date;
  createdAt: Date;
}

// SubscriptionCreated — Notifications підписується для welcome-letter.
export class SubscriptionCreated implements DomainEvent {
  static readonly EVENT_NAME = "billing.SubscriptionCreated";
  readonly name: string = SubscriptionCreated.EVENT_NAME;

  constructor(
    public readonly subscriptionId: string,
    public readonly userId: string,
    public readonly plan: string,
    public readonly at: Date,
  ) {}
}
