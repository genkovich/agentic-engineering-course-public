// Postgres adapter для auth.UserRepository.
// Реалізує port, оголошений у auth/domain. Domain не знає про pg.
import type { DbPool } from "../../../shared/db.js";
import type { UserRepository } from "../../domain/repository.js";
import type { User } from "../../domain/user.js";

interface UserRow {
  id: string;
  email: string;
  password_hash: string;
  created_at: Date;
}

function rowToUser(r: UserRow): User {
  return {
    id: r.id,
    email: r.email,
    passwordHash: r.password_hash,
    createdAt: r.created_at,
  };
}

export class PgUserRepo implements UserRepository {
  constructor(private readonly db: DbPool) {}

  async create(u: User): Promise<void> {
    await this.db.query(
      `INSERT INTO auth_users (id, email, password_hash, created_at) VALUES ($1, $2, $3, $4)`,
      [u.id, u.email, u.passwordHash, u.createdAt],
    );
  }

  async findByEmail(email: string): Promise<User | null> {
    const res = await this.db.query<UserRow>(
      `SELECT id, email, password_hash, created_at FROM auth_users WHERE email = $1`,
      [email],
    );
    if (res.rowCount === 0) return null;
    return rowToUser(res.rows[0]!);
  }

  async findById(id: string): Promise<User | null> {
    const res = await this.db.query<UserRow>(
      `SELECT id, email, password_hash, created_at FROM auth_users WHERE id = $1`,
      [id],
    );
    if (res.rowCount === 0) return null;
    return rowToUser(res.rows[0]!);
  }
}
