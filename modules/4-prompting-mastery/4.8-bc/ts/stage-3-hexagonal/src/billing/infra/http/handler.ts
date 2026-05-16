// HTTP adapter для Billing BC.
import type { FastifyInstance } from "fastify";

import { AppError } from "../../../shared/apperr.js";
import { writeError } from "../../../shared/httputil.js";
import type { Service } from "../../app/service.js";
import { InvalidPlanError } from "../../domain/errors.js";

interface SubscribeReq {
  user_id?: string;
  plan?: string;
}

interface SubscribeResp {
  subscription_id: string;
  plan: string;
  next_charge_at: Date;
}

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export class Handler {
  constructor(private readonly svc: Service) {}

  register(app: FastifyInstance): void {
    app.post<{ Body: SubscribeReq }>("/subscriptions", async (req, reply) => {
      const body = req.body ?? {};
      if (!body.plan) {
        return reply.code(400).send({ error: "invalid_request" });
      }
      if (!body.user_id || !UUID_RE.test(body.user_id)) {
        return reply.code(400).send({ error: "invalid_user_id" });
      }
      try {
        const sub = await this.svc.subscribe(body.user_id, body.plan);
        const resp: SubscribeResp = {
          subscription_id: sub.id,
          plan: sub.plan,
          next_charge_at: sub.nextChargeAt,
        };
        return reply.code(201).send(resp);
      } catch (err) {
        if (err instanceof InvalidPlanError) {
          return writeError(
            reply,
            new AppError(
              InvalidPlanError.CODE,
              "plan must be basic|pro|enterprise",
              400,
            ),
          );
        }
        req.log.error({ err }, "subscribe failed");
        return writeError(reply, err);
      }
    });
  }
}
