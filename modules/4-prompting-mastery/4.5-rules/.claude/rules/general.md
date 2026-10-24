# General project rules

Цей файл - unconditional. Немає frontmatter з `paths:`, тому Claude завантажує його кожну сесію разом з кореневим `AGENTS.md`. Сюди йдуть тільки три категорії: baseline coding, non-negotiable security, shared project assumptions.

## Baseline coding standards

- Every public function has a one-line doc comment that explains why it exists, not what it does.
- Keep imports grouped: stdlib first, third-party second, internal last. Blank line between groups.
- No commented-out code in commits. Delete or move to a TODO with a tracking link.

## Non-negotiable security

- Never commit secrets, tokens, or credentials. If a value comes from env, document the variable name in `.env.example` with an empty default.
- Never log full request bodies or response payloads. Log structured fields, not blobs.
- Validate every input that crosses a trust boundary: HTTP request, queue message, file upload. Domain code trusts its callers.
- Run dependency audits on every PR. New direct dependencies require a one-line justification in the PR description.

## Shared project assumptions

- This is a fullstack monorepo: Go 1.26 API, React 19 web client, Terraform-managed infra.
- Postgres is the only datastore. We do not add new datastores without an architecture review.
- All persistent IDs are UUID v7 generated in the application layer. Database does not generate IDs.
- Time is stored as `timestamptz` in UTC. Display layer converts to user timezone.
- Errors propagate up. Domain returns sentinel errors, ports map them to HTTP codes. No panics outside main.
