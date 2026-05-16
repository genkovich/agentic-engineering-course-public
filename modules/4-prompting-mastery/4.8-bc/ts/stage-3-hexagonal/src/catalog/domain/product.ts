// Catalog Bounded Context, доменні типи й порти.
// Read-only BC — без published events на цьому етапі.

export interface Product {
  id: string;
  name: string;
  priceCents: number;
  categoryId: string;
}
