---
name: legacy-tests
description: Use when running Step 3.2 of legacy refactoring protocol — generates contract/characterization/architecture tests for the new module before any cutover. Triggers on '/legacy-tests <module>' or when user asks to 'згенерувати тести для legacy', 'characterization tests', 'fix point of reference'.
argument-hint: <module-name>
allowed-tools: Read, Write, Edit, Bash, Glob
disable-model-invocation: false
---

# legacy-tests — Step 3.2 фіксація поведінки тестами

Генерує три обовʼязкові типи тестів у `tests/<module>/` + два опційні. Усі мають бути зелені на legacy-реалізації перед finalize-плану.

## Аргументи

- `<module-name>` — імʼя нового модуля.

## Inputs

- `LEGACY/<module>.md` (Step 2)
- `PLAN.md` skeleton (Step 3.1) — для public interface

## Three obligatory test types

### 1. Contract tests — `tests/<module>/contract/`

Перевіряють що public interface поводить себе як описано у `apps/api/openapi.yaml` (відповіді, статус-коди, формат). Не перевіряють внутрішню логіку.

### 2. Characterization tests — `tests/<module>/characterization/`

Параметризовані тести з 15-20 кейсами вхід→вихід (кейси беруться з `LEGACY/<module>.md` секція 4 + доповнюються через subagent).

### 3. Architecture tests — `tests/<module>/architecture/`

Перевіряють що нова архітектура `domain → app → infra → ports` дотримана. Через `import-linter` або `pytest`-кастомні правила:

```python
# tests/account/architecture/test_layers.py
import pytest
import importlib
import inspect

def test_domain_does_not_import_infra():
    domain = importlib.import_module("internal.account.domain")
    src = inspect.getsource(domain)
    assert "internal.account.infra" not in src, "domain не має знати про infra"
```

Або через `.importlinter` config + `lint-imports`.

## Optional (nice to have)

### 4. Integration tests — `tests/<module>/integration/`

Через FastAPI `TestClient`, перевіряють повний HTTP-флоу.

### 5. Unit tests — `tests/<module>/unit/`

Точкові тести на domain validators (для edge cases hypothesis-based).

## Subagent для генерації characterization-кейсів

```
Read LEGACY/<module>.md + public interface з PLAN.md skeleton.
Поверни 15-20 пар вхід→вихід у форматі:

@pytest.mark.parametrize("input1,input2,expected", [
  ("...", "...", "..."),
  ...
])

Включи:
- Усі приклади з LEGACY секція 4
- Edge cases: empty, very long, unicode, duplicates
- Error cases: invalid format, taken value, expired token
- Race condition cases (rate limit, concurrent register)

Без імплементації тесту, тільки список кейсів і необхідні моки.
```

## Acceptance criteria

- `tests/<module>/{contract,characterization,architecture}/` створені
- Кожна папка має ≥1 `test_*.py` файл
- characterization має 15-20 кейсів через `parametrize`
- architecture перевіряє хоча б 1 layer constraint
- `pytest tests/<module>` зелений
- Тести **не використовують** мовчазних мокіів — кожен мок або підтверджує виклик через `mock.assert_called_with(...)`, або не використовується

## Verification: smell-test через "deliberate breakage"

Перед тим як finalize-плану — тимчасово зламай legacy реалізацію:

```bash
# у internal/users/registration.py замінити return на None
sed -i.bak 's/return {"status"/return None  # broken/' internal/users/registration.py
pytest tests/account/  # має почервоніти
mv internal/users/registration.py.bak internal/users/registration.py
pytest tests/account/  # знов зелено
```

Якщо breakage не червонить тест — це привид. Виправ, потім finalize.

## Examples

```
/legacy-tests account
pytest tests/account/  # has to be green
/legacy-plan account --phase=finalize
```

## Anti-patterns

- **Не дозволь subagent повертати тест із `assert True`** — це привид. Skill валідовує: `grep "assert True" tests/<module>` має дати 0 матчів.
- **Не мокай так, щоби мок повертав None** — це призводить до silent pass. Кожен мок має або реальний return value, або `assert_called_with`.
- **Не лий усі тести в один файл** — три типи тестів живуть у трьох папках, інакше характеристичні і архітектурні мішаються і ламається структура звіту.
