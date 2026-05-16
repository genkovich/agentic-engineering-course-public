import type { FastifyInstance } from "fastify";

import { writeError } from "../../shared/httputil.js";
import type { Service } from "./service.js";

interface SendTestBody {
  user_id?: string;
  channel?: string;
  payload?: string;
}

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export class Handler {
  constructor(private readonly svc: Service) {}

  register(app: FastifyInstance): void {
    app.post<{ Body: SendTestBody }>(
      "/notifications/test",
      async (req, reply) => {
        const body = req.body ?? {};
        if (!body.user_id || !UUID_RE.test(body.user_id)) {
          return reply.code(400).send({ error: "invalid_user_id" });
        }
        const channel = body.channel || "email";
        const payload = body.payload || "test notification";
        try {
          const n = await this.svc.send(body.user_id, channel, payload);
          return reply.code(200).send({
            notification_id: n.id,
            channel: n.channel,
            sent_at: n.sentAt,
          });
        } catch (err) {
          req.log.error({ err }, "send notification failed");
          return writeError(reply, err);
        }
      },
    );
  }
}
