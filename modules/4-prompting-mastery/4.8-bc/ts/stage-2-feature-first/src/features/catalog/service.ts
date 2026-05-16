// Catalog feature — service: продукти, категорії.
import type { Product } from "./model.js";
import type { Repository } from "./repository.js";

export class Service {
  constructor(private readonly repo: Repository) {}

  list(): Promise<Product[]> {
    return this.repo.list();
  }
}
