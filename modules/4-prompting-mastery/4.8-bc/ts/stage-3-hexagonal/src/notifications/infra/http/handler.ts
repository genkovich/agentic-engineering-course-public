// HTTP adapter для Notifications BC.
import type { FastifyInstance } from "fastify";

import { writeError } from "../../../shared/httputil.js";
import type { Service } from "../../app/service.js";
import { CHANNEL_EMAIL, type Channel } from "../../domain/notification.js";

interface SendTestReq {
  user_id?: string;
  channel?: string;
  payload?: string;
}

interface SendTestResp {
  notification_id: string;
  channel: string;
  sent_at: Date | null;
}

const UUID_RE =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function asChannel(s: string | undefined): Channel {
  if (s === "email" || s === "push" || s === "sms") return s;
  return CHANNEL_EMAIL;
}

export class Handler {
  constructor(private readonly svc: Service) {}

  register(app: FastifyInstance): void {
    app.post<{ Body: SendTestReq }>(
      "/notifications/test",
      async (req, reply) => {
        const body = req.body ?? {};
        if (!body.user_id || !UUID_RE.test(body.user_id)) {
          return reply.code(400).send({ error: "invalid_user_id" });
        }
        const channel = asChannel(body.channel);
        const payload = body.payload || "test notification";
        try {
          const n = await this.svc.send(body.user_id, channel, payload);
          const resp: SendTestResp = {
            notification_id: n.id,
            channel: n.channel,
            sent_at: n.sentAt,
          };
          return reply.code(200).send(resp);
        } catch (err) {
          req.log.error({ err }, "send notification failed");
          return writeError(reply, err);
        }
      },
    );
  }
}
