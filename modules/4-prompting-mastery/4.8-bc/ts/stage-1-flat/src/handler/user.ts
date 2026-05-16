import type { FastifyInstance } from "fastify";

import { InvalidCredentialsError } from "../service/user.js";
import type { UserService } from "../service/user.js";

interface CredsBody {
  email?: string;
  password?: string;
}

export function mountUser(app: FastifyInstance, svc: UserService): void {
  app.post<{ Body: CredsBody }>("/auth/register", async (req, reply) => {
    const { email, password } = req.body ?? {};
    if (!email || !password) {
      return reply.code(400).send({ error: "invalid_request" });
    }
    try {
      const u = await svc.register(email, password);
      return reply.code(201).send({ user_id: u.id, email: u.email });
    } catch (err) {
      req.log.error({ err }, "register failed");
      return reply.code(500).send({ error: "register_failed" });
    }
  });

  app.post<{ Body: CredsBody }>("/auth/login", async (req, reply) => {
    const { email, password } = req.body ?? {};
    if (!email || !password) {
      return reply.code(400).send({ error: "invalid_request" });
    }
    try {
      const u = await svc.login(email, password);
      return reply.code(200).send({ user_id: u.id, email: u.email });
    } catch (err) {
      if (err instanceof InvalidCredentialsError) {
        return reply.code(401).send({ error: "invalid_credentials" });
      }
      req.log.error({ err }, "login failed");
      return reply.code(500).send({ error: "login_failed" });
    }
  });
}
