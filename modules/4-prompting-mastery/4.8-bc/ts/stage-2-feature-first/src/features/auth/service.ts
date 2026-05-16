// Auth feature — service: реєстрація, логін.
// Vertical slice: handler, service, repository, model — всі в одній папці.
import { randomUUID } from "node:crypto";
import bcrypt from "bcryptjs";

import type { User } from "./model.js";
import type { Repository } from "./repository.js";

export class InvalidCredentialsError extends Error {
  constructor() {
    super("auth.invalid_credentials");
    this.name = "InvalidCredentialsError";
  }
}

export class Service {
  constructor(private readonly repo: Repository) {}

  async register(email: string, password: string): Promise<User> {
    const passwordHash = await bcrypt.hash(password, 10);
    const u: User = {
      id: randomUUID(),
      email,
      passwordHash,
      createdAt: new Date(),
    };
    await this.repo.create(u);
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
