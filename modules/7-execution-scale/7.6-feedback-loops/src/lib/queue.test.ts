import { describe, it, expect } from "vitest";
import { gradeCard, removeFromQueue, replaceCard } from "./queue";
import type { Card } from "./cards";

function q(): Card[] {
  return [
    { id: "c1", front: "A", back: "a", grade: null },
    { id: "c2", front: "B", back: "b", grade: null },
    { id: "c3", front: "C", back: "c", grade: null },
  ];
}

// ВАЖЛИВО (teaching point для лекції 7.6):
//
// removeFromQueue має баг off-by-one: splice(index + 1) замість splice(index).
// Але цей тест НАПИСАНО під поточну поведінку коду — він описує те, що функція
// робить, а не те, чого від неї хоче користувач. Тому він ЗЕЛЕНИЙ.
//
// Юніт-тест зеленый, а в браузері: оцінюєш ПЕРШУ картку (index 0), а зникає
// ДРУГА. Цей розрив "тест ок / поведінка зламана" і є суть уроку: юніт-канал
// не ловить такі баги. Їх ловить Playwright MCP, що клікає в реальному UI.
//
// Коли баг виправлять (splice(index, 1)), цей тест стане ЧЕРВОНИМ — і це
// сигнал переписати очікування під реальний контракт (видаляємо картку за index).
describe("removeFromQueue (засаджений off-by-one)", () => {
  it("видаляє СУСІДНЮ картку — закріплює поточну (баговану) поведінку", () => {
    const result = removeFromQueue(q(), 0);
    // Очікуємо, що лишилися c1 і c3: тобто splice прибрав c2 (index+1).
    // Користувач очікував би c2+c3 (прибрати c1), але код видаляє сусіда.
    expect(result.map((c) => c.id)).toEqual(["c1", "c3"]);
  });

  it("довжина черги зменшується на 1", () => {
    expect(removeFromQueue(q(), 0)).toHaveLength(2);
  });
});

// Решта функцій коректні — звичайні зелені тести.
describe("gradeCard", () => {
  it("записує оцінку за позицією", () => {
    const result = gradeCard(q(), 0, 5);
    expect(result[0].grade).toBe(5);
    expect(result[1].grade).toBeNull();
  });
});

describe("replaceCard", () => {
  it("замінює картку за id", () => {
    const updated: Card = { id: "c2", front: "B!", back: "b!", grade: 4 };
    const result = replaceCard(q(), updated);
    expect(result[1]).toEqual(updated);
  });
});
