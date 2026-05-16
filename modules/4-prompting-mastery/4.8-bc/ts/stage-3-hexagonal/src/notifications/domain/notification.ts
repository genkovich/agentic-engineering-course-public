// Notifications Bounded Context.
// Notifications — sink BC: підписується на події інших BC і шле email/push/sms.

export type Channel = "email" | "push" | "sms";

export const CHANNEL_EMAIL: Channel = "email";
export const CHANNEL_PUSH: Channel = "push";
export const CHANNEL_SMS: Channel = "sms";

export interface Notification {
  id: string;
  userId: string;
  channel: Channel;
  payload: string;
  sentAt: Date | null;
}

// Sender — port. Реалізації живуть у notifications/infra/{email,push,stub}.
export interface Sender {
  send(n: Notification): Promise<void>;
}
