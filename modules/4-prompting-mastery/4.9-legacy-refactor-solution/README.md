# 4.9 Legacy Refactoring: пройдений цикл (solution)

Приклад до уроку **Legacy Refactoring без меж** з курсу «Agentic Engineering». Стартує з того самого коду, що й [`../4.9-legacy-refactor`](../4.9-legacy-refactor), і показує, як виглядає репозиторій після першого проходу протоколу.

Звіряй сюди після свого циклу, не копіюй. Якщо перенести ці файли до себе, тести стануть зелені, але спайка, критика і навмисного злому ти не зробиш, а саме їх урок і тренує. Твої артефакти вийдуть іншими, і це нормально: модель, формулювання і порядок кроків у кожного свої.

## Що тут є

| Файл / тека | Крок | Що подивитись |
|---|---|---|
| `SPIKE.md` | Step 1 | чотири критерії і verdict спайка |
| `LEGACY/account.md` | Step 2 | 6-секційне резюме legacy-модуля |
| `CRITIC.md` | Step 2 | статус кожного твердження з резюме: підтверджено / спростовано / невизначено |
| `PLAN.md` | Step 3 | скелет, дописаний із зелених тестів |
| `tests/account/{contract,characterization,architecture}/` | Step 3 | characterization-тести б'ють у legacy, known defects задокументовані тестами |
| `internal/account/` | Step 4 | новий модуль: `domain → app → infra → ports` |
| `server.py` | Step 4 | гібрид після cutover одного use case: `register` уже з `internal.account`, `verify_email` і `reset_password` ще з `internal.users` |
| `REFACTOR_LOG.md` | Step 4 | рядок про register cutover |

Цикл зупинено після register. Cutover `verify_email` і `reset_password` та видалення `internal/users/` сюди не входять. Тому в `server.py` гібрид: поки частина use case живе на legacy, DI-точка збирає обидві реалізації.

## Як запустити

```bash
cd modules/4-prompting-mastery/4.9-legacy-refactor-solution
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pytest -q          # 50 passed, 1 skipped (skip: архітектурний тест чекає, поки internal/users зникне)
python server.py   # App ready. account handlers: ['register', 'verify_email', 'reset_password']
```

Потрібен Python 3.12 або новіший, залежність лише одна, pytest.

`.claude/settings.json` тут той самий, що й у чистому старті: забороняє Claude редагувати `internal/users/**`. Діє, коли Claude запущено з цієї теки.

## Як звіряти

1. `diff -r ../4.9-legacy-refactor/internal/users internal/users` порожній: legacy під час циклу не правили.
2. Порівняй свій `CRITIC.md` з цим. Тут спростованих нуль, а невизначених 14, бо критик брав вибірку з 3 файлів із 6. Скільки вийшло в тебе і чому?
3. Зламай legacy навмисно (як в уроці) і подивись, які тести з `tests/account/characterization/` червоніють у тебе і тут.
4. Порівняй межі: `tests/account/architecture/test_layers.py` тут і у твоєму рішенні.
