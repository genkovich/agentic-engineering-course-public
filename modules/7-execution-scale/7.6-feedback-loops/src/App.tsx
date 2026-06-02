import { useEffect, useState } from "react";
import type { Card } from "./lib/cards";
import { seedCards } from "./lib/cards";
import { gradeCard, removeFromQueue, replaceCard } from "./lib/queue";
import { loadQueue } from "./lib/storage";

export function App() {
  // Початковий стан: збережена черга з localStorage або сід.
  const [queue, setQueue] = useState<Card[]>(() => loadQueue() ?? seedCards);
  const [editingId, setEditingId] = useState<string | null>(null);

  // !!! ЗАСАДЖЕНИЙ БАГ (story-27, localStorage-регресія) !!!
  // Тут МАВ би бути ефект, що зберігає чергу при кожній зміні:
  //
  //   useEffect(() => { saveQueue(queue); }, [queue]);
  //
  // Його навмисно нема. saveQueue імпортована в storage.ts, але ніде не кличеться,
  // тож стан не переживає reload. Це і є регресія, яку ловить субагент-рев'юер.
  useEffect(() => {
    // (порожньо — персистенції нема)
  }, [queue]);

  function handleGrade(index: number, grade: number) {
    // 1) записати оцінку, 2) прибрати оцінену картку з черги.
    const graded = gradeCard(queue, index, grade);
    setQueue(removeFromQueue(graded, index));
  }

  function handleSaveEdit(updated: Card) {
    setQueue(replaceCard(queue, updated));
    setEditingId(null);
  }

  const editingCard = queue.find((c) => c.id === editingId) ?? null;

  return (
    <main className="mx-auto min-h-screen max-w-xl bg-slate-50 p-8">
      <h1 className="mb-1 text-2xl font-bold text-slate-900">Черга карток на повторення</h1>
      <p className="mb-6 text-sm text-slate-500">
        Оціни картку (1–5) — вона має зникнути з черги. Або відредагуй її.
      </p>

      {editingCard ? (
        <LazyEditForm card={editingCard} onSave={handleSaveEdit} onCancel={() => setEditingId(null)} />
      ) : (
        <ul data-testid="queue" className="flex flex-col gap-4">
          {queue.length === 0 && (
            <li data-testid="queue-empty" className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-slate-400">
              Черга порожня.
            </li>
          )}
          {queue.map((card, index) => (
            <li
              key={card.id}
              data-testid="card"
              data-card-id={card.id}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div className="mb-3 flex items-start justify-between gap-3">
                <span className="font-medium text-slate-800">{card.front}</span>
                <button
                  data-testid="edit-link"
                  onClick={() => setEditingId(card.id)}
                  className="shrink-0 text-sm text-indigo-600 hover:underline"
                >
                  Редагувати
                </button>
              </div>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((grade) => (
                  <button
                    key={grade}
                    data-testid="grade-button"
                    data-grade={grade}
                    onClick={() => handleGrade(index, grade)}
                    className="h-9 w-9 rounded-md border border-slate-300 text-slate-700 hover:bg-indigo-50"
                  >
                    {grade}
                  </button>
                ))}
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}

// Тонка обгортка, щоб тримати import форми поряд (форма у власному файлі).
import { EditCardForm } from "./components/EditCardForm";
function LazyEditForm(props: React.ComponentProps<typeof EditCardForm>) {
  return <EditCardForm {...props} />;
}
