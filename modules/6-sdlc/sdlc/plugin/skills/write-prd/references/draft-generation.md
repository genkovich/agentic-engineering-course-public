# Draft generation — per-section contract for write-prd Protocol step 6

How the skill turns required inputs + selected channel outputs + template instructions into a draft for each PRD section. The authoritative format/structure source is the `<!-- Skill instruction: ... -->` comment in [../templates/PRD-template.md](../templates/PRD-template.md) for that section. This file is the operational glue: where the content comes from and what is forbidden.

## Inputs in priority order

1. **`CONTEXT.md` `## Glossary`** — canonical for role names + domain terms. If anything contradicts it (idea-brief, reference code, MCP source), glossary wins.
2. **`idea-brief.md`** — sections §2 Problem, §3 Users, §6 Out of scope, §11 RICE, §13 Recommendation.
3. **Channel outputs from step 4** — reference-module patterns (entity types, error codes, authz, status transitions), MCP-Atlassian quotes, project docs, RAG hits.

## Per-section sources

- **§1 Context** — 3-4 paragraphs. ¶1 from idea-brief §2 Problem. ¶2 from idea-brief «Why now» / triggers. ¶3 from idea-brief §13 Recommendation (cite directly). ¶4 (optional) reference patterns + MCP/docs/RAG quotes as **traceability context** — and the slot where Phase 7.5 `Override` resolutions emit «Decision overrides» bullets.
- **§2 Goals** — 2-3 strategic outcomes, each a manifestation of idea-brief §13. Cite §13 directly. No numbers (those live in §7 KPIs).
- **§3 Non-goals** — 3-4 entries, each with reason. Source: idea-brief §6 Out of scope.
- **§4 User stories** — ≥5 US (no upper cap) in `As a <role> / I want / So that` form. Skill proposes as many as needed to cover all roles from CONTEXT glossary + all goals from §2. Roles **only** from CONTEXT glossary (no `user`/`admin` invented if the glossary defines specific roles).
- **§5 Acceptance criteria** — see «§5 AC contract» below.
- **§6 NFR table** — recommended-list rows with numeric targets, **no upper cap**. No «fast»/«reliable»/«high». Measurement = concrete production metric name (e.g. endpoint name from reference module). TBD allowed only with owner + due tied to a row in §8.
- **§6.1 Security / privacy** — data classification, personal data touched, authZ/authN impact, **3-5 abuse cases** (cross-org access, draft-leak, SSRF/injection through URL/text fields, spam create with rate limit, optional token misuse), security review verdict.
- **§7 KPIs** — ≥3 metrics (no upper cap), baseline → target with timeframe. Skill proposes as many as RICE drivers from idea-brief §11 + Recommendation §13. baseline=0 OK for new feature; baseline=TBD requires a measurement plan inline.
- **§8 Open questions** — 2-3 entries, each with owner + due (date or stage trigger).

The authoritative format for each section lives in the template inline comments — read `./templates/PRD-template.md` at step 5 and treat each `<!-- Skill instruction: ... -->` as the per-section generation prompt.

## §5 AC contract

AC describes a **business-observable outcome from the actor's perspective**. Format: Given / When / Then.

**No upper cap on the AC count.** Skill proposes as many as needed to cover all US ≥1 AC + all 5 coverage types represented. If a `Drop` (or `Save as Open Question`) during Socratic step 7 leaves a coverage type with zero ACs, skill regenerates a replacement AC of the same coverage type and runs a mini-batch on it.

Five coverage types are mandatory — at least 1 AC of each:

1. **happy** — actor performs main flow → system records the outcome and confirms.
2. **error** — actor submits invalid input → system blocks the action and explains the reason to the actor (no HTTP code, no error-string — phrase as «system shows the actor that <field> must be <constraint>»).
3. **authorization** — actor lacks permission (cross-org / cross-role / not-owner) → system either denies access or hides existence. Rationale in business terms («system hides existence to avoid leaking that the object belongs to another team») — no `404`/`403`.
4. **domain invariant** — actor attempts an action that violates a named invariant (e.g. «no published lessons», «unique sequence per course») → system blocks the action and names the invariant in plain language (no error-code-string, no `409`).
5. **cross-context** — actor's action depends on state in another bounded context (membership, parent-child relation) → system enforces the cross-context rule.

Each AC tagged with its US-NN. Roles from CONTEXT glossary and domain-invariant **names** as natural-language phrases are allowed — they are business terms.

### Forbidden tokens in §5 AC text

Zero tolerance — checked by Phase 7.5 critic F6 and pre-write regex scan (see [critic-phase.md](./critic-phase.md)):

- HTTP verbs / methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.
- URL paths: `/courses`, `/lessons/{id}`, `/api/v1/...` (anything starting with `/` followed by lowercase identifier).
- HTTP status codes as bare numerics in AC body: `200`, `201`, `400`, `401`, `403`, `404`, `409`, `5xx`, `500`, `503`.
- Error-code strings matching `[a-z_]+\.[a-z_]+` (e.g. `course.not_methodist`, `validation.description_too_long`).
- JSON-schema fragments / payload bodies: `{title, description}`, `{id, status: "draft"}`.
- SQL / DB constructs: `UNIQUE(...)`, `UNIQUE INDEX`, `FK`, `pq.*`, raw `INSERT`/`SELECT`/`UPDATE`, constraint names (`uniq_course_seq`).

The technical mapping for these (HTTP method/path/status, error-code strings, payload schemas, DB constraints) lives in **stage 09** (`sdlc:define-api`) and **stage 10** (`sdlc:decide-adr`). PRD AC is WHAT a user can observe, not HOW the system encodes it.

### Race conditions / edges

If an AC needs a concurrent edge variant, add it as `AC-NNb` (subletter) — still in business language.

## Pre-write hygiene

Before handing the draft to step 7 (Socratic), the skill must:

- Confirm CONTEXT.md glossary terms are used verbatim in §4 US roles.
- Confirm §3 Non-goals quote idea-brief §6 reasons (no inventing).
- Confirm §1 ¶3 cites idea-brief §13 Recommendation verbatim or paraphrases without losing the vector.
- Confirm §5 AC contains ≥1 of each coverage type and 0 forbidden tokens (a self-scan; the Phase 7.5 critic + regex scan are the second backstop).
