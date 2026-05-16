import type { DbPool } from "../db.js";
import type { Product } from "../model/product.js";

export class ProductRepository {
  constructor(private readonly db: DbPool) {}

  async list(): Promise<Product[]> {
    const res = await this.db.query<{
      id: string;
      name: string;
      price_cents: string;
      category_id: string;
    }>(`SELECT id, name, price_cents, category_id FROM products ORDER BY name`);
    return res.rows.map((r) => ({
      id: r.id,
      name: r.name,
      priceCents: Number(r.price_cents),
      categoryId: r.category_id,
    }));
  }
}
