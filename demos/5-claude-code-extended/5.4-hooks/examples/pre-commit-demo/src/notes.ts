export type Note = {
  id: string;
  title: string;
  body: string;
  createdAt: number;
};

const store = new Map<string, Note>();

export function createNote(title: string, body: string): Note {
  const note: Note = {
    id: crypto.randomUUID(),
    title,
    body,
    createdAt: Date.now(),
  };
  store.set(note.id, note);
  return note;
}

export function readNote(id: string): Note | undefined {
  return store.get(id);
}

export function updateNote(id: string, patch: Partial<Omit<Note, "id" | "createdAt">>): Note | undefined {
  const current = store.get(id);
  if (!current) return undefined;
  const next: Note = { ...current, ...patch };
  store.set(id, next);
  return next;
}

export function deleteNote(id: string): boolean {
  return store.delete(id);
}

export function listNotes(): Note[] {
  return [...store.values()].sort((a, b) => a.createdAt - b.createdAt);
}

export function _resetStore(): void {
  store.clear();
}
