// shared/httputil — допоміжки для відповідей: error mapping → AppError.
import type { FastifyReply } from "fastify";

import { AppError, isAppError } from "./apperr.js";

export function writeError(reply: FastifyReply, err: unknown): FastifyReply {
  if (isAppError(err)) {
    return reply
      .code(err.statusCode)
      .send({ error: err.code, message: err.message });
  }
  return reply.code(500).send({ error: "internal" });
}

export { AppError };
