# Trigger: auto-format (recipe-1)

Демонструє slide 6.1 — PostToolUse + matcher `Edit|Write` запускає formatter за розширенням файлу одразу після write.

## Передумова

У PATH є хоча б один formatter:
- **TypeScript/JS/JSON/MD/CSS/HTML** — `prettier` (через `npm i -g prettier` або локально через npx)
- **Python** — `black` (через `pip install black`)
- **Go** — `gofmt` (іде з Go toolchain)
- **Rust** — `rustfmt` (іде з Rust toolchain)

Якщо formatter відсутній — recipe-1 тихо exit 0 (не блокує, просто пропускає). Це навмисно.

## Промпт для Claude (копі-паст)

> Створи файл `src/foo.ts` з функцією `add(a, b)` яка повертає `a + b`. Не дотримуйся форматування — пиши «брудно», у одну довжелезну строку, без пробілів навколо `=` і `+`, з зайвими подвійними пробілами всередині. Я хочу побачити, як hook автоматично відформатує файл після write.

## Що має статись

1. Claude використає Write tool на `src/foo.ts` з «брудним» вмістом
2. Write завершується успішно — файл записаний
3. PostToolUse hook `recipe-1-auto-format.sh` спрацьовує (matcher: `Edit|Write`)
4. Скрипт читає stdin, витягує `tool_input.file_path` через python3, бачить `*.ts` → викликає `prettier --write src/foo.ts`
5. Файл миттєво відформатований prettier'ом — пробіли, переноси рядків, semicolons як треба
6. У терміналі: `cat src/foo.ts` показує охайний код, `git diff` теж

## На чому акцентувати у скринкасті

- **PostToolUse не блокує** — Claude не дізнається, що hook щось зробив. Side-effect, не gate
- **case по розширенню** — `*.ts → prettier`, `*.py → black`, `*.go → gofmt`. Розширь під свій стек у `recipe-1-auto-format.sh:21-34`
- **Тиха degradation** — якщо prettier не встановлений, hook все ще exit 0 (рядок `command -v prettier >/dev/null 2>&1 && ... || true`). Це принципово для observability-style hooks: не валити основний flow

## Як перевірити в isolation (без Claude)

```bash
# Створи тимчасовий файл "брудного" коду
echo "const   add  =(a,b)=>{return a+b;};" > /tmp/foo.ts

# Прокинь payload, що вказує на цей файл
echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/foo.ts","content":""}}' \
  | bash .claude/hooks/recipe-1-auto-format.sh

# Файл уже відформатований
cat /tmp/foo.ts
# → const add = (a, b) => {
#     return a + b;
#   };

rm /tmp/foo.ts
```

Auto-runner `make test-hooks` теж викликає recipe-1 на `payloads/protect-clean.json` (просто перевіряє, що скрипт не падає; реальне форматування — у живій сесії, бо потрібен файл на диску).

## Очищення

```bash
rm src/foo.ts
```
