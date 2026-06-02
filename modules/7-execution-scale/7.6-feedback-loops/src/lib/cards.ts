// Типи і сід-дані для черги карток. Це kata-абстракція ("картка на повторення"),
// а не модель якогось реального продукту.

export type Card = {
  id: string;
  front: string; // те, що бачить користувач (питання)
  back: string; // відповідь
  grade: number | null; // остання оцінка 1..5, або null якщо ще не оцінювали
};

// Захардкоджені сід-дані: рівно 3 картки у черзі.
export const seedCards: Card[] = [
  { id: "c1", front: "Що таке feedback loop?", back: "Цикл: дія → сигнал → корекція.", grade: null },
  { id: "c2", front: "Що таке off-by-one?", back: "Помилка на одиницю в індексі/межі.", grade: null },
  { id: "c3", front: "Що таке regression?", back: "Поломка того, що раніше працювало.", grade: null },
];
