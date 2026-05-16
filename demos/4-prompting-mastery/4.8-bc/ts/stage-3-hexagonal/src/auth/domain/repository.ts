// UserRepository — port. Реалізація живе в auth/infra/postgres.
import type { User } from "./user.js";

export interface UserRepository {
  create(u: User): Promise<void>;
  findByEmail(email: string): Promise<User | null>;
  findById(id: string): Promise<User | null>;
}
