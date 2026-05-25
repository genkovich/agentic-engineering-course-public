# Draft generation — per-section contract for architecture-design Protocol step 6

## TL;DR (короткий вступ українською)

Це крок 6 у Protocol — як skill робить **чорновик у памʼяті** перед тим, як питати користувача (крок 7) і писати на диск (крок 7e).

На кожну з 12 секцій Arc42 skill:

1. Бере джерела у пріоритеті: CONTEXT.md → PRD.md → Explore report → попередні рішення.
2. Тягне з **item-bank** (бібліотеки готових варіантів) — наприклад, для §4 це «sync HTTP / async via outbox / sync через спільну БД».
3. Прогоняє **pre-Socratic hygiene** (попередні перевірки чистоти): чи актори з CONTEXT, чи числа з PRD §6 NFR, чи всі Mermaid-блоки використовують реальні імена.

Глосарій:
- *item-bank* — бібліотека типових варіантів для секції (skill підказує, які опції найчастіше зустрічаються).
- *pre-Socratic hygiene* — фінальні перевірки до того, як питати користувача: щоб не питати про те, що вже зафіксовано у CONTEXT/CLAUDE.md.

---

How the skill turns required inputs (PRD + CONTEXT + Explore report) + earlier-section decisions + template instructions into an in-memory draft for each of the 12 Arc42 sections. The authoritative format/structure source is the inline comment in [../templates/sad-template.md](../templates/sad-template.md) for that section. This file is the operational glue: where the content comes from per section + the item-banks the skill draws from + pre-Socratic hygiene checks.

The draft is held in memory only — the on-disk `sad.md` is **not** touched between Step 4 (bootstrap copy) and Step 7e (per-section file write). The skill ends Step 6 with all 12 sections proposed in-memory + each section's decision list ready for the Step 7 batch loop.

## Inputs in priority order

1. **`CONTEXT.md` `## Glossary`** — canonical for role names + domain terms. If anything contradicts it (PRD, Explore output, reference code), glossary wins.
2. **`docs/features/<slug>/PRD.md`** — Goals (§2), Non-goals (§3), NFR (§6 incl. numeric targets + measurement sources), Constraints, KPIs (§7), Open questions (§8), §1 Context overrides (¶4 bullets emitted by `sdlc:write-prd` Phase-7.5 critic).
3. **Step 3 Explore report** — primary language + framework + versions; top-level module layout; ports/adapters/layering conventions; data stores; inter-module communication style; CLAUDE.md-pinned constraints relevant to `<slug>`. Greenfield → null (skill notes `<!-- brownfield: N/A — greenfield repo -->` in §3 and skips repo-pattern citations).
4. **Earlier-section in-memory decisions** — §4 strategic choices constrain §5/§6/§7/§8; §5 module boundaries constrain §6 flows; §10 quality scenarios reference §1 quality goals. The skill must read its own in-memory draft when drafting later sections (no re-reading the file).

## Per-section sources + item-banks

The item-banks below are guidance — the skill picks how many items to draft based on size class (`.size`) and PRD signal. No upper cap on items per section; lower bounds noted where they exist.

- **§1 Introduction and goals.**
  - Intent (1 paragraph): from PRD §2 Goals + §1 Context.
  - **Top-3 quality goals (1-liners; ≥3, typically 3, occasionally 4)** — from PRD §6 NFR ranked by NFR criticality + PRD §13 Recommendation. Each goal is 1 line; full scenarios live in §10.
  - Stakeholders table: from PRD §4 User-story roles + CONTEXT glossary (Tech Lead row added, Sign-off owner = Yes).

- **§2 Constraints.**
  - **Technical**: Explore-reported language + framework + datastore versions + architecture convention. If PRD §6 NFR includes a pin override → that wins.
  - **Organisational**: PRD §2 deadline + effort budget if quoted; otherwise leave `<TBD by PM>` and add an entry to §11 Risks.
  - **Conventions**: link to CLAUDE.md + reference any module-level patterns from Explore output.
  - **Regulatory**: PRD §6.1 Security/privacy verdict + abuse-cases — copy applicable controls.

- **§3 Context and scope.**
  - 2-3 sentences business context: from PRD §1 ¶1 + §1 ¶3 Recommendation vector.
  - External systems table: from PRD §6.1 Security cross-context entries + Explore «inter-module communication» + «data stores» rows.
  - **C4 Context (L1) Mermaid block**: actors from CONTEXT glossary roles + PRD §4 US, external systems from Explore. 5-10 elements max. Syntax → see [c4-mermaid-syntax.md](./c4-mermaid-syntax.md).

- **§4 Solution strategy.**
  - **Top-3 strategic choices (≥3, typically 3, sometimes 4)** — the seeds for ADRs. Each: 2-3 sentences rationale referencing relevant Quality Goals + Constraints.
  - **Decision-bank (typical strategic decisions per choice)**:
    - Module-to-module integration: async via outbox events / sync HTTP / sync via shared DB.
    - Persistence strategy: single store / per-module store / CQRS.
    - Dashboard / read-side tech: server-rendered / SPA / API-only.
    - Concurrency model: optimistic locking / pessimistic locking / event sourcing.
    - Caching tier: none / in-process / shared (Redis).
  - **ADR-gate kicks in almost always** for §4 decisions because they're strategic-level. Plan ≥2 ADRs from §4 alone.

- **§5 Building block view.**
  - 1 paragraph: layered / hexagonal / clean / event-driven + why.
  - **Decision-bank**:
    - Extend existing module vs new module (boundary heuristic from Explore).
    - Layered vs hexagonal vs clean (default = follow project convention from CLAUDE.md; only ask if PRD signals divergence).
    - Internal sub-package layout (`domain/`, `app/`, `infra/`, `ports/` or project equivalent).
  - **C4 Container (L2) Mermaid block**: monolith → each module = `Container`; standalone process → each `Service` = `Container`. ContainerDb for datastores. Syntax → see [c4-mermaid-syntax.md](./c4-mermaid-syntax.md).

- **§6 Runtime view.**
  - **1 flow for XS/S, 3-5 for M+** — happy-path always present; failure-mode flow if §4 picked async or has external dependency; async event-propagation flow if §4 picked events.
  - Mermaid `sequenceDiagram` block per flow with actors + ≥2 participants + ≥3 message arrows. Reference §5 containers by name (no inventing new ones).
  - **Decision-bank**: which failure modes are critical enough to diagram (downstream-down, timeout, partial-failure, idempotency reset).

- **§7 Deployment view.**
  - Topology in 2-3 sentences: where it runs + replicas + scaling thresholds.
  - Monitoring rows: metrics + alerts + tracing — sourced from CLAUDE.md observability section + PRD NFR latency targets.
  - **For XS/S that doesn't change deployment** → `<!-- N/A: feature reuses existing deployment unit -->` is allowed (still draft a 1-sentence justification).

- **§8 Crosscutting concepts.**
  - Table rows: logging / auth / errors / ID strategy / i18n / observability / outbox-events / rate-limiting (if applicable).
  - **Default = «inherit from CLAUDE.md»** — bundled as one `AskUserQuestion` per [socratic-cadence.md](./socratic-cadence.md) Rule 1: "I'm assuming defaults from CLAUDE.md (slog/JWT/apperr/UUID-v7). Override?" with 2 options (`Keep defaults` / `Custom for §X`).
  - Per-feature override only if PRD §6 NFR or §6.1 Security signals it.

- **§9 Architecture decisions.**
  - Table auto-populated as ADRs spawn in §4-§8. No drafting in Step 6 — section starts empty, filled during Step 7 ADR-gates.

- **§10 Quality requirements.**
  - **≥3 scenarios (one per Quality Goal from §1)** — full When/Then/How-verify form.
  - Numbers from PRD §6 NFR **verbatim** — no inventing, no rounding. If PRD says «p95 ≤ 250ms», SAD says «p95 ≤ 250ms». Forbidden: «fast», «scalable», «high availability» without a number.
  - **How-verify**: concrete test name / chaos drill / load-test command / Prometheus metric — not «integration test».

- **§11 Risks and technical debt.**
  - Auto-generated at end of Step 7 from edits-log + PRD §8 Open Questions + Explore-reported brownfield gotchas.
  - **Decision-bank**: outbox lag during outage; schema-versioning debt; brownfield drift; security debt accepted in v1; accepted-debt rows.
  - **Open-architectural-decision rows** (from Step 7 `Save as Open Question` resolutions): see [socratic-loop.md](./socratic-loop.md) §«Save-as-OQ landing zone».
  - **Severity column** accepts literal `Open question` value for OQ rows (in addition to Low/Medium/High for regular risks).

- **§12 Glossary.**
  - Auto-extract from CONTEXT.md glossary terms that appear in sad.md body + add domain terms surfaced during Step 7 Socratic that aren't in CONTEXT (flag those for `sdlc:fix-term` follow-up after pass).

## Pre-Socratic hygiene

Before handing the in-memory draft to Step 7 batch loop, the skill must self-check:

- §1 Stakeholders + §3 actors use CONTEXT glossary roles verbatim (no inventing `user`/`admin` if glossary defines specific roles).
- §2 Constraints reflect Explore output (no contradicting CLAUDE.md without an explicit Override note pointing at §11).
- §3 + §5 Mermaid blocks declare all elements before `Rel` lines (no dangling references; no `Container_Bondary` typos).
- §10 numeric targets cite PRD §6 NFR row exactly (no inventing numbers; no rounding `≤ 250ms` to `≤ 300ms`).
- §6 sequence diagrams reference participants from §5 Container view by name.
- §11 includes at least one row sourced from Explore-reported brownfield gotchas (or empty rows with `<!-- N/A: greenfield -->` comment if applicable).

A hygiene failure regenerates the offending section in-memory before Step 7. The Phase-8 critic (see [critic-phase.md](./critic-phase.md)) is the second backstop — pre-Socratic hygiene is the first.
