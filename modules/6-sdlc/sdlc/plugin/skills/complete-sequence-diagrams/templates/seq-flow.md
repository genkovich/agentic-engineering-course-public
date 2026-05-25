---
status: Draft
owner: "<Tech Lead name>"
reviewers: []
updated_at: "<YYYY-MM-DD>"
feature_size: S
stage: "07"
ticket: "<ticket-id>"
---

# Sequence — <flow name>

<!-- Stage 07 → see SDLC/plugin/skills/draw-sequence/SKILL.md -->
<!-- One file per flow. Cover happy + 1-2 error paths. -->

## Happy path

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant API as API
    participant SVC as Service
    participant DB as Database

    C->>API: <request>
    API->>SVC: <call>
    SVC->>DB: <query>
    DB-->>SVC: <result>
    SVC-->>API: <response>
    API-->>C: 200 OK
```

## Error path: <name>

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant API as API

    C->>API: <request>
    API-->>C: <4xx / 5xx> with <error code>
```
