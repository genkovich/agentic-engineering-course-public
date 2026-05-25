---
status: Draft
owner: "<Architect name>"
reviewers: ["<Tech Lead name>", "<Senior reviewer name>"]
updated_at: "<YYYY-MM-DD>"
feature_size: S
stage: "04"
ticket: "<ticket-id>"
---

# Architecture brief — <feature>

<!-- Stage 04 → see SDLC/plugin/skills/draft-architecture/SKILL.md -->
<!-- GATE: Lead + Senior approve -->

**Architect:** <name>
**Date:** <YYYY-MM-DD>

## Goal (1 sentence)
<HOW in one sentence.>

## Components
- **<component 1>** — <responsibility>. New | Existing.
- **<component 2>** — <...>

## Boundaries
- <component 1> owns: <data / API / runtime>.
- Integration with <component 2>: <sync HTTP / async event / shared DB — explain why>.

## Data flow
```mermaid
flowchart LR
    A[Client] -->|HTTP| B[<component 1>]
    B -->|<event>| C[<component 2>]
```

## Tech stack
- Language: <...>
- Framework: <...>
- Storage: <...>
- Infra: <...>

<!-- Why: if a new stack — justify; if existing — confirm it covers NFRs -->

## Security / privacy impact
- Trust boundaries: <external client / internal service / data store>.
- Sensitive data: <none / fields / retention>.
- Threats considered: <auth bypass / injection / replay / data leakage / abuse>.
- Required review: <security-review.md / N/A with reason>.

## Trade-offs

| Decision | Chosen | Rejected | Why |
|---|---|---|---|
| <topic 1> | <option A> | <option B> | <1 sentence> |
| <topic 2> | <...> | <...> | <...> |

## Open questions
- [ ] <q>
