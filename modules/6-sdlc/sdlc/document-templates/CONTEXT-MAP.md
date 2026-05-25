---
status: Living
updated_at: "<YYYY-MM-DD>"
---

# Context Map

<!--
CONTEXT-MAP.md is needed ONLY when the repo has > 1 bounded context.
Single-context repo (default) — use CONTEXT.md at the root; either skip this file
or leave it as a reminder with an empty table row.

Multi-context split is a separate decision (usually stage 04 — architecture brief
or a dedicated ADR "Split into ordering / billing contexts"). Don't split prematurely.
-->

| Context | Path | Description |
|---------|------|-------------|
| <name>  | <src/...> | <1-line scope> |

<!--
Example multi-context layout (uncomment when actually splitting):

| ordering | src/ordering/ | Order lifecycle, cart, checkout. Owns Order, LineItem. |
| billing  | src/billing/  | Invoices, payments, refunds. Owns Invoice, Payment.    |

Each context has its own CONTEXT.md and docs/adr/ at its own root.
System-wide ADRs (e.g. "shared event-bus") live in the root docs/adr/.
-->
