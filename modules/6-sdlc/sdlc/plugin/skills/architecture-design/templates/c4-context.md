---
status: Draft
owner: "<Architect name>"
reviewers: []
updated_at: "<YYYY-MM-DD>"
feature_size: M
stage: "06"
ticket: "<ticket-id>"
---

# C4 — Context

<!-- Stage 06 → see SDLC/plugin/skills/draw-c4/SKILL.md -->

```mermaid
C4Context
    title System Context — <feature>

    Person(user, "<User role>", "<what they do>")
    System(system, "<Our system>", "<purpose>")
    System_Ext(extA, "<External system A>", "<integration>")
    System_Ext(extB, "<External system B>", "<integration>")

    Rel(user, system, "Uses", "HTTPS")
    Rel(system, extA, "Reads from", "REST")
    Rel(system, extB, "Publishes events", "Kafka")
```
