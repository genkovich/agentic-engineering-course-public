// Auth use cases. Залежить тільки від domain interfaces + shared/events.
import { randomUUID } from "node:crypto";
import bcrypt from "bcryptjs";

import type { EventBus } from "../../shared/events/bus.js";
import {
  EmailAlreadyExistsError,
  InvalidCredentialsError,
} from "../domain/errors.js";
import type { UserRepository } from "../domain/repository.js";
import { UserRegistered, type User } from "../domain/user.js";

interface PgLikeError {
  code?: unknown;
}

function isUniqueViolation(err: unknown): boolean {
  // Postgres unique violation SQLSTATE = 23505.
  const e = err as PgLikeError;
  return typeof e?.code === "string" && e.code === "23505";
}

export class Service {
  constructor(
    private readonly repo: UserRepository,
    private readonly bus: EventBus,
  ) {}

  async register(email: string, password: string): Promise<User> {
    const passwordHash = await bcrypt.hash(password, 10);
    const u: User = {
      id: randomUUID(),
      email,
      passwordHash,
      createdAt: new Date(),
    };
    try {
      await this.repo.create(u);
    } catch (err) {
      if (isUniqueViolation(err)) {
        throw new EmailAlreadyExistsError();
      }
      throw err;
    }
    await this.bus.publish(new UserRegistered(u.id, u.email, u.createdAt));
    return u;
  }

  async login(email: string, password: string): Promise<User> {
    const u = await this.repo.findByEmail(email);
    if (!u) throw new InvalidCredentialsError();
    const ok = await bcrypt.compare(password, u.passwordHash);
    if (!ok) throw new InvalidCredentialsError();
    return u;
  }
}
