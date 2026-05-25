# File structure

Two angles: where artefacts land per feature (`delivery/<slug>/`), and where the templates that produce them live inside the toolkit (`sdlc/`).

## Per-feature artefact layout

```
delivery/
  <feature-slug>/
    idea-brief.md
    PRD.md
    sad.md                 # SAD (Arc42 12 sections) — C4 L1 inline §3, L2 inline §5
    diagrams/
      seq-<flow>.md
      deployment.md
      c4-component.md      # L3, optional, out of scope for SAD
    data-model.md
    rollback-plan.md       # pulled by hand from sdlc/document-templates/
    contracts/
      openapi.yaml
      events.md
    adr/
      0001-<decision>.md
      0002-<decision>.md
    tasks/
      _epic.md
      tracker.md
      <task-slug>.md
    CONTEXT.md
    claude-context.md      # pulled by hand from sdlc/document-templates/
    test-plan.md
    review-checklist.md    # pulled by hand from sdlc/document-templates/
docs/
  CHANGELOG.md
.claude/
  skills/
    <feature>-execution.md
KB/                        # mirrored to Obsidian vault
  <domain>/<feature>.md
```

## Where the templates that produce these artefacts live

```
sdlc/
  plugin/
    skills/
      <skill-name>/
        SKILL.md           # protocol + DoD + anti-patterns
        templates/         # the starter shape THIS skill copies into delivery/<slug>/
        references/        # mini-guides the skill reads at specific steps
  document-templates/      # cross-feature / manual / legacy — pulled by hand
    CHANGELOG.md
    CONTEXT-MAP.md
    claude-context.md
    rollback-plan.md
    review-checklist.md
    migration-plan.md
    task-breakdown.md      # legacy alias
    SPEC.md / arc42.md / architecture-brief.md   # legacy
    adr/NNNN-title.md      # legacy fallback
    diagrams/c4-component.md
```

## Why like this

- **Everything lives in repo** (next to code) — not in Confluence/Notion. Access through git, versioning, code review.
- **`delivery/<slug>/`** — all per-feature in one place, not scattered across `docs/`, `wiki/`, `architecture/`.
- **`adr/` per feature** — decisions with feature context. Cross-cutting ADRs — under root `docs/adr/`.
- **Templates colocated with their owner skill** — each `plugin/skills/<name>/templates/` is the single source for the artefact that skill produces. `document-templates/` only keeps cross-feature/manual/legacy snippets.
- **`.claude/skills/`** — Claude Code reads this automatically; keep execution context here.
- **`KB/`** — synced with Obsidian vault after merge (stage 18). This is durable knowledge, not in-progress artefacts.

## Slugs

- `kebab-case`, short, no date: `rate-limiting`, `user-import`, `audit-log-v2`.
- NOT `JIRA-1234-rate-limiting` — JIRA ID lives in frontmatter / commits.

## Cleanup

After merge + KB sync:
- Keep `delivery/<slug>/` in repo as an archive (read-only).
- Do NOT delete — needed for git blame and majority-decision archaeology.
- After 1 year you can move it to `delivery/_archive/<year>/<slug>/`.
