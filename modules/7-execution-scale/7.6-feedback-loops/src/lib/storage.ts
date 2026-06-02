import type { Card } from "./cards";

const STORAGE_KEY = "card-review-queue";

// Завантажити збережений стан черги з localStorage.
// Повертає null, якщо нічого не збережено або дані пошкоджені.
export function loadQueue(): Card[] | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as Card[];
  } catch {
    return null;
  }
}

// Зберегти стан черги в localStorage.
//
// !!! ЗАСАДЖЕНИЙ БАГ (story-27, localStorage-регресія) !!!
// Ця функція ІСНУЄ і коректна — але App.tsx її НІКОЛИ не викликає.
// Тобто стан черги/оцінок живе тільки в пам'яті React; після reload сторінки
// все скидається на сід. Це регресія персистенції.
//
// Баг не ловиться ні юніт-тестом (функція сама по собі коректна), ні скріншотом
// (візуально до reload усе ок). Його ловить субагент-рев'юер: дивиться на git diff
// + AC ("стан переживає reload"), бачить, що saveQueue не викликається ніде в App,
// і повертає REJECT. Після фіксу (виклик saveQueue у відповідному ефекті) → ACCEPT.
export function saveQueue(queue: Card[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(queue));
}

// Очистити збережений стан (для тестів / "почати спочатку").
export function clearQueue(): void {
  localStorage.removeItem(STORAGE_KEY);
}
