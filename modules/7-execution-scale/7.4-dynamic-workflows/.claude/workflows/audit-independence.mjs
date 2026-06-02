// audit-independence - менший workflow: перевіряє ПЕРЕДУМОВУ паралелізму до
// будь-якого запису. На кожну сторіс спавнить N незалежних аудиторів, які
// наосліп звіряють, що файли цієї сторіс не перетинаються з файлами інших.
// Згода всіх аудиторів (збіжність) - підстава паралелити; будь-який перетин →
// блок із вердиктом, бо це гонка за запис.
export const meta = {
  name: 'audit-independence',
  description: 'Verify story file sets do not overlap before any parallel run (convergence audit)',
  phases: [{ title: 'Audit' }],
}

const STORIES = [
  { id: 'SNIP-3', files: ['src/snippets/search.py'] },
  { id: 'SNIP-4', files: ['src/snippets/dedupe.py'] },
  { id: 'SNIP-5', files: ['src/snippets/export.py'] },
]
const N = 2 // незалежних аудиторів на сторіс - згода всіх потрібна для PASS

phase('Audit')
const verdicts = await parallel(
  STORIES.map((s) => () => {
    const others = STORIES.filter((x) => x.id !== s.id).flatMap((x) => x.files)
    return parallel(
      Array.from({ length: N }, (_, i) => () =>
        agent(
          `Аудитор #${i + 1}, незалежно: чи ${s.id} (пише у ${s.files.join(', ')}) перетинається ` +
            `з файлами інших сторіс [${others.join(', ')}]? Перевір реальні writes у git diff. Поверни вердикт.`,
          { label: `${s.id}-audit-${i + 1}`, phase: 'Audit', schema: { overlap: 'boolean', sharedWrites: 'array' } },
        ),
      ),
    ).then((votes) => {
      const independent = votes.every((v) => v && v.overlap === false)
      return { id: s.id, independent }
    })
  }),
)

const blocked = verdicts.filter((v) => !v.independent).map((v) => v.id)
if (blocked.length) throw new Error(`overlap detected - re-split before parallel run: ${blocked.join(', ')}`)
log(`усі ${STORIES.length} сторіс незалежні (нуль перетину) → безпечно паралелити`)

// Підсумок аудиту - віддаємо через export, щоб скрипт лишався валідним ES-модулем.
export const summary = { verdicts, safeToParallelize: true }
