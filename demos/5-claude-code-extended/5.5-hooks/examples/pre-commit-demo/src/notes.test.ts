import { beforeEach, describe, expect, it } from "vitest";
import {
  _resetStore,
  createNote,
  deleteNote,
  listNotes,
  readNote,
  updateNote,
} from "./notes.js";

describe("notes CRUD", () => {
  beforeEach(() => {
    _resetStore();
  });

  it("creates a note with id, title, body, createdAt", () => {
    const note = createNote("hello", "world");
    expect(note.id).toBeTypeOf("string");
    expect(note.title).toBe("hello");
    expect(note.body).toBe("world");
    expect(note.createdAt).toBeTypeOf("number");
  });

  it("reads a note by id", () => {
    const created = createNote("t", "b");
    expect(readNote(created.id)).toEqual(created);
  });

  it("updates a note via patch", () => {
    const created = createNote("old title", "old body");
    const updated = updateNote(created.id, { title: "new title" });
    expect(updated?.title).toBe("new title");
    expect(updated?.body).toBe("old body");
    expect(readNote(created.id)?.title).toBe("new title");
  });

  it("deletes a note", () => {
    const created = createNote("a", "b");
    expect(deleteNote(created.id)).toBe(true);
    expect(readNote(created.id)).toBeUndefined();
  });

  it("lists notes sorted by createdAt", () => {
    createNote("a", "1");
    createNote("b", "2");
    const all = listNotes();
    expect(all).toHaveLength(2);
    expect(all[0]!.createdAt).toBeLessThanOrEqual(all[1]!.createdAt);
  });
});
