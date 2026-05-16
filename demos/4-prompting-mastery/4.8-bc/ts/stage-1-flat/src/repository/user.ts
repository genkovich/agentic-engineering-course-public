import type { DbPool } from "../db.js";
import type { User } from "../model/user.js";

export class UserRepository {
  constructor(private readonly db: DbPool) {}

  async create(u: User): Promise<void> {
    await this.db.query(
      `INSERT INTO users (id, email, password_hash, created_at) VALUES ($1, $2, $3, $4)`,
      [u.id, u.email, u.passwordHash, u.createdAt],
    );
  }

  async findByEmail(email: string): Promise<User | null> {
    const res = await this.db.query<{
      id: string;
      email: string;
      password_hash: string;
      created_at: Date;
    }>(
      `SELECT id, email, password_hash, created_at FROM users WHERE email = $1`,
      [email],
    );
    if (res.rowCount === 0) return null;
    const r = res.rows[0]!;
    return {
      id: r.id,
      email: r.email,
      passwordHash: r.password_hash,
      createdAt: r.created_at,
    };
  }

  async findById(id: string): Promise<User | null> {
    const res = await this.db.query<{
      id: string;
      email: string;
      password_hash: string;
      created_at: Date;
    }>(
      `SELECT id, email, password_hash, created_at FROM users WHERE id = $1`,
      [id],
    );
    if (res.rowCount === 0) return null;
    const r = res.rows[0]!;
    return {
      id: r.id,
      email: r.email,
      passwordHash: r.password_hash,
      createdAt: r.created_at,
    };
  }
}
