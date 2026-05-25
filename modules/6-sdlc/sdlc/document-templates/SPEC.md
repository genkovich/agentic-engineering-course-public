---
status: Draft
owner: "<PM name>"
reviewers: ["<Tech Lead name>"]
updated_at: "<YYYY-MM-DD>"
feature_size: S
stage: "03"
ticket: "<ticket-id>"
aliases: [PRD]
---

# SPEC — <feature-name>

<!-- Stage 03 → see SDLC/plugin/skills/write-spec/SKILL.md -->
<!-- GATE: PM + Tech Lead sign-off required -->

> **Note:** In PM notation this artifact is often called a **PRD**. It's the same document — the engineering form of Product Requirements. See section mapping in `plugin/skills/write-spec/SKILL.md`.

**Status:** Draft | Review | Approved
**PM:** <name>
**Tech Lead:** <name>
**Last updated:** <YYYY-MM-DD>

## 1. Context
<Why we're doing this. Link to idea-brief and brainstorm.>

## 2. Goals
- <goal 1>
- <goal 2>

## 3. Non-goals
- <non-goal 1>
- <non-goal 2>

## 4. User stories

### US-01: <title>
**As a** <role>
**I want** <action>
**So that** <value>

## 5. Acceptance criteria

### AC-01 (US-01)
**Given** <preconditions>
**When** <action>
**Then** <outcome>

## 6. Non-functional requirements

| Aspect | Target | Measurement |
|--------|--------|-------------|
| Latency p95 | ≤ <Nms> | <where measured> |
| Throughput | ≥ <N req/s> | <...> |
| Availability | <99.9%> | <SLO window> |
| Security | <...> | <...> |

## 6.1 Security / privacy
- Data classification: <public / internal / confidential / regulated>.
- Personal data touched: <none / list fields>.
- AuthZ/AuthN impact: <...>.
- Abuse cases: <...>.
- Security review: <required / N/A with reason>. Required for M+, public, API, or data-heavy changes.

## 7. Metrics / KPIs
- <metric 1> — baseline: <...>, target: <...>
- <metric 2> — <...>

## 8. Open questions
- [ ] <q> — owner: <name>, due: <date>
