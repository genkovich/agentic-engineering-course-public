// shared/events/bus — мінімальний in-memory event bus для cross-BC комунікації.
// BC-публікатор не знає про підписників. BC-підписник реєструє handler у своєму infra/events/.

export interface DomainEvent {
  readonly name: string;
}

export type Handler<E extends DomainEvent> = (e: E) => void | Promise<void>;

export class EventBus {
  private readonly handlers: Map<string, Handler<DomainEvent>[]> = new Map();

  subscribe<E extends DomainEvent>(name: string, h: Handler<E>): void {
    const list = this.handlers.get(name) ?? [];
    // Cast safely: handler bound to a specific event name receives that event.
    list.push(h as unknown as Handler<DomainEvent>);
    this.handlers.set(name, list);
  }

  async publish<E extends DomainEvent>(e: E): Promise<void> {
    const list = this.handlers.get(e.name);
    if (!list) return;
    for (const h of list) {
      await h(e);
    }
  }
}

export function newBus(): EventBus {
  return new EventBus();
}
