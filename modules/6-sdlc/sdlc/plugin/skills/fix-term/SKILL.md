---
name: fix-term
description: >
  Use when a domain term shows up in conversation (interview, PRD, ADR)
  and you want to fix its meaning in CONTEXT.md glossary before it drifts.
  Triggers on "fix term X", "what is X in our domain?", "add to CONTEXT",
  "fix term {X}", "/sdlc-fix-term {term}". Lazy-bootstraps CONTEXT.md
  (single-context or multi-context via CONTEXT-MAP.md), asks for canonical
  definition + NOT-cross-reference, checks conflict with existing entries,
  appends a line to ## Glossary. Output: edited CONTEXT.md (created lazily
  if missing). Skip for generic tech terms (HTTP, database) — that's not a
  domain glossary. Primary invocation context: `sdlc:interview` triggers
  this skill automatically at phase 3 (Glossary checkpoint) when its
  glossary-matching spots a new domain term in a user answer; standalone
  invocation is for manual edits or for retro-fitting an existing glossary.
---

# Skill: fix-term (CONTEXT.md domain glossary atomic)

Atomic skill for inline domain term resolution. Lazy-bootstraps `CONTEXT.md` when a domain term first shows up + NOT-cross-reference (to avoid future drift / homonym confusion).

CONTEXT bootstrap logic lives here as a standalone skill. Reused: `sdlc:interview` (phase 3 Glossary checkpoint) delegates here inline when a new domain term shows up in user answers; user can invoke directly («fix tenant»).

## Owner

Whoever drives the conversation — anyone who sees ambiguity. Tech Lead approves the canonical form.

## When to use

- «fix term `<term>`», «what is `<term>` in our domain?», «add `<term>` to CONTEXT».
- During interview/brainstorm the user uses a domain term (tenant, quota, account, consumer, organization) and ambiguity arises.
- `/sdlc-fix-term <term>` as explicit invocation.
- Skip for generic tech terms (HTTP, JSON, database, queue, REST) — that's not a domain glossary, that's tech. Put them in `sad.md` or ADR.
- Skip if the term is already in `CONTEXT.md` and the definition is unchanged — don't duplicate.

## Inputs

- `<term>` — word / phrase from the domain. If not given — ask.
- (Optional) `<context>` — for multi-context repo (vendor / customer / internal). Detected via `CONTEXT-MAP.md` at repo root.
- (Optional) `<feature-slug>` — for scope-aware terms; standalone use — root-level CONTEXT.md.

## Protocol

1. **Detect context.** `test -f CONTEXT-MAP.md` at the repo root.
   - Exists → multi-context repo. Ask: «which context for `<term>`? Available: <list from CONTEXT-MAP.md>». Write to `<ctx>/CONTEXT.md`.
   - Not exists → single-context. Target: `./CONTEXT.md` (root) or `docs/features/<slug>/CONTEXT.md` if `<feature-slug>` is given and the team prefers a per-feature glossary.
2. **Generic-term filter.** Check that `<term>` is not generic tech: `HTTP`, `database`, `queue`, `cache`, `JSON`, `REST`, `gRPC`, `Redis`, `Postgres`, etc. If yes — refuse: «`<term>` is tech, not domain. Fix it in sad.md / ADR instead of CONTEXT.md».
3. **Bootstrap CONTEXT.md (lazy).** `test -f <target>/CONTEXT.md`. Not exists → copy `./templates/CONTEXT.md` → `<target>/CONTEXT.md`. Exists → read existing.
4. **Conflict check.** `grep -i "^- <term>" <target>/CONTEXT.md` — is the term already there?
   - Exists, identical definition → STOP, report «already in glossary».
   - Exists, different definition → ESCALATE: «term is already defined as `<existing>`. Is this the same concept or different?» If different — propose disambiguation (`tenant-billing` vs `tenant-runtime`).
   - Not exists → continue.
5. **Ask canonical definition.** AskUserQuestion: «How to define `<term>` in this context, in 1 sentence?» (free text or 2-3 proposed phrasings, if there are any from brainstorm).
6. **Ask NOT-cross-reference.** AskUserQuestion: «Which concept is `<term>` often confused with? (NOT — so that 6 months from now a reader doesn't mix them up)». If there's no plausible confusion — `None`.
7. **Compose entry.** Format:
   ```
   - <term> — <canonical definition in 1 sentence>. NOT <conflicting concept with explanation of the difference>.
   ```
   Or without NOT, if step 6 = None: `- <term> — <definition>.`
8. **Append to ## Glossary.** Read existing CONTEXT.md, append the line in section `## Glossary` (alphabetical order if the glossary is already sorted, otherwise — at the end).
9. **MP rules check.**
   - If `## Invariants` / `## Out of scope` sections are empty after bootstrap — delete them (only `## Glossary` must remain).
   - Don't add implementation details (Redis stores X with TTL Y) — that's PRD/sad.md.
10. **Update front-matter.** `updated_at: <today>` in CONTEXT.md frontmatter.
11. **Propose commit.** `context: + <term>` or `context: + <term>, <term2>` (if batch). Standalone or as part of an intake commit.

## Questions for discussion

- Is this really a domain term, not tech?
- 1-sentence canonical definition.
- Is there a homonym / NOT-cross-reference (what it's confused with)?
- Single-context or multi-context — where to write?

## Definition of Done

- `<target>/CONTEXT.md` exists and contains `<term>` in `## Glossary`.
- Definition in the format «1-sentence canonical + (opt.) NOT cross-reference».
- Conflict with existing entries resolved (either reported or disambiguated).
- Empty H2 sections deleted (only `## Glossary` is mandatory).
- `updated_at` updated.

## Anti-patterns

- **CONTEXT.md as PRD.** «Redis stores rate-limit counters with TTL 1 min» — that's implementation, put it in `sad.md` / ADR consequences.
- **Empty H2 «for completeness».** `## Invariants` without bullets — anti-pattern. Delete.
- **Silent CONTEXT update.** Adding a term without confirmation — the user doesn't control the glossary.
- **Batched term resolution.** «I'll remember, add at the end» — you won't remember. Inline.
- **Generic term in glossary.** `HTTP`, `JSON`, `Redis` — that's tech, not domain.
- **Overwrite on re-run.** The skill reads existing and appends, doesn't rewrite.
- **Term without NOT cross-reference in an ambiguous domain.** «tenant — customer org» without «NOT user (user — a person inside the tenant)» — confusion in 6 months.

## Template

→ [./templates/CONTEXT.md](./templates/CONTEXT.md)

## Example invocation

> **User:** «fix term tenant for rate-limiting-per-user»
>
> **Skill behavior:**
> 1. `test -f CONTEXT-MAP.md` → not exists. Single-context. Target: `./CONTEXT.md` (root).
> 2. Generic-term filter: `tenant` — not generic tech → continue.
> 3. `test -f CONTEXT.md` → not exists. Copy template.
> 4. `grep -i "^- tenant" CONTEXT.md` → not found.
> 5. AskUserQuestion canonical: User: «tenant — billable customer org with 1+ users».
> 6. AskUserQuestion NOT: User: «with user (that's a different entity — a person inside the tenant)».
> 7. Compose: `- tenant — billable customer org with 1+ users. NOT user (user — a person inside the tenant).`
> 8. Append to `## Glossary`.
> 9. MP check: `## Invariants` and `## Out of scope` empty → delete.
> 10. `updated_at: 2026-05-18` in frontmatter.
> 11. Commit: `context: + tenant`.
