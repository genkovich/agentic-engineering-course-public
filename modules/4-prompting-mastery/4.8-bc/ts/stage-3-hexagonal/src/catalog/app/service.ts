// Catalog use case — список продуктів.
import type { Product } from "../domain/product.js";
import type { Repository } from "../domain/repository.js";

export class Service {
  constructor(private readonly repo: Repository) {}

  list(): Promise<Product[]> {
    return this.repo.list();
  }
}
