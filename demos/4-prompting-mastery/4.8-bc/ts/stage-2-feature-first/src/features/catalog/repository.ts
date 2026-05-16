import type { DbPool } from "../../shared/db.js";
import type { Product } from "./model.js";

export class Repository {
  constructor(private readonly db: DbPool) {}

  async list(): Promise<Product[]> {
    const res = await this.db.query<{
      id: string;
      name: string;
      price_cents: string;
      category_id: string;
    }>(
      `SELECT id, name, price_cents, category_id FROM catalog_products ORDER BY name`,
    );
    return res.rows.map((r) => ({
      id: r.id,
      name: r.name,
      priceCents: Number(r.price_cents),
      categoryId: r.category_id,
    }));
  }
}
