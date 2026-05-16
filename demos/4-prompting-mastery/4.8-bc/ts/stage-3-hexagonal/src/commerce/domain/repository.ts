import type { Order } from "./order.js";

export interface Repository {
  create(o: Order): Promise<void>;
}
