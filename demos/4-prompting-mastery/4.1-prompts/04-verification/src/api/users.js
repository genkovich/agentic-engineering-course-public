import express from "express";
import { randomUUID } from "node:crypto";

export const usersRouter = express.Router();

usersRouter.post("/users", express.json(), (req, res) => {
  const { email, name } = req.body ?? {};

  if (
    typeof email !== "string" ||
    !email.includes("@") ||
    typeof name !== "string" ||
    name.length === 0
  ) {
    return res.status(400).json({ error: "validation_failed" });
  }

  return res.status(201).json({ id: randomUUID(), email, name });
});
