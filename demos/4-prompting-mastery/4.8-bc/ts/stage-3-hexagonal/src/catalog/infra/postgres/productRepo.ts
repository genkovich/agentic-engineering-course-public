import type { DbPool } from "../../../shared/db.js";
import type { Product } from "../../domain/product.js";
import type { Repository } from "../../domain/repository.js";

interface ProductRow {
  id: string;
  name: string;
  price_cents: string;
  category_id: string;
}

export class PgProductRepo implements Repository {
  constructor(private readonly db: DbPool) {}

  async list(): Promise<Product[]> {
    const res = await this.db.query<ProductRow>(
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
