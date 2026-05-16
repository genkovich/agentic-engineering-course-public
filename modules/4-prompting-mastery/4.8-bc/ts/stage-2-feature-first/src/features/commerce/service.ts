// Commerce feature — service: замовлення.
import { randomUUID } from "node:crypto";

import type { Order } from "./model.js";
import type { Repository } from "./repository.js";

export class Service {
  constructor(private readonly repo: Repository) {}

  async place(userId: string, totalCents: number): Promise<Order> {
    const o: Order = {
      id: randomUUID(),
      userId,
      totalCents,
      status: "pending",
      createdAt: new Date(),
    };
    await this.repo.create(o);
    return o;
  }
}
