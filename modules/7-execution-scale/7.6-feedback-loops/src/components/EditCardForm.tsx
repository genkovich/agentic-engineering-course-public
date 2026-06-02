import { useState } from "react";
import type { Card } from "../lib/cards";

type Props = {
  card: Card;
  onSave: (updated: Card) => void;
  onCancel: () => void;
};

// Форма редагування картки. Еталон дизайну — baselines/edit-card-form.png.
//
// !!! ЗАСАДЖЕНИЙ БАГ (story-26, розбіжність із Figma-еталоном) !!!
// За еталоном кнопка "Скасувати" має внутрішній відступ 12px (px-3 → 0.75rem).
// Тут стоїть 8px (px-2 → 0.5rem). Кнопка візуально вужча за еталон.
//
// Баг не ловиться ні юніт-тестом, ні навіть Playwright-сценарієм поведінки
// (форма зберігає/скасовує коректно). Його ловить screenshot-diff проти
// baselines/edit-card-form.png: піксельна різниця у зоні кнопки > порогу.
export function EditCardForm({ card, onSave, onCancel }: Props) {
  const [front, setFront] = useState(card.front);
  const [back, setBack] = useState(card.back);

  return (
    <form
      data-testid="edit-card-form"
      className="rounded-xl border border-slate-300 bg-white p-6 shadow-sm"
      onSubmit={(e) => {
        e.preventDefault();
        onSave({ ...card, front, back });
      }}
    >
      <h2 className="mb-4 text-lg font-semibold text-slate-800">Редагувати картку</h2>

      <label className="mb-3 block">
        <span className="mb-1 block text-sm font-medium text-slate-600">Питання</span>
        <input
          data-testid="edit-front"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-slate-800"
          value={front}
          onChange={(e) => setFront(e.target.value)}
        />
      </label>

      <label className="mb-5 block">
        <span className="mb-1 block text-sm font-medium text-slate-600">Відповідь</span>
        <input
          data-testid="edit-back"
          className="w-full rounded-md border border-slate-300 px-3 py-2 text-slate-800"
          value={back}
          onChange={(e) => setBack(e.target.value)}
        />
      </label>

      <div className="flex justify-end gap-3">
        <button
          type="button"
          data-testid="cancel-button"
          onClick={onCancel}
          className="rounded-md border border-slate-300 px-2 py-2 font-medium text-slate-600 hover:bg-slate-100"
        >
          Скасувати
        </button>
        <button
          type="submit"
          data-testid="save-button"
          className="rounded-md bg-indigo-600 px-3 py-2 font-medium text-white hover:bg-indigo-700"
        >
          Зберегти
        </button>
      </div>
    </form>
  );
}
