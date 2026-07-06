# Demo: 9.7 release & docs — local skills → CI release pipeline

**Module:** 9 — Collaboration
**Lecture:** 9.7 Реліз і документація з Claude

A self-contained mini-repo for the 9.7 demos. The lecture is demo-driven: each
point is *say it → call the skill → run it → open GitHub → show it*. One small
feature drives the whole pipeline.

## The release driver: one `feat`

`Note` already carries a `tags` field, but nothing searches by tag. The seeded
history adds one commit — `feat: filter notes by tag` — a `NoteBook.filter_by_tag`
method. That single commit fires the entire pipeline:

```
feat: filter notes by tag
   ├─ next-version.sh  → MINOR bump → v0.2.0
   ├─ curate-changelog → an "Added" line
   ├─ release-notes    → a partner narrative
   └─ docs/api.md never mentioned the method → real docs drift the tool catches
```

## Two halves: a rule decides, the agent explains

The version and the doc gap are **decided deterministically by scripts** (no
LLM). The agent's job is the human-readable layer on top — explain the bump,
curate the prose, propose the doc fix. Keep that line clear.

| Script | What it decides (no LLM) |
|---|---|
| `scripts/next-version.sh` | the next semver from the commit types (`feat`→MINOR…) — prints `0.2.0` |
| `scripts/check-docs-drift.py` | which public `NoteBook` methods are missing from `docs/api.md` — flags `filter_by_tag` |

## Skills (local, in a session)

Each is a user-invokable skill under `.claude/skills/<name>/`. None of them
commits or pushes — they prepare the working tree; a human applies it.

| Skill | What it does |
|---|---|
| `/bump-version` | reads `next-version.sh`, explains **why** MINOR, edits `pyproject.toml`, proposes the tag |
| `/curate-changelog` | curates `[Unreleased]` in `docs/CHANGELOG.md` (filter · group · rewrite, 6 categories) |
| `/release-notes` | same input, partner-facing narrative — prints to chat |
| `/check-docs-drift` | runs `check-docs-drift.py`, proposes the `docs/api.md` fix |
| `/codify-rule` | turns a mistake seen **twice** into a durable `.claude/rules/` rule |
| `/release` | orchestrator: runs the four release stages in order, pausing at each human gate |

## Workflows (the same logic, as CI)

Four workflows, each fired by its own event. The curation logic is identical to
the skills — only **where** it runs changes (your terminal → the server).

| Workflow | Trigger | What it does |
|---|---|---|
| `.github/workflows/version.yml` | `pull_request` | `next-version.sh` + agent → comments the proposed semver |
| `.github/workflows/docs-drift.yml` | `pull_request`, `push: main` | `check-docs-drift.py` + agent → comments if `docs/api.md` lagged |
| `.github/workflows/changelog.yml` | `push: tags ['v*']` | `claude -p` curates `[Unreleased]` → **Release-PR** |
| `.github/workflows/release-notes.yml` | `push: tags ['v*']` | `claude -p` writes notes → **draft GitHub Release** |

Shared plumbing: `.github/prompts/*` (the headless prompts + JSON schemas),
`.github/scripts/extract-structured.py` (recovers the schema'd JSON from the
`claude -p` response), `.github/release.yml` (GitHub's deterministic PR→category
skeleton the agent humanizes).

## Repo layout

```
9.7-release-docs/
├── src/                 notes library (add/get/list/remove/find + the seeded feat)
├── docs/
│   ├── CHANGELOG.md      Keep a Changelog: [Unreleased] + released 0.1.0
│   └── api.md            hand-written NoteBook reference — the docs-drift surface
├── pyproject.toml        single source of truth for the version (0.1.0)
├── scripts/
│   ├── next-version.sh   deterministic semver from commit types
│   └── check-docs-drift.py  deterministic code-vs-doc gap (ast)
├── .claude/
│   ├── skills/           the six skills above
│   └── rules/notes-style.md  a narrow house rule (for the error→rule loop)
├── .github/             workflows + prompts + schemas + scripts
├── seed-history.sh       turn the folder into a repo with a real CC history + v0.1.0
├── record-setup.sh       one-command GitHub bootstrap (private repo, secret, push baseline)
├── reset-demo.sh         revert working-tree edits + drop throwaway branches/tags
├── RECORD.md             the recording runbook (beats in lecture order)
└── RULE-LOOP.md          the planted error→rule case
```

## Run it locally (no GitHub)

```bash
cp -R 9.7-release-docs ~/release-demo && cd ~/release-demo
./seed-history.sh
./scripts/next-version.sh        # 0.2.0
./scripts/check-docs-drift.py    # filter_by_tag undocumented
```

Then in a Claude session run `/release` (or each skill). Read every diff —
**fewer lines than the raw log** is curation, not a dump.

## Record it (one command)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
./record-setup.sh
cd ~/release-demo-9-7 && claude
```

You get a private GitHub repo, seeded, secret set, Actions allowed to open PRs,
`v0.1.0` pushed — and **no release tag**. Walk the beats in `RECORD.md`: open a
PR (version + docs-drift comments), then push `v0.2.0` (changelog Release-PR +
draft Release).

## Honest notes

- **Cost.** On this tiny repo with `claude-haiku-4-5` a run is a few cents
  (~$0.06–0.10 measured). It scales with repo size and turns; pin a cheap model
  and a `--max-turns` cap as here.
- **Determinism.** An LLM curating prose is not bit-for-bit reproducible — two
  runs may word a bullet differently. That is exactly why the output lands as a
  **reviewable PR + draft**, not a direct push to `main` or a published release.
  The version and the doc gap, by contrast, come from scripts — those *are*
  reproducible.
- **No-op on the baseline.** The changelog workflow exits cleanly when there is
  nothing to curate (the `v0.1.0` baseline tag, where `HEAD` is the tag itself)
  — a green no-op, not a failure. The live `v0.2.0` run is the real one.
- **What the platform does vs the agent.** GitHub's `.github/release.yml` groups
  merged PRs deterministically; the agent's job is the human-readable layer on
  top. Keep that line clear.
