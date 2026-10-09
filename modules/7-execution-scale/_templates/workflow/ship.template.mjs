// ship-<SCOPE> - шаблон динамічного workflow.
//
// Що це робить: доставляє кілька НЕЗАЛЕЖНИХ історій паралельно (фаза Implement),
// потім перевіряє кожну через збіжність (convergence) двох незалежних рецензентів
// (фаза Verify).
//
// Як користуватись: скопіюй у `.claude/workflows/ship-<scope>.mjs`, заміни
// плейсхолдери `<…>` під свій стек і заповни масив STORIES реальними історіями.
// Плейсхолдери: `<SCOPE>` (коротка назва набору історій, наприклад `tags` / `auth`),
// `<TEST_CMD>` (команда тестів, наприклад `pytest -q` / `go test ./...` / `npm test`).
//
// meta мусить бути чистим літералом (без змінних чи викликів усередині) - рантайм
// читає його ще до запуску тіла, щоб показати фази у списку `/workflows`.
export const meta = {
  name: 'ship-<SCOPE>',
  description: 'Deliver independent stories in parallel, verify each via convergence',
  phases: [{ title: 'Implement' }, { title: 'Verify' }],
}

// Передумова паралелі - НЕЗАЛЕЖНІСТЬ, а не оптимізація. Кожна історія пише РІВНО в
// свій файл, і множини файлів не перетинаються. Якщо дві історії чіпають один файл -
// прибери одну зі списку або зший їх послідовно; інакше паралельні гілки наступлять
// одна одній на запис. Заміни ці заготовки реальними історіями свого бэклогу.
const STORIES = [
  { id: '<SCOPE>-1', file: '<CODE_DIR>/feature_one.<EXT>', test: '<TEST_DIR>/feature_one.<EXT>' },
  { id: '<SCOPE>-2', file: '<CODE_DIR>/feature_two.<EXT>', test: '<TEST_DIR>/feature_two.<EXT>' },
  { id: '<SCOPE>-3', file: '<CODE_DIR>/feature_three.<EXT>', test: '<TEST_DIR>/feature_three.<EXT>' },
]

// ── Фаза Implement ──────────────────────────────────────────────────────────
// parallel() - барʼєр (barrier): запускає по одному agent() на історію ОДНОЧАСНО і
// чекає, поки завершаться ВСІ гілки, перш ніж віддати масив результатів. Тут барʼєр
// доречний, бо хочемо мати всю хвилю реалізованою перед перевіркою.
// (Для довшої хвилі краще pipeline(STORIES, implement, verify) - тоді кожна історія
// верифікується, щойно її збудовано, без чекання найповільнішого сусіда. pipeline -
// це конвеєр: елемент проходить наступний крок одразу, не чекаючи на решту.)
phase('Implement')
const built = await parallel(
  STORIES.map((s) => () =>
    agent(
      `Реалізуй ${s.id}: доведи ${s.test} до зеленого, змінюючи ТІЛЬКИ ${s.file}. ` +
        `Контракт - у docstring/коментарях функцій та tasks/story-${s.id.toLowerCase()}.md. ` +
        `Не чіпай тести і не торкайся чужих файлів коду. Запусти <TEST_CMD> на ${s.test}.`,
      { label: s.id, phase: 'Implement', schema: { id: 'string', file: 'string', green: 'boolean' } },
    ),
  ),
)

// ── Фаза Verify ─────────────────────────────────────────────────────────────
// Збіжність (convergence): на кожну реалізовану історію спавнимо ДВОХ незалежних
// рецензентів. Кожен наосліп перевіряє два твердження - тести зелені і тести
// незаймані. Лишаємо історію лише тоді, коли ОБИДВА рецензенти згодні (votes === 2):
// один агент може помилитись, згода двох незалежних - це і є сигнал, вартий довіри.
// Вкладений parallel() усередині pipeline() запускає двох рецензентів одночасно для
// кожної історії; зовнішній pipeline() жене історії конвеєром.
phase('Verify')
const confirmed = await pipeline(
  built,
  async (s) => {
    const reviews = await parallel(
      [1, 2].map((n) => () =>
        agent(
          `Рецензент #${n}, незалежно від інших: для ${s.id} запусти <TEST_CMD> на ` +
            `${STORIES.find((x) => x.id === s.id).test} і перевір, що (1) тести зелені, ` +
            `(2) git diff на теці тестів порожній. Поверни вердикт.`,
          { label: `${s.id}-review-${n}`, phase: 'Verify', schema: { passes: 'boolean', testsUntouched: 'boolean' } },
        ),
      ),
    )
    const votes = reviews.filter((r) => r && r.passes && r.testsUntouched).length
    return { id: s.id, confirmed: votes === 2 }
  },
)

const kept = confirmed.filter((v) => v.confirmed).map((v) => v.id)
log(`${kept.length}/${STORIES.length} історій підтверджено збіжністю: ${kept.join(', ')}`)

// Підсумок прогону - те, що рантайм поверне у сесію (саме результат, не транскрипт
// усіх агентів). Top-level await вище легальний у workflow-скрипті; підсумок віддаємо
// через export, щоб скрипт лишався валідним ES-модулем (bare top-level return впав би
// на `node --check`).
export const summary = { built, confirmed, kept }
