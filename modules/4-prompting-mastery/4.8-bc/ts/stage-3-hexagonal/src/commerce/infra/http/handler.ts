// HTTP adapter для Commerce BC.
import type { FastifyInstance } from "fastify";

import { writeError } from "../../../shared/httputil.js";
import type { Service } from "../../app/service.js";

interface PlaceReq {
  user_id?: string;
  total_cents?: number;
}

interface PlaceResp {
  order_id: string;
  status: string;
}

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export class Handler {
  constructor(private readonly svc: Service) {}

  register(app: FastifyInstance): void {
    app.post<{ Body: PlaceReq }>("/orders", async (req, reply) => {
      const body = req.body ?? {};
      if (!body.user_id || !UUID_RE.test(body.user_id)) {
        return reply.code(400).send({ error: "invalid_user_id" });
      }
      if (typeof body.total_cents !== "number") {
        return reply.code(400).send({ error: "invalid_request" });
      }
      try {
        const o = await this.svc.place(body.user_id, body.total_cents);
        const resp: PlaceResp = { order_id: o.id, status: o.status };
        return reply.code(201).send(resp);
      } catch (err) {
        req.log.error({ err }, "place order failed");
        return writeError(reply, err);
      }
    });
  }
}
