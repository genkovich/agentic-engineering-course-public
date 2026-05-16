import type { FastifyInstance } from "fastify";

import { writeError } from "../../shared/httputil.js";
import type { Service } from "./service.js";

export class Handler {
  constructor(private readonly svc: Service) {}

  register(app: FastifyInstance): void {
    app.get("/products", async (req, reply) => {
      try {
        const products = await this.svc.list();
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
        return writeError(reply, err);
      }
    });
  }
}
