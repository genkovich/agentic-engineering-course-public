// Repository — port. Реалізація живе в catalog/infra/postgres.
import type { Product } from "./product.js";

export interface Repository {
  list(): Promise<Product[]>;
}
