// Commerce use case — створення замовлення.
import { randomUUID } from "node:crypto";

import type { EventBus } from "../../shared/events/bus.js";
import { InvalidOrderError } from "../domain/errors.js";
import { OrderPlaced, type Order } from "../domain/order.js";
import type { Repository } from "../domain/repository.js";

export class Service {
  constructor(
    private readonly repo: Repository,
    private readonly bus: EventBus,
  ) {}

  async place(userId: string, totalCents: number): Promise<Order> {
    if (totalCents < 0) throw new InvalidOrderError();

    const o: Order = {
      id: randomUUID(),
      userId,
      totalCents,
      status: "pending",
      createdAt: new Date(),
    };
    await this.repo.create(o);
    await this.bus.publish(
      new OrderPlaced(o.id, o.userId, o.totalCents, o.createdAt),
    );
    return o;
  }
}
