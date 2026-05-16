import type { FastifyInstance } from "fastify";

import { writeError } from "../../shared/httputil.js";
import type { Service } from "./service.js";

interface SubscribeBody {
  user_id?: string;
  plan?: string;
}

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export class Handler {
  constructor(private readonly svc: Service) {}

  register(app: FastifyInstance): void {
    app.post<{ Body: SubscribeBody }>("/subscriptions", async (req, reply) => {
      const body = req.body ?? {};
      if (!body.plan) {
        return reply.code(400).send({ error: "invalid_request" });
      }
      if (!body.user_id || !UUID_RE.test(body.user_id)) {
        return reply.code(400).send({ error: "invalid_user_id" });
      }
      try {
        const sub = await this.svc.subscribe(body.user_id, body.plan);
        return reply.code(201).send({
          subscription_id: sub.id,
          plan: sub.plan,
          next_charge_at: sub.nextChargeAt,
        });
      } catch (err) {
        req.log.error({ err }, "subscribe failed");
        return writeError(reply, err);
      }
    });
  }
}
