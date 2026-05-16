// shared/httputil — спільні HTTP helpers (JSON write + error mapping).
// Cross-cutting утиліти, мінімум — без бізнес-логіки.
import type { FastifyReply } from "fastify";

import { AppError, isAppError } from "./apperr.js";

export function writeError(reply: FastifyReply, err: unknown): FastifyReply {
  if (isAppError(err)) {
    return reply
      .code(err.statusCode)
      .send({ error: err.code, message: err.message });
  }
  return reply
    .code(500)
    .send({ error: "internal", message: "unexpected error" });
}

export { AppError };
