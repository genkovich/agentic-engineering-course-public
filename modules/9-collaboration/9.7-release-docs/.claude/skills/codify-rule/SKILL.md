---
name: codify-rule
description: >-
  Turn a repeated mistake into a durable, path-scoped rule in .claude/rules/. Triggers on
  "codify this rule", "make a rule so this doesn't happen again", "/codify-rule", "закодифікуй правило",
  "петля помилка-правило". Use only when the same mistake showed up TWICE (twice = a pattern, once =
  noise). Names the wrong shape and the right shape with one short example of each, scopes the rule to
  the paths that matter, and leaves the edit in the working tree so the next agent on this repo
  inherits the fix. Edits only .claude/rules/; never commits or pushes.
allowed-tools: Bash(git log:*), Bash(git diff:*), Read(src/**), Read(.claude/rules/**), Write(.claude/rules/**), Edit(.claude/rules/**)
user-invocable: true
disable-model-invocation: true
argument-hint: ''
model: claude-haiku-4-5
effort: low
---

# Skill: codify-rule

Goal: capture a mistake seen twice as a narrow, concrete rule the next agent inherits — so the fix lands once, in a versioned file, instead of by hand every time.

A rule earns its place only on a **repeated** mistake. This is the closing move of the error→rule loop: a signal caught twice (in review, in CI, in a rejected PR) becomes a durable instruction every agent on the repo loads.

## Inputs

- The case the user describes: the repeated mistake and the convention it broke.
- The code that shows both shapes (the right one and the regressions), in `src/`.
- `.claude/rules/` — existing rules; `templates/rule.md` — the rule shape.

## Protocol

1. **Read the case.** Open the files the user points at in `src/` and quote the exact wrong shape and the right shape side by side. Confirm the mistake appears **at least twice** — if it is a one-off, say so and do not write a rule.
2. **Find the home.** Look in `.claude/rules/` for a file that already owns this area. If one fits, append to it (tighten it). Otherwise create `.claude/rules/<topic>.md` with a `globs:` line scoping it to the paths that matter. Follow `templates/rule.md`.
3. **Write it narrow and concrete:** name the wrong shape, name the right shape, one short example of each. Not a moral ("handle errors well") — a specific instruction the next agent applies without the user.
4. **Leave the edit in the working tree.** Do not commit. Show `git diff .claude/rules/` so the human reads the rule before it lands.

## Definition of Done

- The rule addresses a mistake confirmed **twice**, not a one-off.
- It names the wrong shape and the right shape with one example of each, and is scoped with `globs:`.
- No near-duplicate rule was added — an existing rule covering the area was tightened instead.
- The edit is in the working tree; `git diff .claude/rules/` is shown. Nothing committed.

## Anti-patterns

- **Codifying a one-off.** Once is noise. A rule on every single slip bloats `.claude/rules/` and hurts the agent. Wait for the second occurrence.
- **A vague moral.** "Be careful with errors" teaches nothing. Name the exact wrong and right shapes.
- **Bundling unrelated advice** into one rule, or adding a near-duplicate next to an existing rule.
- **Committing or pushing.** Leave the suggestion in the working tree.
- **Editing outside `.claude/rules/`.**

## References & templates

- `templates/rule.md` — narrow path-rule scaffold.
