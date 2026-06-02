---
name: tdd
description: TDD-orchestrator що проганяє повний Red-Green-Refactor цикл через 3 ізольовані agents. Використовуй коли користувач каже `/tdd <story-id>` (наприклад `/tdd story-24-sm2`), або «прогон TDD циклу на story X», «запусти TDD pipeline», «зроби RGR на цій story». Послідовно викликає tdd-test-writer → tdd-implementer → tdd-refactorer через Agent tool, з automatic bash-gates між фазами. Підтримує опційний flag `--review-tests` для зупинки після RED і human review.
allowed-tools: Bash, Read, Agent
---

# tdd — orchestrator повного RGR циклу

Цей skill — диригент. Сам НЕ пише ні тестів, ні коду. Викликає 3 справжніх Claude Code agents (з `.claude/agents/`) через Agent tool, кожен у своєму isolated context. Між фазами виконує bash-гейти автоматично. На failure будь-якого гейту — STOP з actionable error.

Чому 3 окремі agents, а не 3 skill-виклики у одному контексті: skill виконується inline у тому самому context window головного агента. Agent tool створює окреме context window зі своїм system prompt. Тільки другий варіант дає реальний isolation, який лікує context pollution — головний аргумент Section 4 лекції 7.7.

## Inputs

З користувацького промпта витягни:
- `<story-id>` — обов'язково. Наприклад `story-24-sm2`. Має існувати файл `tasks/<story-id>.md`.
- `--review-tests` — опційний flag. Якщо є, після Phase 1 зупинитись і чекати на user input («continue» / «abort») перед запуском Phase 2. Це augmented coding варіант з Section 9 лекції.

## Pre-flight checks (виконати ПЕРЕД будь-якою фазою)

Виконай у Bash:

1. `git status --porcelain` — output має бути порожній.
   - Якщо ні: STOP з `Working tree not clean. Commit or stash changes before /tdd <story-id>.`
2. `test -f tasks/<story-id>.md && echo OK` — story-файл має існувати.
   - Якщо ні: STOP з `Story file tasks/<story-id>.md not found.`
3. `git rev-parse HEAD` — запам'ятай baseline SHA для фінального звіту.

## Phase 1 — RED (tdd-test-writer)

Виклич Agent tool:

```
Agent(
  subagent_type="tdd-test-writer",
  description="RED phase: write failing tests for <story-id>",
  prompt="Story: <story-id>. Read tasks/<story-id>.md and CLAUDE.md, then follow your standard RED-phase workflow: write failing tests in tests/, confirm pytest red, commit with `test(<scope>): add failing tests per AC` (scope = domain prefix from story), output `RED phase commit: <SHA>`. STOP after commit. Do not write implementation."
)
```

Дочекайся завершення. Витягни з output рядок `RED phase commit: <SHA>` — запиши як `RED_SHA`.

### Gate 1 — verify RED state

Виконай у Bash послідовно:

- `git log -1 --pretty=%s` — output має починатись з `test(`.
  - Якщо ні: STOP з `Phase 1 gate failed: last commit subject doesn't start with test(. Got: <subject>. SHA: <RED_SHA>.`
- `pytest -q; echo "EXIT:$?"` — exit code MUST be != 0 (тести мають падати).
  - Якщо EXIT:0: STOP з `Phase 1 gate failed: pytest passes after RED phase. Tests don't actually verify new behavior — they pass on empty implementation. SHA: <RED_SHA>.`

Якщо `--review-tests` flag присутній: STOP з:
```
Phase 1 complete (RED). Review tests via `git show <RED_SHA>`.
To continue: run `/tdd <story-id>` again (will re-detect RED state and skip to Phase 2).
To abort: `git reset --hard <baseline-SHA>`.
```

(Зауваж: для auto-continue після review треба, щоб Pre-flight #1 не зашкодив. Один з варіантів — користувач каже «continue» одним рядком, і skill стартує безпосередньо з Phase 2 без re-run pre-flight. Альтернатива — повний re-run, який детектить останній commit як RED і пропускає Phase 1.)

## Phase 2 — GREEN (tdd-implementer)

Виклич Agent tool:

```
Agent(
  subagent_type="tdd-implementer",
  description="GREEN phase: implement <story-id> to make tests pass",
  prompt="Story: <story-id>. Read tests/ (read-only) and interface stub in src/. Follow your standard GREEN-phase workflow: write minimal monolithic implementation in src/, drive pytest to green, commit with `feat(<scope>): implement to make tests pass`, output `GREEN phase commit: <SHA>`. STOP after commit. Do NOT modify any file under tests/."
)
```

Витягни `GREEN_SHA` з output.

### Gate 2 — verify GREEN state

Виконай у Bash:

- `git log -1 --pretty=%s` — output має починатись з `feat(`.
  - Якщо ні: STOP з `Phase 2 gate failed: last commit subject doesn't start with feat(. Got: <subject>. SHA: <GREEN_SHA>.`
- `pytest -q; echo "EXIT:$?"` — exit code MUST be 0.
  - Якщо ні: STOP з `Phase 2 gate failed: pytest still red after implementer. SHA: <GREEN_SHA>.`
- `git diff --name-only HEAD~1 HEAD -- tests/` — output MUST be порожній (тести не торкалися).
  - Якщо непорожній: STOP з `Phase 2 gate failed: implementer modified tests/. Hard rule violated. Files changed: <files>. SHA: <GREEN_SHA>.`

## Phase 3 — REFACTOR (tdd-refactorer)

Виклич Agent tool:

```
Agent(
  subagent_type="tdd-refactorer",
  description="REFACTOR phase: extract helpers for <story-id>",
  prompt="Story: <story-id>. Refactor src/ implementation: extract at least 2 private helpers based on natural branches per story rules, run pytest after each change. Commit with `refactor(<scope>): extract helpers`, output `REFACTOR phase commit: <SHA>`. STOP after commit. Tests are STRICTLY read-only."
)
```

Витягни `REFACTOR_SHA` з output.

### Gate 3 — verify REFACTOR state

Виконай у Bash:

- `git log -1 --pretty=%s` — output має починатись з `refactor(`.
  - Якщо ні: STOP з `Phase 3 gate failed: last commit subject doesn't start with refactor(. Got: <subject>. SHA: <REFACTOR_SHA>.`
- `pytest -q; echo "EXIT:$?"` — exit code MUST be 0.
  - Якщо ні: STOP з `Phase 3 gate failed: refactor broke tests. SHA: <REFACTOR_SHA>.`
- `git diff --name-only HEAD~1 HEAD -- tests/` — output MUST be порожній.
  - Якщо непорожній: STOP з `Phase 3 gate failed: refactorer modified tests/. SHA: <REFACTOR_SHA>. Files: <files>.`
- `grep -E '^\s*def _' src/<feature>.py | wc -l` (де `<feature>` витягається з commit-diff) — output MUST be ≥ 2 (мінімум 2 приватні helpers).
  - Якщо < 2: STOP з `Phase 3 gate failed: refactorer extracted only <n> helpers, expected ≥ 2. SHA: <REFACTOR_SHA>.`

## Final report

Виведи користувачу:

```
TDD pipeline complete for <story-id>.

Commits:
  RED      <RED_SHA>      test(<scope>): add failing tests per AC
  GREEN    <GREEN_SHA>    feat(<scope>): implement to make tests pass
  REFACTOR <REFACTOR_SHA> refactor(<scope>): extract helpers

Gates passed:
  ✓ Phase 1: pytest red after test-writer, commit subject = test(
  ✓ Phase 2: pytest green after implementer, tests/ untouched
  ✓ Phase 3: pytest green after refactorer, tests/ untouched, ≥ 2 helpers extracted

Inspect: git log --oneline -3
Verify isolation: git diff HEAD~3 HEAD -- tests/ (must be non-empty for RED phase only)
```

## Anti-patterns

- **Не виконуй фази inline.** Кожна фаза = окремий Agent tool call. Якщо пишеш тести сам у головному контексті — context pollution повернувся, semantic argument лекції зламано.
- **Не пропускай gates.** Gate 2 (`git diff -- tests/`) — критичний; без нього втрачаєш гарантію, що implementer не "виправив" тест.
- **Не намагайся "fix" failing agent.** Якщо agent не зміг закрити phase — це сигнал про story або стек. STOP, дай користувачу побачити helpful error. Pipeline не повинен "майже працювати".
- **Не амальгамуй commits.** 3 окремих commits — це observability layer. Squash-у не місце у цьому pipeline.

## Example invocations

```
User: /tdd story-24-sm2
You:  (run pre-flight → Phase 1 via Agent → Gate 1 via Bash → Phase 2 → Gate 2 → Phase 3 → Gate 3 → final report)

User: /tdd story-24-sm2 --review-tests
You:  (same as above, але STOP після Gate 1 з review prompt)

User: /tdd story-99-broken-tests  (де тести виявились зеленими після test-writer)
You:  STOP з "Phase 1 gate failed: pytest passes after RED phase..."
```
