// HTTP adapter для Auth BC.
import type { FastifyInstance } from "fastify";

import { writeError } from "../../../shared/httputil.js";
import type { Service } from "../../app/service.js";
import type {
  LoginReq,
  LoginResp,
  RegisterReq,
  RegisterResp,
} from "./dto.js";
import { toAPIError } from "./errors.js";

export class Handler {
  constructor(private readonly svc: Service) {}

  register(app: FastifyInstance): void {
    app.post<{ Body: RegisterReq }>("/auth/register", async (req, reply) => {
      const { email, password } = req.body ?? {};
      if (!email || !password) {
        return reply.code(400).send({ error: "invalid_request" });
      }
      try {
        const u = await this.svc.register(email, password);
        const resp: RegisterResp = {
          user_id: u.id,
          email: u.email,
          created_at: u.createdAt,
        };
        return reply.code(201).send(resp);
      } catch (err) {
        req.log.error({ err }, "register failed");
        return writeError(reply, toAPIError(err));
      }
    });

    app.post<{ Body: LoginReq }>("/auth/login", async (req, reply) => {
      const { email, password } = req.body ?? {};
      if (!email || !password) {
        return reply.code(400).send({ error: "invalid_request" });
      }
      try {
        const u = await this.svc.login(email, password);
        const resp: LoginResp = { user_id: u.id, email: u.email };
        return reply.code(200).send(resp);
      } catch (err) {
        req.log.error({ err }, "login failed");
        return writeError(reply, toAPIError(err));
      }
    });
  }
}
