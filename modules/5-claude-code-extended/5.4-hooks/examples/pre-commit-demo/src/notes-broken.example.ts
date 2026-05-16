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

// BUG: ignores `patch`, returns the original note unchanged.
// The "updates a note via patch" test will fail — that's exactly the
// failure pre-commit should catch before this gets committed.
export function updateNote(id: string, _patch: Partial<Omit<Note, "id" | "createdAt">>): Note | undefined {
  return store.get(id);
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
