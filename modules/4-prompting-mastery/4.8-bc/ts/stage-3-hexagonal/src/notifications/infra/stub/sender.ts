// Заглушка Sender — логує у stdout. Для демо.
// Production-варіант жив би у notifications/infra/email/, notifications/infra/push/.
import type { Notification, Sender } from "../../domain/notification.js";

export class StubSender implements Sender {
  async send(n: Notification): Promise<void> {
    // eslint-disable-next-line no-console
    console.log(
      `[stub-sender] ${n.channel} -> user=${n.userId} payload=${JSON.stringify(n.payload)}`,
    );
    return Promise.resolve();
  }
}
