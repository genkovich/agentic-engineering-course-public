import { randomUUID } from "node:crypto";

import type { Order } from "../model/order.js";
import type { OrderRepository } from "../repository/order.js";

export class OrderService {
  constructor(private readonly repo: OrderRepository) {}

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
