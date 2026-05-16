export interface Notification {
  id: string;
  userId: string;
  channel: string;
  payload: string;
  sentAt: Date | null;
}
