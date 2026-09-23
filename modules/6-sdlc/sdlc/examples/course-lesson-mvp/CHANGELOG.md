# Changelog — course-lesson-mvp

All notable changes to this feature follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Semantic versioning per [SemVer](https://semver.org/).

---

## [1.0.0] — 2026-05-30

### Added

- **Course authoring** — `POST /courses` for methodists to create draft courses (title, description ≤ 500 chars, optional cover image URL). Rate-limited at 30 req/min/user. (PRD US-01, AC-01, AC-02, AC-09)
- **Block-based lesson creation** — `POST /courses/{id}/lessons` with structured body (text / video_embed / image / code blocks). Sequence auto-assigned if omitted; explicit sequence protected by `UNIQUE(course_id, sequence)` at DB level — concurrent inserts return 409 `lesson.sequence_conflict`. (PRD US-02, AC-03, AC-04, AC-04b, AC-10)
- **Content blocks** — `POST /lessons/{id}/blocks` to append polymorphic blocks per ADR-0001. (PRD US-02)
- **Course and lesson publishing** — `POST /courses/{id}/publish` and `POST /lessons/{id}/publish`, both idempotent via `Idempotency-Key` header + Redis dedup (24h window). Course publish gated on ≥ 1 published lesson (AC-05). Both publish operations enqueue outbox events (`course.published`, `lesson.published`) in the same transaction. (PRD US-03, AC-05, AC-06)
- **Course and lesson reading** — `GET /courses`, `GET /courses/{id}`, `GET /lessons`, `GET /lessons/{id}`. Cross-org reads on published resources return 404 `course.not_found` (existence-hiding, AC-07 deviation from mentorship-style 403). Draft courses visible only to `course_owner` + `admin`. (PRD US-04, AC-07, AC-08)
- **Lesson reorder** — `PATCH /courses/{id}/lessons/reorder` — bulk sequence update in single transaction; draft-only; payload bounded at 50 items (DoS mitigation). (PRD US-05)
- **Lesson completion tracking** — `POST /lessons/{id}/completion` — idempotent: first call returns 201, subsequent calls return 200 with unchanged `completed_at`. Allowed only on published lessons of caller's org. (PRD US-06, AC-11, AC-12)
- **GDPR peer-visibility preference** — `GET /me/preferences` and `PATCH /me/preferences`. Default `peer_visibility: private` (privacy-by-default). Every change logged to `user_preference_audit` for GDPR compliance recall. (PRD US-07, AC-13)
- **Peer-completion signal** — `GET /lessons/{id}` response enriched with `peer_completion: {count, recent_completers[], my_completed}`. Count of completions within caller's org; up to 5 most-recent completers with `peer_visibility: public`. Anti-fingerprinting: if `count < 3`, response returns `count: null` and empty completers list. Peer-blob cached in Redis with 60-second TTL; cache miss falls back to live DB read. (PRD US-08, AC-14, AC-15; ADR-0002)
- **Lesson comments** — `POST /lessons/{id}/comments` (plain text ≤ 2 000 chars, server-side HTML-escaped, rate-limited at 10/hour/user) and `GET /lessons/{id}/comments` (cursor-paginated, hidden comments shown with placeholder). (PRD US-09, AC-16, AC-17)
- **Comment moderation** — `POST /comments/{id}/hide` — admin-only action; flips status to `hidden`, replaces content with `[hidden by moderator]`, preserves original in `comment_audit` for compliance recall. (PRD US-10, AC-18)

### Migrations

- `20260523000001_add_is_methodist_to_org_members` — ALTER `org_members` to add `is_methodist BOOLEAN NOT NULL DEFAULT false`.
- `20260523000002_create_course_lesson_tables` — 8 new tables: `courses`, `lessons`, `lesson_blocks`, `lesson_completions`, `user_preferences`, `user_preference_audit`, `comments`, `comment_audit`.
- `20260523000003_add_course_lesson_indexes` — composite indexes for publish-gate query, peer-blob hot path, and comments pagination.

### Architecture decisions

- **ADR-0001** — Lesson body stored as typed rows in `lesson_blocks` table (not a monolithic JSON document). Enables atomic single-block edits and O(N) batch reorder within lesson.
- **ADR-0002** — Redis introduced as shared infrastructure for per-user rate-limiting (token-bucket) and peer-blob caching (60s TTL). Redis failure degrades gracefully: peer-blob falls back to live DB read; publish endpoints fail-close (503) on idempotency store unavailability.

### Known limitations (deferred to v2)

- Native video upload not supported; `video_embed` blocks store external URLs only (YouTube / Vimeo, allowlist TBD per OQ-1).
- Edit-after-publish not supported; published content is immutable in v1. Workflow: unpublish → edit → republish.
- Comments are flat (no threading, no reply-to-reply). Notification fan-out on new comment deferred.
- Public profile pages aggregating a user's completed courses are out of scope (privacy aggregation vector, PRD §3).
- Course catalog / full-text search deferred (fewer than 10 published courses per org in pilot phase).

---

[1.0.0]: https://github.com/genkovich/agentic-engineering-course/compare/...course-lesson-mvp-v1.0.0
