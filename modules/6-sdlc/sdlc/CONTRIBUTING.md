# Contributing to sdlc/

This plugin uses the standard Claude Code skills layout for OSS. If you forked it and want to add your own stage or wrapper — below is a quick-start guide.

## Layout

```
sdlc/
├── plugin/
│   ├── plugin.json                 # OSS metadata
│   ├── README.md                   # plugin-level docs
│   └── skills/
│       ├── <name>/
│       │   └── SKILL.md            # frontmatter + protocol + DoD + anti-patterns
│       └── ...
├── document-templates/             # skeleton artefacts that skills copy into delivery/
├── 00-overview/                    # process-map, definition-of-ready, mvp-vs-full
├── examples/                       # end-to-end examples (rate-limiting, goals-tracking)
├── tests/                          # fixtures + manual rubric
├── LICENSE                         # MIT
├── CHANGELOG.md
└── CLAUDE.md                       # project-level instructions for Claude
```

## Adding a new atomic skill

1. **Start with the mapping to an existing stage or a new one.** If it's an SDLC stage — pick a number; if it's cross-cutting (like `propose-adr`) — no number.

2. **Create `plugin/skills/<name>/SKILL.md`** with frontmatter:
   ```markdown
   ---
   name: <name>
   description: >
     Use when <conditions>. Triggers on "<phrase 1>", "<phrase 2>",
     "/sdlc-<name> <slug>". Output: <artefact path>. Prerequisite: <prereq>.
   ---
   ```

3. **Required sections (in order):**
   - `# Skill: <name> (SDLC stage NN)` or `# Skill: <name> (cross-cutting)`
   - intro (1-3 sentences)
   - `## Owner`
   - `## When to use`
   - `## Inputs`
   - `## Protocol` — 1-15 numbered steps
   - `## Questions for discussion`
   - `## Definition of Done`
   - `## Anti-patterns` — 4-8 bullets, each with a reason
   - `## Template` — link to `document-templates/<file>`
   - `## Example invocation` — full run-through on a real example

4. **Description must list trigger phrases.** Claude Code resolves trigger phrases from `description` (including `/sdlc-<name>`). Without them the skill doesn't activate automatically.

5. **If it's a GATE skill** — in Protocol step 1 add a hard prereq check:
   ```
   1. **Prereq check (hard).** `test -f delivery/<slug>/<file>` — exit ≠ 0 → refuse.
   ```

6. **If it produces an artefact in `delivery/<slug>/`** — copy the template, don't write from scratch:
   ```
   Copy `sdlc/document-templates/<file>` → `delivery/<slug>/<file>`.
   ```

7. **Update `plugin/README.md`** skill table.

8. **Update `CHANGELOG.md`** — entry under [Unreleased] / Added.

## Adding a new composite wrapper

1. **Frontmatter** with triggers (including `/sdlc-<name>`).
2. **Required sections:**
   - `# Skill: <name> (SDLC stages NN-MM composite)`
   - intro
   - `## Owner`, `## When to use`, `## Inputs`
   - `## Protocol` with §A / §B / §C... — each phase **delegates** to an atomic skill, doesn't duplicate logic.
   - `## Questions for discussion`, `## Definition of Done`, `## Idempotency`, `## Anti-patterns`, `## Template`, `## Example invocation`.
3. **Delegation rule.** A wrapper does NOT contain atomic protocol — only invocation. If you feel the urge to copy a protocol — that's an anti-pattern.
4. **Size-awareness.** If the wrapper covers optional artefacts — add a §0 size-check against `delivery/<slug>/.size`.
5. **Single commit propose** at the end of §F.

## Adding a new template

1. Create `document-templates/<file>.md` with:
   - frontmatter (filled in by the skill)
   - HTML-comment header: `<!-- Stage NN → see SDLC/plugin/skills/<skill>/SKILL.md -->`
   - placeholders `<...>` and guideline comments `<!-- Why: ... -->`
2. Update the skill's `## Template` link.

## Style rules

- **Mermaid only** for diagrams.
- **English language** in the body. Frontmatter `description` is English for cross-team discoverability.
- **Anti-patterns with a reason**, not just a list. "Don't X, because Y → consequence Z".
- **Examples on a real feature**, not abstract (`rate-limiting-per-user`, not `example-feature`).

## Testing

Manual test fixtures in [`plugin/tests/`](plugin/tests/). Note: `fixtures/intake/` is a legacy snapshot from v3.x (the prior `intake` wrapper has been consolidated into the `interview` skill); kept for diff archeology. Run:

```bash
# Pick a fixture
cat plugin/tests/fixtures/propose-adr/01-pass-mp/input.md

# Replay in a Claude session
claude /sdlc-propose-adr test-feature < input.md

# Compare output
diff -r delivery/test-feature/ plugin/tests/fixtures/propose-adr/01-pass-mp/expected/
```

Eval rubric: [`plugin/tests/rubric.md`](plugin/tests/rubric.md).

## PR checklist

- [ ] New / changed skill has all required sections in order.
- [ ] Frontmatter description lists trigger phrases (including `/sdlc-...`).
- [ ] If it's a GATE — Protocol step 1 does a hard prereq check.
- [ ] `README.md` skill table updated.
- [ ] `CHANGELOG.md` has an entry under [Unreleased].
- [ ] If it's a breaking change — bump major + add a migration note in CHANGELOG.

## Questions?

Open an issue or send a PR as a draft — the review will suggest improvements.
