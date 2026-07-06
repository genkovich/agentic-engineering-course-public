# RECORD.md — recording runbook for lecture 9.7

Everything in 9.7 is **demo-driven**: each lecture point is *say it → call the
skill → go to the folder → run it → open GitHub → show this*. This is the clean
command cheat-sheet for those beats, in the lecture's order. Nothing here needs
prepping by hand — `record-setup.sh` leaves the repo ready, and the releases are
generated live on camera.

The beats mirror the 🎬 blocks in the lecture, in order:
**version → changelog → release-notes → docs-drift → error→rule loop.**

---

## 0. One-time setup (before recording)

```bash
gh auth status                        # logged in to GitHub
export ANTHROPIC_API_KEY=sk-ant-...   # becomes the repo Actions secret
./record-setup.sh                     # or: ./record-setup.sh my-repo ~/my-dir
cd ~/release-demo-9-7                  # the target dir it created
claude                                 # open the session you'll record in
```

You now have `v0.1.0` tagged on GitHub and eight curatable commits on top —
**no release tag yet**. The `feat: filter notes by tag` among them is the
release driver. `docs/api.md` already drifted (it doesn't list `filter_by_tag`).

> The baseline `v0.1.0` push fires one **harmless no-op** changelog run (nothing
> to release at the baseline). Ignore it; the live `v0.2.0` run is the real one.

---

## 1. Local pipeline — no GitHub (the backbone, Section 3)

The whole release prep runs locally as skills. Two halves are deterministic
(`scripts/`), the rest is the agent curating.

```bash
# --- deterministic, no LLM: the number and the drift come from scripts ---
./scripts/next-version.sh             # prints 0.2.0 (a feat landed -> MINOR)
./scripts/check-docs-drift.py         # flags NoteBook.filter_by_tag undocumented (exit 1)

# --- agent prepares; you review each diff ---
/bump-version                         # explains "MINOR, because feat: filter notes by tag",
                                      #   edits pyproject.toml, proposes `git tag v0.2.0`
git diff pyproject.toml               # version 0.1.0 -> 0.2.0

/curate-changelog                     # curate [Unreleased] from the log since v0.1.0
git diff docs/CHANGELOG.md            # fewer lines than the log = curation, not a dump

/release-notes                        # same input, partner-facing narrative (prose, to chat)
                                      #   put it next to the changelog: one input, two outputs

/check-docs-drift                     # runs the script, proposes the docs/api.md fix
git diff docs/api.md                  # filter_by_tag row added; re-run the script -> exit 0
```

Or run the whole thing at once and review four diffs:

```bash
/release                              # bump-version -> curate-changelog -> release-notes
                                      #   -> check-docs-drift, pausing at each human gate
./reset-demo.sh                       # between takes
```

Beat to say: the version and the drift are **decided by a rule** (scripts); the
agent **explains and prepares**; you **apply**. Nothing here pushes.

---

## 2. Live on GitHub — the same skills become CI steps

### 2a. Open a PR → `version` + `docs-drift` comment

```bash
git checkout -b show-drift
git commit --allow-empty -m "chore: open PR for the demo"
git push -u origin show-drift
gh pr create --fill
```

Then in the browser, on the PR:

- **`version`** comments the proposed bump: `0.1.0 → 0.2.0`, MINOR, naming the
  `feat`.
- **`docs-drift`** comments that `NoteBook.filter_by_tag` is missing from
  `docs/api.md`, with the row to paste. *This is "docs drift, as it runs."*

### 2b. Push the release tag → `changelog` + `release-notes`

```bash
sed -n '1,6p' .github/workflows/changelog.yml   # show the trigger: push tags ['v*']
git tag v0.2.0 && git push origin v0.2.0          # push the release tag — live
```

Then in the browser:

- **Actions tab** → `changelog` and `release-notes` jobs start: install the CLI,
  run `claude -p`, log `cost`/`turns`. **~1–2 min.**
- **Pull requests** → a `changelog/v0.2.0` **Release-PR** with the changelog diff
  in its body.
- **Releases** → a **draft** GitHub Release with the partner notes.

The line to say: a human reviews the PR and publishes the draft — agent
prepares, human ships (**human-in-the-loop**).

---

## 3. Error → durable rule (Section 4)

`see RULE-LOOP.md for the planted case`

```bash
sed -n '33,53p' src/notes.py          # get is the right shape; remove and find regress it (twice)
/codify-rule                          # describe the case; it writes a narrow rule
git diff .claude/rules/               # the new rule lands as a normal diff
```

Optional inheritance beat: open a new `claude` session, ask for another
`NoteBook` lookup method, show it raises `NotesError` unprompted.

---

## 4. Reset between takes

```bash
./reset-demo.sh                       # revert version/changelog/api.md/rules, drop branches + v0.2.0
```

Keeps `v0.1.0`. A Release-PR / draft Release left on GitHub from a live take you
close by hand: `gh pr close changelog/v0.2.0 -d` and `gh release delete v0.2.0 -y`.
