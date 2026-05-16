// Billing feature — model.
export interface Subscription {
  id: string;
  userId: string;
  plan: string;
  nextChargeAt: Date;
  createdAt: Date;
}
