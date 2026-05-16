import type { FastifyInstance } from "fastify";

import { writeError } from "../../shared/httputil.js";
import { InvalidCredentialsError, Service } from "./service.js";

interface CredsBody {
  email?: string;
  password?: string;
}

export class Handler {
  constructor(private readonly svc: Service) {}

  register(app: FastifyInstance): void {
    app.post<{ Body: CredsBody }>("/auth/register", async (req, reply) => {
      const { email, password } = req.body ?? {};
      if (!email || !password) {
        return reply.code(400).send({ error: "invalid_request" });
      }
      try {
        const u = await this.svc.register(email, password);
        return reply.code(201).send({ user_id: u.id, email: u.email });
      } catch (err) {
        req.log.error({ err }, "register failed");
        return writeError(reply, err);
      }
    });

    app.post<{ Body: CredsBody }>("/auth/login", async (req, reply) => {
      const { email, password } = req.body ?? {};
      if (!email || !password) {
        return reply.code(400).send({ error: "invalid_request" });
      }
      try {
        const u = await this.svc.login(email, password);
        return reply.code(200).send({ user_id: u.id, email: u.email });
      } catch (err) {
        if (err instanceof InvalidCredentialsError) {
          return reply.code(401).send({ error: "invalid_credentials" });
        }
        req.log.error({ err }, "login failed");
        return writeError(reply, err);
      }
    });
  }
}
