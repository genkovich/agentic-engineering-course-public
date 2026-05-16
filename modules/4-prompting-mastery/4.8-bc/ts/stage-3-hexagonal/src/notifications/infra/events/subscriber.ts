// Підписники на події інших BC.
// Notifications — sink: слухає auth.UserRegistered, billing.SubscriptionCreated, commerce.OrderPlaced
// і викликає notifications/app/service.send.
//
// Імпорт чужих BC domain-ів припустимий ТУТ, бо це event subscription layer
// (за конвенцією — як і pub/sub topic name є cross-BC). dependency-cruiser config дозволяє це
// тільки для notifications/infra/events.
import { UserRegistered } from "../../../auth/domain/user.js";
import { SubscriptionCreated } from "../../../billing/domain/subscription.js";
import { OrderPlaced } from "../../../commerce/domain/order.js";
import type { EventBus } from "../../../shared/events/bus.js";
import type { Service } from "../../app/service.js";
import { CHANNEL_EMAIL } from "../../domain/notification.js";

export function registerSubscribers(bus: EventBus, svc: Service): void {
  bus.subscribe<UserRegistered>(UserRegistered.EVENT_NAME, async (e) => {
    try {
      await svc.send(e.userId, CHANNEL_EMAIL, "Welcome to our service!");
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("[notifications.subscriber] welcome email:", err);
    }
  });

  bus.subscribe<OrderPlaced>(OrderPlaced.EVENT_NAME, async (e) => {
    try {
      await svc.send(e.userId, CHANNEL_EMAIL, "Your order has been placed.");
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("[notifications.subscriber] order placed:", err);
    }
  });

  bus.subscribe<SubscriptionCreated>(
    SubscriptionCreated.EVENT_NAME,
    async (e) => {
      try {
        await svc.send(
          e.userId,
          CHANNEL_EMAIL,
          `Subscription confirmed: ${e.plan}`,
        );
      } catch (err) {
        // eslint-disable-next-line no-console
        console.error("[notifications.subscriber] subscription created:", err);
      }
    },
  );
}
