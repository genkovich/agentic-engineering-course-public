import type { Subscription } from "./subscription.js";

export interface Repository {
  create(s: Subscription): Promise<void>;
}
