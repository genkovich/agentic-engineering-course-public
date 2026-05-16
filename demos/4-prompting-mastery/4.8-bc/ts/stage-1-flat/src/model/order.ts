export interface Order {
  id: string;
  userId: string;
  totalCents: number;
  status: string;
  createdAt: Date;
}
