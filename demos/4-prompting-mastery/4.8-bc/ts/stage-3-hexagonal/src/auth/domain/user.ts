// Auth Bounded Context, доменні типи й event.
// Не імпортує net/http, БД, інші BC.
import type { DomainEvent } from "../../shared/events/bus.js";

export interface User {
  id: string;
  email: string;
  passwordHash: string;
  createdAt: Date;
}

// UserRegistered — domain event, публікується через event bus.
// Notifications BC підписується на нього для welcome-листа.
export class UserRegistered implements DomainEvent {
  static readonly EVENT_NAME = "auth.UserRegistered";
  readonly name: string = UserRegistered.EVENT_NAME;

  constructor(
    public readonly userId: string,
    public readonly email: string,
    public readonly at: Date,
  ) {}
}
