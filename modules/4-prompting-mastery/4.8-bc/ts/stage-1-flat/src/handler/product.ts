import type { FastifyInstance } from "fastify";

import type { ProductService } from "../service/product.js";

export function mountProduct(app: FastifyInstance, svc: ProductService): void {
  app.get("/products", async (req, reply) => {
    try {
      const products = await svc.list();
      return reply.code(200).send({
        products: products.map((p) => ({
          id: p.id,
          name: p.name,
          price_cents: p.priceCents,
          category_id: p.categoryId,
        })),
      });
    } catch (err) {
      req.log.error({ err }, "list products failed");
      return reply.code(500).send({ error: "list_failed" });
    }
  });
}
