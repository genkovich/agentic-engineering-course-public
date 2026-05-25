---
name: api-forge
description: >
  Use when user wants to generate API contract (OpenAPI 3.1 / GraphQL / async events)
  per SDLC stage 10 (api-contracts) protocol. Triggers on "api-forge for {slug}",
  "API for {slug}", "openapi for {feature}", "GraphQL schema", "AsyncAPI",
  "events for {feature}", "stage 10 for {slug}", "/sdlc-api-forge {slug}".
  Output: docs/features/{slug}/contracts/openapi.yaml + docs/features/{slug}/contracts/api-sync-report.md
  + contracts/events.md (if async).
  Hard gate: docs/features/{slug}/PRD.md (stage 03). data-model.md (stage 08)
  is recommended but optional — without it the skill runs in scenario B
  (PRD + sequences only) and fills `unresolved_origins` in the sync report.
  Renamed from `define-api` in v3.3.0; the legacy name is kept as a deprecation wrapper.
stage: "10"
---

# Skill: api-forge (SDLC stage 10)

Generator of API contract: **OpenAPI 3.1** for synchronous HTTP APIs + AsyncAPI / events.md for events. Clear error model (`{code, message, details?}`), cursor pagination, URL versioning, BearerAuth defaults. The contract is **never written by hand** — it is the deterministic output of reading the source-of-truth artifacts (`data-model.md`, sequence diagrams, PRD §4) and projecting them into OpenAPI 3.1 schema. Produces `docs/features/<slug>/contracts/openapi.yaml` + `docs/features/<slug>/contracts/api-sync-report.md`.

This is the **stage 10 runner**: contract is locked before FE / consumer side starts integration. Mock server (Prism / Postman) is brought up from the contract. The same contract feeds BE codegen (`oapi-codegen`, `openapi-generator`) and FE codegen (`openapi-typescript`, `openapi-fetch`) so both sides share a single source of types.

## Owner

Backend Lead.

## When to use

- "API for <slug>", "api-forge for <slug>", "openapi for <feature>", "GraphQL for <feature>", "events for <feature>", "run stage 10".
- User has PRD (data-model optional) and wants to lock the interface before handlers.
- `/sdlc-api-forge <slug>` as explicit invocation.
- `/sdlc-api-forge <slug> --reconcile` when `data-model.md` arrives after a scenario-B run.
- Skip if openapi.yaml exists, passed lint (spectral / graphql-inspector), AND api-sync-report.md core checks all ✓.

## Inputs

- `<slug>` — same as for PRD / data-model.
- **Hard gate (refuse if missing):** `docs/features/<slug>/PRD.md`. If missing — STOP, suggest `sdlc:write-prd`.
- **Recommended (auto-detected; their presence determines scenario A vs B):**
  - `docs/features/<slug>/data-model.md` — strongest source of typed fields and constraints. Presence triggers scenario A (typed contract). Absence triggers scenario B (PRD/sequence-derived contract with `unresolved_origins` block).
  - `docs/features/<slug>/sad.md` §6 — both container-level sequences AND endpoint-level sequences embedded under `### US-N: <title>` (or `### Endpoint-level: <method path>`) headings. Default output of `complete-sequence-diagrams` (both coverage-audit and single-flow modes are inline). Parse all Mermaid `sequenceDiagram` blocks: container-level identifies async actors (Worker, Scheduler, External) so endpoints get `Idempotency-Key`; endpoint-level `alt`-blocks become OpenAPI `responses` (see step 9).
- **Optional (auto-detected, enrich generation when present):**
  - `docs/features/<slug>/idea-brief.md` — feature motivation. Fills `info.description` with one-paragraph context ("why this API exists") so downstream consumers (other teams, AI) understand purpose, not just shape.
  - `docs/features/<slug>/adr/*.md` — architecture decisions on versioning, error format, authentication. Override skill defaults when present (e.g., ADR mandates header versioning → URL versioning default is overridden).
  - **Existing `contracts/openapi.yaml`** — if present, the skill diffs and updates in place rather than overwriting whole-cloth.

If any recommended/optional input is missing, the skill still generates a usable `openapi.yaml`. The `api-sync-report.md` flags which enrichment was skipped and why it would have helped (e.g., "no endpoint-level sequences found in sad.md §6 → error responses derived from PRD acceptance criteria only; may miss 403 not-owned branches").

## Scenarios A vs B

The skill detects scenario from inputs and tells the user which one it is running.

### Scenario A — data-model.md exists (preferred)

Contract is **derived** from the model. Every field has an `origin` in a typed entity. Constraints (`maxLength`, `pattern`, `enum`) trace back to DDL (`varchar(N)`, `CHECK`, ENUM type). Error codes derive from constraints (`UNIQUE (a, b)` → `<entity>.duplicate_<field>`). `unresolved_origins` is **empty**.

Drift check (step 17) verifies field-by-field alignment. Drift in scenario A means model and contract disagree on form — human resolves which artifact is right.

### Scenario B — data-model.md missing (fallback)

Contract is **inferred** from PRD §4 acceptance criteria + sequence diagrams + SAD §6 namespacing. Types are less precise (`string` without `maxLength`, no enum patterns yet). Error codes derive from `alt`-blocks in sequences, not from constraints.

`unresolved_origins` lists every field whose origin is "inferred from PRD/sequence, needs confirmation when data-model.md arrives". This is **not an error** — it is **declared incompleteness**, visible to the team.

### Reconcile (`--reconcile` flag)

When `data-model.md` arrives after a scenario-B run, re-run the skill with `--reconcile`. It:

1. Re-reads inputs (now includes data-model.md).
2. Switches scenario B → A.
3. Tightens types: `string` becomes `string` + `maxLength` where DDL exists.
4. Promotes low-confidence origins to high.
5. Empties `unresolved_origins`.
6. Surfaces any field that **had** an inferred origin from PRD but **now disagrees** with the model — that is real drift, not stale incompleteness.

`--reconcile` is the **point of convergence** between two artifacts that lived independently.

## Defaults

The skill applies a fixed set of defaults — not invented per-feature, but agreed minimum drawn from public industry guidelines (see Sources of best practices below). Defaults baseline lives in `.claude/rules/openapi.md`; deviations are flagged in `api-sync-report.md` so the team makes deviation a conscious decision.

| Topic | Default | Rationale |
|---|---|---|
| OpenAPI version | `3.1.0` | JSON Schema 2020-12 reused by JSON validators; native webhooks; `nullable` via `type: [string, null]`. |
| Error response shape | `{code, message, details?}` snake_case | Homogeneous FE handling; `code` gives machine rule "retry vs change request". |
| Error `code` namespacing | `<module>.<error_name>` | `lesson.duplicate_slug`, `lesson.module_not_found` — domain-readable. |
| Pagination for list endpoints | Cursor (UUID v7), not offset | Stable pages under concurrent writes; stable context for AI consumer. |
| URL versioning | `/api/v1/...` | Simpler than header versioning; cacheable; version is visible in the path. |
| Authentication | `BearerAuth: type: http, scheme: bearer` global | Global default; public endpoints declare explicit `security: []`. |
| ID generation | UUID v7 in application, not in DB | Cursor pagination; client can predict ID before request (idempotency). |
| Validation in spec | `pattern` / `enum` / `maxLength` mandatory for bounded fields | Double safety: handler validates again, but contract + audit keep consistency with DB. |
| Schema reuse | `$ref` mandatory; inline schemas forbidden | Single source of truth per type — less drift between endpoints. |
| Forbidden | `nullable: true` (3.0 style), real PII in `example`, `additionalProperties: true` on response shapes | Style leak from 3.0; PII in Swagger UI; internal field leakage. |

When an ADR overrides a default (e.g., header versioning), the report records "deviation by ADR-NNNN" so the override is documented, not silent.

## Protocol

1. **Prereq check (hard).** `test -f docs/features/<slug>/PRD.md` → exit ≠ 0 = refuse with pointer to `sdlc:write-prd`. data-model.md absence is **not** a refusal — it switches to scenario B.
2. **Detect scenario.** Scenario A if `docs/features/<slug>/data-model.md` exists, B otherwise. Tell the user which scenario was detected and which inputs were found / missing.
3. **Read prereqs.** PRD (AC → endpoints + validation rules), data-model if A (resource shapes, types, constraints).
4. **Read optional inputs (auto-detect).** For each of `docs/features/<slug>/sad.md`, `docs/features/<slug>/idea-brief.md`, `docs/features/<slug>/adr/*.md`: if present, parse and surface a one-line "found" note. If absent, surface "skipped" with consequence note. Never refuse on absence — these are enrichments, not prerequisites.
5. **Pick style.** HTTP REST (OpenAPI 3.1) — default for resource APIs; GraphQL — for query-flexibility; events — AsyncAPI. Ask user if ambiguous.
6. **Copy templates.** Copy from `./templates/`:
   - `openapi.yaml` → `docs/features/<slug>/contracts/openapi.yaml` (or update in place if exists).
   - `events.md` → `docs/features/<slug>/contracts/events.md` (if async).
7. **Versioning.** URL-based (`/api/v1/...`) — default. Header-based — only if ADR mandates it. `?v=2` — anti-pattern.
8. **Endpoints per AC.** For each user-story AC — endpoint(s). Method + path + request schema + response schema + error responses. In scenario A, schema fields trace to data-model entity columns; in scenario B, schemas are derived from PRD field names + sequence message names.
9. **Generate error branches from `alt`-blocks (when sequences present).** For each endpoint covered by a Mermaid `sequenceDiagram` block inline under sad.md §6 (US-N container-level or `### Endpoint-level: <method path>` heading): parse the `alt … else … end` blocks and add a response entry per branch (e.g., `alt not found` → `404 lesson.not_found`, `alt not owner` → `403 lesson.not_owned`, `alt invalid state` → `409 lesson.invalid_state`). This closes the typical PRD blind spot — PRD lists happy path + 2-3 errors; sequences exhaustively enumerate error branches including 403 not-owned, which PRD often omits.
10. **Error model.** Unified `{code, message, details?}`. Code — `<module>.<error_name>` snake_case. HTTP status mapping (4xx → client, 5xx → server). No `{"error": "something failed"}`.
11. **Idempotency.** Mutating + retriable endpoints (POST, PATCH) — `Idempotency-Key` header. Describe TTL and retention. If a sequence shows `Note over API, Worker: retry up to N` for an endpoint — mark `Idempotency-Key` mandatory.
12. **Pagination.** Cursor-based for lists (`?after=&before=&limit=`) on UUID v7. Response wraps in `{items, has_next, has_prev, next_cursor}`. Offset — anti-pattern.
13. **Async events.** For each event: name (`<module>.<action>.<v>`), schema (JSON Schema or Avro), producer, consumers, retry / DLQ behavior. If sequences contain async `API->>Worker: enqueue` messages — derive the event list from those messages and pre-fill `events.md` payload skeletons.
14. **Examples.** Each operation — request example + 200/201 example + error example. Use placeholder PII (`<...>@example.test`, `+380 00 000 00 00`, `Test User`) — never real values.
15. **Lint.** Suggest running `spectral lint contracts/openapi.yaml` (or graphql-inspector). If not yet wired — add to `make sdlc-check`.
16. **Mock server.** Suggest bringing up Prism: `prism mock contracts/openapi.yaml`. FE / consumer must have an access point to the mock.
17. **Run inline drift check (5-point) + write `api-sync-report.md`.** Compare the generated `openapi.yaml` against all read artifacts. The report has three sections:

    **Section A — field origins table.** One row per `(operation, schema_field)` pair: `schema_path | origin | confidence`. `confidence: high` for scenario-A fields with matching DDL types; `medium` for PRD-derived fields; `low` for fields inferred from sequence message names only.

    **Section B — drift findings.** Five-point checklist (each ✓ or ✗ with one-line diagnostic on ✗):

    1. **Endpoint ↔ data-model** — every endpoint maps to ≥1 query/mutation against an entity in `data-model.md` (e.g., `POST /lessons/{id}/publish` → `UPDATE lessons SET status='published'`). In scenario B: every endpoint maps to a sequence (since model absent).
    2. **Error codes ↔ domain sentinels** — every `code` in OpenAPI `ErrorResponse` has a sentinel constant in `domain/errors.go` (or equivalent for non-Go stacks). In scenario A, sentinels typically derive from UNIQUE/NOT NULL constraints in the model.
    3. **Validation ↔ DB constraints** — `maxLength`, `pattern`, `enum` in OpenAPI align with `VARCHAR(N)` / app validation / DB `UNIQUE` in `data-model.md` (scenario A only; scenario B records "deferred to reconcile").
    4. **Entity ↔ endpoint** — every entity in `data-model.md` is served by ≥1 endpoint, or explicitly noted as "intentionally internal" (e.g., `media_blobs` exposed only via signed URL inside a block payload). Scenario A only.
    5. **OpenAPI ↔ sequence** — endpoint-level sequences inline у sad.md §6 use the same HTTP methods / paths / response codes as `openapi.yaml`. Mismatch usually means the sequence was drawn before OpenAPI was finalized and never updated.

    **Core checks** (1, 2, 3) failing — surface as blocker to the user. **Supporting checks** (4, 5) failing — become follow-up items in the report.

    **Section C — unresolved_origins.** Empty in scenario A. In scenario B — list of fields whose origin is "inferred from PRD/sequence, needs confirmation when data-model.md arrives". Each entry: `schema_path | current origin | what reconcile would tighten`.

18. **Self-check against DoD.** Lint pass, examples on all operations, error model with codes, mock server up, `api-sync-report.md` core checks (1–3) all ✓, scenario explicitly recorded.
19. **Propose commit.** `10: API contract for <slug> via api-forge` + next owner (Decision owner → stage 11 ADRs).

## Modes

| Mode | Trigger | Behaviour |
|---|---|---|
| Initial run | `/sdlc-api-forge <slug>` (no `openapi.yaml` exists yet) | Full generation. Writes both files from scratch. |
| Update | `/sdlc-api-forge <slug> --update` (after sources changed) | Re-reads inputs, regenerates YAML in-place. Preserves `info.version`. Reports diff in summary. |
| Reconcile | `/sdlc-api-forge <slug> --reconcile` (after `data-model.md` arrives in scenario B) | Switches scenario B → A. Tightens types (`string` → `string` with `maxLength`), promotes `low` origins to `high`, empties `unresolved_origins`. |

## Invariants

- **Never invent fields.** If a field has no origin in any input, the skill refuses to add it and asks the user where it should come from.
- **Never silently drop fields.** If a field disappears from `data-model.md`, the skill keeps it in the YAML with a `# stale` comment and surfaces it in the report — human decides whether to remove from contract or restore in model.
- **Never edit sources.** Reads only. Modification of `data-model.md` / `prd.md` / sequences is the user's job.
- **Stack-agnostic schema names.** Schemas use the domain language from `data-model.md`, not Go/TS/Python idioms.
- **Never bump `info.version` silently.** The user bumps semver explicitly with a CHANGELOG entry.

## Conflicts — human in the loop

| Conflict | Skill action |
|---|---|
| Field in `data-model.md` with no story in PRD covering it | Add field to schema with a `# unused-in-prd` note in `api-sync-report.md`; ask user. |
| Sequence references operation that maps to no endpoint in the resulting contract | Add `# orphan-sequence` flag in report; ask user (forgotten endpoint? internal job?). |
| PRD validation rule contradicts DDL constraint (`maxLength 300` in PRD vs `varchar(200)` in DDL) | Take the stricter value; flag both in report. Human resolves which artifact is wrong. |
| Existing `openapi.yaml` has fields not in any source | Keep them with `# manual-addition` comment; flag in report. |

If ≥3 flags appear in one run — pause, surface the list to the user, ask whether to continue or fix sources first.

## Definition of Done

- Contract committed at `docs/features/<slug>/contracts/openapi.yaml`.
- `api-sync-report.md` committed alongside: scenario recorded, core checks (1–3) all ✓ or explicitly waived, `unresolved_origins` empty (A) or listed (B).
- Mock server up (Prism / Postman).
- FE / consumer sides know where to pull from.
- Spectral / graphql-inspector lint pass.

## Anti-patterns

- "Contract after code" — FE / consumer integrates against breaking changes. Contract-first.
- Error as free text: `{"error": "something failed"}`. Must be `{code, message, details?}`.
- Versioning via `?v=2` query param — non-standard, breaks cache.
- Idempotency "if you feel like it" for mutating + retriable. Must be mandatory Idempotency-Key with TTL.
- Async events without schema. Subscriber dies on the first breaking change.
- Operations without examples. Lint passes, but implementer doesn't know what such a request actually means.
- Method names in sequence diagrams and in API are different. Onboarding engineer walks into a trap.
- **Drift check skipped because "the spec was just generated, of course it matches"**. The 5-point check exists precisely because generation can match PRD-as-read while diverging from data-model or sequences (different files, different humans wrote them). Always run drift; surfacing a clean 5/5 ✓ is cheap, surfacing a silent ✗ in prod is not.
- **Error responses derived only from PRD.** PRD typically lists happy path + 2-3 errors. Sequences exhaustively enumerate `alt` branches including 403 not-owned and concurrent-modification states. Skipping the sequence enrichment leaves blind spots.
- **Hiding scenario B as if it were complete.** Scenario B is a valid state, not a half-baked one. `unresolved_origins` must be visible. Pretending the contract is fully typed when it isn't sets the team up for a silent drift when the model arrives.
- **`nullable: true`** (3.0 style) in 3.1 documents. Use `type: [string, null]`.
- **Real PII in `example` blocks.** Use placeholders.

## Sources of best practices

Defaults applied by this skill are drawn from public industry guidelines, recorded here so the team knows where each rule came from and can argue with the source if they want to deviate.

- **Microsoft REST API Guidelines** — https://github.com/microsoft/api-guidelines. Error shape with machine-readable `code`, URL versioning, `BearerAuth` default.
- **Google AIP (API Improvement Proposals)** — https://google.aip.dev/. Resource-oriented paths, snake_case field names, domain-namespaced error codes.
- **Zalando RESTful API Guidelines** — https://opensource.zalando.com/restful-api-guidelines/. Cursor pagination via next-link, JSON-only responses, snake_case JSON.
- **Stripe API Versioning** — https://stripe.com/blog/api-versioning. URL versioning trade-offs, deprecation strategy, backwards-compat over 10+ years.
- **Swagger «What is API-First?»** — https://swagger.io/resources/articles/adopting-an-api-first-approach/. Canonical definition of API-first methodology from the team that built Swagger/OpenAPI.
- **OpenAPI 3.1 specification** — https://spec.openapis.org/oas/v3.1.0. Full JSON Schema 2020-12 compatibility.

## Template

→ [./templates/openapi.yaml](./templates/openapi.yaml)
→ [./templates/events.md](./templates/events.md)

## Example invocation

> **User:** `/sdlc-api-forge course-lesson-mvp`
>
> **Skill behavior:**
> 1. `test -f docs/features/course-lesson-mvp/PRD.md` → OK. `test -f data-model.md` → OK → **scenario A**.
> 2. Read PRD §4 user stories: US-1 createLesson, US-2 listLessons, US-3 getLesson, US-4 addBlock, US-5 publishLesson.
> 3. Read data-model.md: entity `lesson` with `id uuid v7`, `module_id uuid FK`, `title varchar(200) NOT NULL`, `slug varchar(80) NOT NULL`, `duration_minutes int CHECK (5..240)`, `content_type ENUM (video|text|quiz)`, UNIQUE `(module_id, slug)`.
> 4. Auto-detect optional inputs:
>    - `sad.md` §6 → found (3 container-level US-NN sequences with async actor `media-worker` + 2 inline endpoint-level sequences for `POST /lessons` create-flow and `POST /lessons/{id}/publish` publish-flow with alt-blocks: not_found, not_owned, invalid_state, slug_conflict).
>    - `idea-brief.md` → found (one-paragraph "why this API" goes into `info.description`).
>    - `adr/0001-content-storage-strategy.md` → found (referenced in `info.description`).
> 5. Style: REST (OpenAPI 3.1) — default for resource API with browser + AI consumers.
> 6. Copy templates → `docs/features/course-lesson-mvp/contracts/openapi.yaml` + `events.md`.
> 7. Versioning: `/api/v1/...` URL-based.
> 8. Endpoints from US: 5 endpoints (POST /lessons, GET /lessons, GET /lessons/{id}, POST /lessons/{id}/blocks, POST /lessons/{id}/publish).
> 9. **Error branches from sequences:** sad.md §6 endpoint-level for `publishLesson` alt-blocks → 404 lesson.not_found, 403 lesson.not_owned, 409 lesson.invalid_state. Endpoint-level for `createLesson` alt → 409 lesson.duplicate_slug. PRD did not list 403; sequence enrichment caught it.
> 10. Error model: `{code, message, details?}` snake_case. Domain sentinels mapped from `data-model.md` invariants.
> 11. Idempotency: POST /lessons/{id}/publish — `Idempotency-Key` mandatory (sequence shows retry note on this endpoint).
> 12. Pagination: GET /lessons?after=&limit= (cursor UUID v7).
> 13. Events from `API->>media-worker: enqueue` in sequences → `events.md` skeleton with `lesson.created.v1`, `lesson.published.v1`.
> 14. Examples on every operation; spectral lint pass.
> 15. Mock: `prism mock contracts/openapi.yaml -p 4010`.
> 16. **`api-sync-report.md`** — scenario A, field origins table (12 rows: 9 `high`, 3 `medium`), drift findings:
>     1. Endpoint ↔ data-model ✓
>     2. Error codes ↔ domain sentinels ✓ (4 codes, 4 sentinels in `domain/errors.go`)
>     3. Validation ↔ DB constraints ✓ (title maxLength 200 ↔ VARCHAR(200), slug pattern ↔ DB CHECK omitted intentionally, app-validated)
>     4. Entity ↔ endpoint ✓ with note: `media_blobs` exposed only via signed URL in block payload (by design, ADR-0001)
>     5. OpenAPI ↔ sequence ✓ (all sequence HTTP codes match spec)
>     Unresolved origins: empty (scenario A).
> 17. Self-check DoD → all green.
> 18. Commit: `10: API contract for course-lesson-mvp via api-forge`.
