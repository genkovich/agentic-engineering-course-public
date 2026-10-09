---
name: review-checker
description: >
  Use when reviewing a pull request to enforce team conventions. Triggers on
  "review this PR", "check the PR", "code review", "PR review checklist".
allowed-tools: Read, Bash, Grep
---

# Review Checker

Apply team conventions to a pull request and surface every violation.

## Rules

1. CHANGELOG entry required for any change touching `src/` or public API
2. No `console.log`, `print()` debug calls, or commented-out code blocks
3. Test coverage required for every new branch in business logic — at least one happy path and one error path
4. No unrelated formatting churn — reject PRs that mix logic with bulk reformatting
5. Security checklist for any change touching auth, PII, or external network calls — list the threat model in the PR description

Output: a numbered list of violations with file paths and line numbers. If clean, say so explicitly.
