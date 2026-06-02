import { describe, it, expect } from "vitest";
import { sortQueue } from "./queue";
import type { Card } from "./cards";

// story-28 · review-order. ЦЕЙ ФАЙЛ ЧЕРВОНИЙ НА СТАРТІ (test-first):
// sortQueue поки стаб (повертає чергу без сортування). Скринкаст #1 — зробити його зеленим.
//
// Це і є детермінований гейт: pre-commit / Stop-hook / verify-gate ганяють `vitest run`,
// бачать червоне, блокують завершення. Повідомлення про падіння (очікував/отримав) — сигнал,
// за яким агент локалізує і виправляє.

const card = (id: string, grade: number | null): Card => ({ id, front: "", back: "", grade });

describe("sortQueue (story-28 · review-order)", () => {
  it("неоцінені (grade null) йдуть перші, далі оцінені за grade зростанням", () => {
    const input = [card("g3", 3), card("u", null), card("g1", 1)];
    // review-order: спершу неоцінена 'u', далі найнижча оцінка 'g1', потім 'g3'
    expect(sortQueue(input).map((c) => c.id)).toEqual(["u", "g1", "g3"]);
  });

  it("стабільний порядок для однакового grade (вхідний порядок зберігається)", () => {
    const input = [card("a", 2), card("b", 2), card("c", 1)];
    expect(sortQueue(input).map((c) => c.id)).toEqual(["c", "a", "b"]);
  });

  it("є чистою функцією — НЕ мутує вхідний масив", () => {
    const input = [card("g2", 2), card("u", null)];
    const before = input.map((c) => c.id);
    sortQueue(input);
    expect(input.map((c) => c.id)).toEqual(before); // вхід має лишитись незмінним
  });
});
