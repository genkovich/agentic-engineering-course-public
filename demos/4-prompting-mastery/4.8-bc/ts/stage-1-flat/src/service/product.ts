import type { Product } from "../model/product.js";
import type { ProductRepository } from "../repository/product.js";

export class ProductService {
  constructor(private readonly repo: ProductRepository) {}

  list(): Promise<Product[]> {
    return this.repo.list();
  }
}
