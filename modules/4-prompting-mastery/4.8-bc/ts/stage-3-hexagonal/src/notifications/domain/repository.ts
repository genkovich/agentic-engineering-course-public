import type { Notification } from "./notification.js";

export interface Repository {
  save(n: Notification): Promise<void>;
}
