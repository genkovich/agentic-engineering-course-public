// HTTP adapter для Catalog BC.
import type { FastifyInstance } from "fastify";

import { writeError } from "../../../shared/httputil.js";
import type { Service } from "../../app/service.js";

interface ProductDTO {
  id: string;
  name: string;
  price_cents: number;
  category_id: string;
}

export class Handler {
  constructor(private readonly svc: Service) {}

  register(app: FastifyInstance): void {
    app.get("/products", async (req, reply) => {
      try {
        const products = await this.svc.list();
        const out: ProductDTO[] = products.map((p) => ({
          id: p.id,
          name: p.name,
          price_cents: p.priceCents,
          category_id: p.categoryId,
        }));
        return reply.code(200).send({ products: out });
      } catch (err) {
        req.log.error({ err }, "list products failed");
        return writeError(reply, err);
      }
    });
  }
}
