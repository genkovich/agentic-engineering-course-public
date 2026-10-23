# 4.1-prompts

Демо до уроку «Як писати промпти». Чотири невеликі теки, на яких видно, як промпт змінює те, що робить Claude Code. Промпти лежать у `PROMPTS.md`.

## Що потрібно

- Claude Code
- Node.js з npm (для `01-refactor` і `04-verification`)
- Go (для `03-race-condition`)

## Підготовка

```bash
cd ~/sources/agentic-engineering-course-public/modules/4-prompting-mastery/4.1-prompts
bash setup.sh
```

`setup.sh` ставить npm-залежності. Окремі git-репозиторії він не створює, тека живе у клоні курсу.

## Як повернути теку в початковий стан

Між прогонами двох промптів на тій самій задачі поверніть теку до стану з репозиторію. Команди запускайте з теки демо, наприклад з `01-refactor`:

```bash
git restore .
git clean -fd .
```

`git restore .` відкочує зміни у файлах, `git clean -fd .` прибирає нові файли, які створив Claude (наприклад, тести). `node_modules` лишається: його ігнорує `.gitignore` курсу. Після цього почніть нову сесію Claude Code (`/clear` або перезапуск `claude`).

## Теки

| Тека | Що всередині | Промпт | Успіх |
|---|---|---|---|
| `01-refactor` | `src/auth/parser.ts`: функція `parseUser`, у якій разом валідація і мапінг у домен. Тестів немає | 1A і 1B | після 1B є тести, `npm test` зелений; подивіться, чи тести ловлять `age: NaN` |
| `02-few-shot` | порожня тека для сесії | 2A і 2B | порівняйте стиль відповідей |
| `03-race-condition` | `counter.go`: 1000 goroutines без синхронізації | 3 | `go run -race counter.go` показує `expected: 1000, got: 1000` і жодного `DATA RACE` |
| `04-verification` | заготовка `src/api/users.js` без handler і без тестів | 4 | Claude сам пише handler і тести, запускає `npm test`, виправляє, поки не стане зелено |

До старту `npm test` у `01-refactor` і `04-verification` проходить без тестів: їх має написати Claude.
