# Process map

Full SDLC diagram with gates and owners.

```mermaid
flowchart TD
    A[Consolidated ideation<br/>14-phase interview<br/>PM/Eng/CTO] --> C[SPEC<br/>PM+Lead]
    C --> D[Architecture brief<br/>Architect]
    D --> E[arc42<br/>Architect]
    E --> F[C4 diagrams<br/>Architect]
    F --> G[Sequence + deployment<br/>Tech Lead]
    G --> H[Data model<br/>Backend Lead]
    H --> I[Migration + rollback<br/>Backend Lead]
    I --> J[API contracts<br/>Backend Lead]
    J --> K[ADR<br/>Decision owner]
    K --> M[Task breakdown<br/>Tech Lead]
    M --> N[Claude execution context<br/>Tech Lead / AI champion]
    N --> O[Test plan<br/>QA/Backend]
    O --> P[Review checklist<br/>Tech Lead]
    P --> Q[Code + Review<br/>Eng + Reviewer]
    Q --> R[Changelog<br/>Release manager]
    R --> S[Obsidian KB sync<br/>Tech Lead]

    classDef gate fill:#fde68a,stroke:#b45309,color:#000;
    class C,D,K,P gate;
```

## Gates

| # | Gate | What it blocks |
|---|------|----------------|
| 03 | SPEC | Without SPEC there is no WHAT/WHY contract — architecture will guess |
| 04 | Architecture brief | Without the brief, full arc42 is written blindly |
| 11 | ADR | Without recorded decisions, downstream tasks have holes |
| 16 | Review checklist | Without a checklist, review is uneven |

## Who writes what

- **PM**: idea-brief (drives ideation), SPEC (co-author), KPIs.
- **Tech Lead**: SPEC (co-author), seq, ADR review (Stage 11) + DoR sign-off (new Stage 13 responsibility), task-breakdown, claude-context, review-checklist, KB note. Joins ideation at multi-perspective review.
- **Architect**: architecture-brief, arc42, C4, sequence.
- **Backend Lead**: data-model, migration, API contracts, ADR (often).
- **QA**: test plan.
- **Release manager**: CHANGELOG, release notes.
