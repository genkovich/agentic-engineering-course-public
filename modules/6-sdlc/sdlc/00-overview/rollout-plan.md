# Rollout plan — 6 adoption phases without bureaucracy

The goal is to keep the team from abandoning SDLC after a week. So we roll it out gradually: first 3 templates, then pilot, then the MVP set.

| Phase | Duration | What we add | What we do NOT add |
|---|---|---|---|
| **0. Baseline** | 1 week | Repo skeleton + 3 templates: SPEC, ADR, claude-context | Everything else |
| **1. Pilot** | 2 sprints | One pilot feature with the full pack | The rest of the team works as before |
| **2. MVP set** | 1 month | MVP set (5 artefacts) mandatory for all M+ tasks | arc42, deployment, full C4 |
| **3. Quality gates** | 2 months | DoR/DoD in PR template + review-checklist attached | Hard SLAs on gates |
| **4. Full set** | 3 months | arc42 + deployment + KB sync automated | — |
| **5. Automation** | later | Repo-local checks: `make sdlc-check`, `make sdlc-metrics`, lint ADR/OpenAPI/links/artefacts in CI | Installable CLI |

## Adoption anti-patterns

- **Everything at once.** "From Monday we write arc42 for everything" = sabotage after a week.
- **No pilot.** The first feature must go through the full cycle, otherwise templates are detached from reality.
- **Tooling before process.** First people get used to filling things in by hand. Then we add lightweight repo-local checks; an installable `dlc` CLI stays as a roadmap packaging on top of the scripts.
- **Perfectionism.** A template is not dogma. If a section is not relevant — leave `<!-- N/A: why -->`, don't invent text.

## Success metrics

- **After 2 months**: ≥80% of M+ tasks have SPEC + `tasks/_epic.md` + claude-context before code starts.
- **After 4 months**: average review time decreased (review-checklist is doing its job).
- **After 6 months**: a new engineer onboards through KB + ADR + C4, without 1-1s with the entire team.

## Automation surface in this repo

- `python3 scripts/sdlc_lint.py --root .` — lint SDLC artefacts.
- `python3 scripts/sdlc_lint.py --root . --metrics` — static metrics report.
- `make sdlc-check` / `make sdlc-metrics` — stable entrypoints for CI and local development.
- `.github/workflows/sdlc-quality.yml` runs checks on PR/push.

## Monthly retro

- Which artefacts did people actually read? (Check Git blame / open count.)
- Which ones were skipped? Why? Should we drop them?
- What new things are people asking for (new section? new template?) — add to SDLC after 2-3 repeat requests, not the first one.
