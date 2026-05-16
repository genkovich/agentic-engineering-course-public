import { describe, it, expect } from "vitest";
import express from "express";
import request from "supertest";
import { usersRouter } from "./users.js";

function makeApp() {
  const app = express();
  app.use(usersRouter);
  return app;
}

const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

describe("POST /users", () => {
  it("201 happy path", async () => {
    const res = await request(makeApp())
      .post("/users")
      .send({ email: "a@b.com", name: "Alice" });

    expect(res.status).toBe(201);
    expect(res.body.email).toBe("a@b.com");
    expect(res.body.name).toBe("Alice");
    expect(res.body.id).toMatch(UUID_V4);
  });

  it("400 on empty email", async () => {
    const res = await request(makeApp())
      .post("/users")
      .send({ email: "", name: "Alice" });

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "validation_failed" });
  });

  it("400 on email without @", async () => {
    const res = await request(makeApp())
      .post("/users")
      .send({ email: "no-at-sign", name: "Alice" });

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "validation_failed" });
  });

  it("400 on empty name", async () => {
    const res = await request(makeApp())
      .post("/users")
      .send({ email: "a@b.com", name: "" });

    expect(res.status).toBe(400);
    expect(res.body).toEqual({ error: "validation_failed" });
  });
});
