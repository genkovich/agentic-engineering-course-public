// ship-snippets - динамічний workflow, який доставляє три НЕЗАЛЕЖНІ сторіс
// (SNIP-3 search, SNIP-4 dedupe, SNIP-5 export) паралельно, потім перевіряє
// кожну через збіжність (convergence) двох незалежних рецензентів.
//
// meta мусить бути чистим літералом (без змінних/викликів усередині) - рантайм
// читає його ще до запуску тіла, щоб показати фази у /workflows.
export const meta = {
  name: 'ship-snippets',
  description: 'Deliver three independent snippet stories in parallel, verify each via convergence',
  phases: [{ title: 'Implement' }, { title: 'Verify' }],
}

// Три сторіс. Кожна пише РІВНО в свій файл - множини не перетинаються, тож
// паралелити безпечно (незалежність як передумова, а не оптимізація).
const STORIES = [
  { id: 'SNIP-3', file: 'src/snippets/search.py', test: 'tests/test_search.py' },
  { id: 'SNIP-4', file: 'src/snippets/dedupe.py', test: 'tests/test_dedupe.py' },
  { id: 'SNIP-5', file: 'src/snippets/export.py', test: 'tests/test_export.py' },
]

// ── Фаза Implement ──────────────────────────────────────────────────────────
// parallel() - барʼєр: запускає по одному agent() на сторіс ОДНОЧАСНО і чекає,
// поки завершаться всі гілки, перш ніж віддати масив результатів. Тут барʼєр
// доречний, бо хочемо мати всю хвилю реалізованою перед перевіркою.
// (Для довшої хвилі краще pipeline(STORIES, implement, verify) - тоді кожна
// сторіс верифікується, щойно її збудовано, без чекання найповільнішого сусіда.)
phase('Implement')
const built = await parallel(
  STORIES.map((s) => () =>
    agent(
      `Реалізуй ${s.id}: доведи ${s.test} до зеленого, змінюючи ТІЛЬКИ ${s.file}. ` +
        `Контракт - у docstring функцій та tasks/story-${s.id.toLowerCase()}.md. ` +
        `Не чіпай tests/ і не торкайся чужих файлів snippets/. Запусти pytest ${s.test} -q.`,
      { label: s.id, phase: 'Implement', schema: { id: 'string', file: 'string', green: 'boolean' } },
    ),
  ),
)

// ── Фаза Verify ─────────────────────────────────────────────────────────────
// Збіжність: на кожну реалізовану сторіс спавнимо ДВОХ незалежних рецензентів.
// Кожен наосліп перевіряє два твердження - тести зелені і tests/ незаймані.
// Лишаємо сторіс лише тоді, коли ОБИДВА рецензенти згодні (votes === 2): один
// агент може помилитись, згода двох незалежних - це і є сигнал, вартий довіри.
phase('Verify')
const confirmed = await pipeline(
  built,
  async (s) => {
    const reviews = await parallel(
      [1, 2].map((n) => () =>
        agent(
          `Рецензент #${n}, незалежно від інших: для ${s.id} запусти ${STORIES.find((x) => x.id === s.id).test} -q ` +
            `і перевір, що (1) тести зелені, (2) git diff -- tests/ порожній. Поверни вердикт.`,
          { label: `${s.id}-review-${n}`, phase: 'Verify', schema: { passes: 'boolean', testsUntouched: 'boolean' } },
        ),
      ),
    )
    const votes = reviews.filter((r) => r && r.passes && r.testsUntouched).length
    return { id: s.id, confirmed: votes === 2 }
  },
)

const kept = confirmed.filter((v) => v.confirmed).map((v) => v.id)
log(`${kept.length}/${STORIES.length} сторіс підтверджено збіжністю: ${kept.join(', ')}`)

// Підсумок прогону - те, що рантайм поверне у сесію (саме результат, не транскрипт
// усіх агентів). Top-level await вище легальний у workflow-скрипті; підсумок
// віддаємо через export, щоб скрипт лишався валідним ES-модулем.
export const summary = { built, confirmed, kept }
