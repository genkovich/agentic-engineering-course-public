// Commerce Bounded Context, доменні типи й event.
import type { DomainEvent } from "../../shared/events/bus.js";

export interface Order {
  id: string;
  userId: string;
  totalCents: number;
  status: string;
  createdAt: Date;
}

// OrderPlaced — domain event. Billing і Notifications BC підписуються.
export class OrderPlaced implements DomainEvent {
  static readonly EVENT_NAME = "commerce.OrderPlaced";
  readonly name: string = OrderPlaced.EVENT_NAME;

  constructor(
    public readonly orderId: string,
    public readonly userId: string,
    public readonly totalCents: number,
    public readonly at: Date,
  ) {}
}
