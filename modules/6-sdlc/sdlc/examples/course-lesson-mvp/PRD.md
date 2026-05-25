---
status: Draft
owner: genkovich
updated_at: 2026-05-23
stage: "03"
feature_size: M
---

# PRD — course-lesson-mvp

## 1. Context

BeerLMS-org-и сьогодні роздають async-навчання через Notion + Slack: lesson-контент живе у Notion-сторінках, оголошення про публікацію — у Slack-нитках, прогрес ніде не агрегується. Це створює фрагментацію для ~80 learner-ів у пілотних org-ах і ~5–10 methodist-ів, які витрачають час на синхронізацію двох інструментів замість того, щоб виробляти контент (idea-brief §2 Problem, §3 Users).

Mentorship-модуль відвантажений 5 тижнів тому, валідував DDD-патерни (org-scoped repos, OrgMemberChecker, error-codes у форматі `mentorship.snake_case`) і дав reusable foundation. Паралельно Q3-onboarding-цикл починається з Iюня — methodist-ам потрібно публікувати курси в одній поверхні з 1-on-1 mentorship-ом, які learner-и вже відкривають у BeerLMS (idea-brief §4 Why now).

Recommendation: **Approach C — Progressive Async Learning + Social Completion** (RICE = 81, idea-brief §13). v1 повністю покриває Approach C scope: methodist створює course → додає block-based lesson → публікує → member читає → member відмічає completion із privacy toggle → інші members бачать peer-completion count + опційно коментують lesson. Social-completion signal і lesson commenting — **core v1 differentiator** і engagement-feedback для methodists (idea-brief §10 Risks: «methodist ghosts після course #1» mitigated саме цим signal-ом). Threading у commenting, notification fan-out і native video upload — deferred до v2 (див. §3 Non-goals).

Reference patterns mirror mentorship-module: error-коди у форматі `course.snake_case` / `lesson.snake_case` / `validation.*`; authz через middleware `orgmw` + repo-layer `org_id = $1` filter + `OrgMemberChecker.IsMethodist` (mirror `IsMentor`); validation у handler-шарі, не у domain-конструкторі. **Одна свідома девіація:** cross-org-доступ до `published` course повертає **404 `course.not_found`** замість mentorship-овського 403 `org_mismatch` — existence-hiding, rationale у §6.1.

## 2. Goals

- Methodist створює та публікує курси в BeerLMS, а не в Notion → консолідує контент-pipeline у єдиному product surface (idea-brief §13 Approach C, closes competitive gap «no async course delivery»).
- Member споживає async-курси у тому ж продукті, де отримує 1-on-1 mentorship → unified delivery surface; знижує context-switching і друкарню паролів для двох інструментів.
- v1 закладає block-based lesson body (text + video_embed + image + code) як native storage-схему для всіх lesson-форматів → дозволяє інкрементально нарощувати lesson-формати без рефакторингу storage.
- Social-completion signal (peer-completion count + opt-in public list completer-ів) і lesson commenting (text-only, без threading у v1) дають methodist-ам real-time engagement feedback і працюють як bandwagon-effect drive для learner-completion → mitigates devil's-vector #1 «methodist ghosts після course #1» з idea-brief §10.

## 3. Non-goals

- **Native video upload** — `embed_url` only у v1 (YouTube/Vimeo, allowlist у §8). Жодного відео-стораджу і transcoding-пайплайну.
- **Edit-after-publish + course versioning** — published course immutable у v1; редагування → unpublish → re-publish (out of scope для v1 UX). Versioning deferred до v2 (idea-brief §5).
- **Threaded comments / reply-to-reply** — v1 commenting — flat list, reply без вкладеності; threading deferred до v2 разом із comment notification fan-out.
- **Notification fan-out на completion / new comment** — у v1 peer-signal і comments видно лише при відкритті lesson; email/push notify deferred до v2 (потребує consent UX і template-system, які поза scope v1).
- **Public profile pages completer-ів** — public-visibility opt-in робить ім'я completer-а видимим у peer-list лише на тій конкретній lesson page; жодних profile-pages зі списком пройдених курсів у v1 (vector privacy aggregation, поза scope v1 GDPR-моделі).
- **Course catalog / повнотекстовий search** — у пілоті < 10 published courses на org, list endpoint достатньо.
- **Cross-org course subscription, payments, push-notifications** — out of scope v1 (idea-brief §5).

## 4. User stories

Ролі тільки з CONTEXT.md §Glossary: `methodist`, `course_owner`, `member`, `admin`. Нових ролей не вводимо.

- **US-01** — Як `methodist`, я створюю course draft (title required, description plain text ≤500 chars, optional cover_image URL), щоб мати приватний робочий простір для контенту до публікації.
- **US-02** — Як `methodist`, я додаю lesson до свого course draft із block-based body (ordered list з блоків типу `text` / `video_embed` / `image` / `code`; sequence — integer у межах course), щоб структурувати багатоформатний контент в одному lesson.
- **US-03** — Як `methodist`, я публікую course (gate: ≥1 published lesson всередині course — invariant з CONTEXT.md), щоб зробити його видимим member-ам своєї org.
- **US-04** — Як `member`, я переглядаю published course своєї org (lesson list упорядкований за sequence ASC), щоб споживати async-контент у тому ж продукті, де відкриваю mentorship.
- **US-05** — Як `methodist`, я перевпорядковую lessons у своєму course draft (sequence editable до моменту публікації course), щоб коригувати порядок перед виходом без обхідних маневрів.
- **US-06** — Як `member`, я відмічаю lesson як completed (explicit «Mark complete» action), щоб мати персональний прогрес-recall (resume-from) і дати methodist-у engagement-signal.
- **US-07** — Як `member`, я налаштовую peer-visibility preference (public-by-default opt-out vs private), щоб контролювати чи моє ім'я з'являється у peer-completion list на lesson-сторінках моєї org.
- **US-08** — Як `member`, я бачу peer-completion summary на lesson page (count + recent completer-list serialized тільки з public-visibility opted-in users), щоб отримати social proof і bandwagon-engagement signal.
- **US-09** — Як `member`, я залишаю коментар на published lesson (text-only, flat list без threading у v1), щоб публічно ставити запитання або давати feedback methodist-у і peer-ам.
- **US-10** — Як `admin`, я приховую неприйнятний коментар (moderation action), щоб тримати org-discussion-простір clean без видалення audit-trail.

## 5. Acceptance criteria

Кожен AC мапиться на US-NN. Coverage: ≥1 happy / ≥1 error / ≥1 authz / ≥1 domain-invariant / ≥1 cross-context.

| ID | US | Coverage | Outcome |
|---|---|---|---|
| **AC-01** | US-01 | happy | `POST /courses` body `{title, description?, cover_image_url?}` → **201**; response `{id, status:"draft", course_owner_id=caller.user_id, org_id=OrgCtx.OrgID, created_at}`. |
| **AC-02** | US-01 | error / validation | `POST /courses` з `description` довжиною > 500 chars → **400** `validation.description_too_long`. (CONTEXT-інваріант: description plain text ≤500.) |
| **AC-03** | US-02 | happy | `POST /courses/{course_id}/lessons` body `{title, body:[{type:"text",content:"…"},{type:"video_embed",url:"https://youtube.com/…"},{type:"image",url:"…"},{type:"code",language:"go",content:"…"}], sequence?}` → **201**; якщо `sequence` не передано — присвоюється наступний вільний integer у межах course; response містить `{id, status:"draft", sequence, body}`. |
| **AC-04** | US-02 | domain invariant | `POST /courses/{id}/lessons` із явним `sequence=N`, що вже зайнятий іншим lesson у тому ж course → **409** `lesson.sequence_conflict`. |
| **AC-04b** | US-02 | domain invariant (concurrency) | Два одночасних `POST /lessons` із однаковим `sequence` на той самий course → DB unique constraint `UNIQUE(course_id, sequence)` відхиляє один transaction → **409** `lesson.sequence_conflict`. Жодного app-level lock; репозиторій транслює `pq.unique_violation` → доменну помилку. |
| **AC-05** | US-03 | domain invariant | `POST /courses/{id}/publish` на course із 0 published lessons → **409** `course.no_published_lessons`. Перевірка у app-layer гарді (mentorship-патерн), не у domain-конструкторі. |
| **AC-06** | US-03 | happy | `POST /courses/{id}/publish` із ≥1 published lesson → **200**; `course.status="published"`, `course.published_at=now() UTC`. Operation idempotent: повторний publish на already-published course → 200, без зміни `published_at`. |
| **AC-07** | US-04 | authz (cross-org, deviation) | `GET /courses/{id}` із учасника іншої org на **published** course → **404** `course.not_found` (свідома девіація від mentorship-овського 403; rationale у §6.1: existence-hiding не розкриває cross-org membership). |
| **AC-08** | US-04 | authz | `GET /courses/{id}` із member тієї ж org на **draft** course (caller ≠ course_owner ∧ caller ≠ admin) → **404** `course.not_found`. Draft видимий тільки `course_owner` і `admin` ролі цієї org. |
| **AC-09** | US-01 | cross-context (org membership) | `POST /courses` від caller без `org_members.is_methodist = true` у поточній org → **403** `course.not_methodist` (mirror mentorship `not_mentor`). |
| **AC-10** | US-02 | cross-context (parent-child) | `POST /courses/{id}/lessons` де `course_id` належить course іншої org → **404** `course.not_found` (lesson не може прикріпитися до course поза callerʼs org; repo-layer фільтрує `course.org_id = OrgCtx.OrgID` перед attach). |
| **AC-11** | US-06 | happy / idempotency | `POST /lessons/{id}/completion` від member цієї org на published lesson → **201**; запис `lesson_completions{user_id, lesson_id, completed_at, org_id}` створюється з `UNIQUE(user_id, lesson_id)`. Повторний POST → **200** без зміни `completed_at` (idempotent). |
| **AC-12** | US-06 | authz | `POST /lessons/{id}/completion` на draft lesson чи на lesson іншої org → **404** `lesson.not_found`. Completion дозволений тільки на published lesson своєї org. |
| **AC-13** | US-07 | privacy / consent | `PATCH /me/preferences` body `{peer_visibility:"public"\|"private"}` → **200**; default `private` для new user (GDPR-friendly opt-in). Зміна логується у `user_preference_audit` (event-type, before, after, changed_at). |
| **AC-14** | US-08 | happy / privacy-aware | `GET /lessons/{id}` response додатково містить `peer_completion: {count: int, recent_completers: [{user_id, display_name}], my_completed: bool}`. `recent_completers` — last 5 completer-ів у цій org з `peer_visibility="public"` тільки; users з `private` не з'являються у списку, але враховуються у `count`. |
| **AC-15** | US-08 | privacy / anonymization threshold | Якщо `count < 3` у тій org для цього lesson — response повертає `peer_completion: {count: null, recent_completers: [], my_completed: bool}` (anti-fingerprinting для малих org). Threshold value (3) — OQ-7. |
| **AC-16** | US-09 | happy | `POST /lessons/{id}/comments` body `{content: "...", max 2000 chars}` від member своєї org на published lesson → **201**; response `{id, author_id, lesson_id, content, created_at, status:"visible"}`. |
| **AC-17** | US-09 | validation / abuse | Comment content > 2000 chars → **400** `validation.comment_too_long`. Rate-limit: 10 comments / hour / user → 429 `rate_limited` після перевищення (mentorship token-bucket reuse). |
| **AC-18** | US-10 | moderation | `POST /comments/{id}/hide` від admin своєї org → **200**; comment.status → `"hidden"`, content замінюється на placeholder `"[hidden by moderator]"`, оригінальний content зберігається у `comment_audit` для compliance recall. Non-admin → **403** `comment.not_moderator`. |

Coverage check: happy (AC-01, AC-03, AC-06, AC-11, AC-14, AC-16) · error/validation (AC-02, AC-17) · authz (AC-07, AC-08, AC-12, AC-18) · domain-invariant (AC-04, AC-04b, AC-05) · cross-context (AC-09, AC-10) · privacy/consent (AC-13, AC-15) — 6/6 ✓.

## 6. NFR

| Aspect | Target | Measurement |
|---|---|---|
| Latency p95 write | `POST /courses` ≤ **250 ms** | API histogram `http_request_duration_seconds{route="POST /courses"}`, mirrors mentorship `POST /sessions`. |
| Latency p95 read list | `GET /orgs/{orgId}/courses` (page ≤ 100) ≤ **400 ms** | API histogram per route; keyset pagination `(created_at, id)` (mentorship parity). |
| Latency p95 publish | `POST /courses/{id}/publish` ≤ **600 ms** | API histogram; includes invariant check `COUNT(lessons.status='published') ≥ 1`. |
| Latency p95 completion | `POST /lessons/{id}/completion` ≤ **200 ms** | API histogram. Single-row insert із unique-constraint check; idempotent path. |
| Latency p95 lesson read with peer-signal | `GET /lessons/{id}` (з peer_completion blob) ≤ **400 ms** | API histogram. Peer-blob — aggregated query на `lesson_completions` JOIN `user_preferences` LIMIT 5; pre-cache у Redis із 60s TTL per (lesson_id) для high-traffic lesson-pages. |
| Latency p95 comments list | `GET /lessons/{id}/comments?page_size=20` ≤ **400 ms** | API histogram. Keyset pagination `(created_at, id)`; default page_size=20. |
| Throughput write | ≥ **30 req/s per API instance** на `POST /courses` + `POST /lessons` + `POST /completion` + `POST /comments` combined | k6 smoke у CI: `tests/load/course-lesson.js`, threshold у CI pipeline. |
| Availability | **99.9 %** rolling 30-day window для всіх `*/courses` + `*/lessons` + `*/completion` + `*/comments` routes | Inherit BeerLMS-API SLO; alerting через існуючий error-budget dashboard. |

### 6.1 Security / Privacy

- **Data classification:** internal, org-scoped. Нові PII-adjacent поля: `user_preferences.peer_visibility` (privacy preference), `lesson_completions.user_id × lesson_id × completed_at` (behavioural footprint), `comments.author_id × content` (user-generated content + author identity). `course_owner_id` reuse-ить існуючий `users.id`; `cover_image_url` — generic asset URL.
- **AuthN:** наявний JWT-middleware → `UserCtx`.
- **AuthZ multi-layer:**
  1. Middleware `orgmw` витягує `OrgCtx{OrgID, Role}` з headers + DB.
  2. Repo-layer **завжди** додає `WHERE org_id = $1` filter (mentorship pattern; немає прямих SELECT без orgID-предіката). Це поширюється і на `lesson_completions` + `comments` repos.
  3. Write endpoints (`POST/PATCH /courses*`, `POST/PATCH /lessons*`) додатково вимагають `OrgMemberChecker.IsMethodist(orgID, userID) = true` → інакше 403 `course.not_methodist` (AC-09).
  4. Read endpoint `GET /courses/{id}` ділить state-machine: published → видимий всім member тієї ж org; draft → видимий тільки course_owner + admin (AC-08).
  5. `POST /lessons/{id}/completion` і `POST /lessons/{id}/comments` дозволені тільки member-ам тієї ж org на published lesson-ах (AC-12).
  6. `POST /comments/{id}/hide` — тільки `OrgMemberChecker.IsAdmin(orgID, userID) = true` (AC-18).
- **GDPR consent + privacy default:**
  - `peer_visibility` default `private` для new user (privacy-by-default; user explicitly opt-ins у public).
  - Зміна preference логується у `user_preference_audit{user_id, old, new, changed_at}` для compliance recall.
  - Anti-fingerprinting threshold: peer-completion count не показується якщо `< 3` completions у тій org для конкретного lesson (AC-15) — захист від N=2-org-deanonymization (якщо в org 2 members, peer-count=1 точно ідентифікує completer-а).
- **Abuse cases (8):**
  1. **Cross-org read** на published course → 404 `course.not_found` (AC-07). Свідома девіація від mentorship-овського 403 `org_mismatch`: 403 на published-resource розкрив би сам факт існування course у чужому org → information leak про cross-org membership patterns. 404 hide-ить existence повністю.
  2. **Draft leak** через repo-bypass → виключено архітектурно: фільтрація `(org_id, status, course_owner_id)` ⇒ у repo-методі `FindCourseByIDForCaller`, не у handler. Юніт-тест `repo_test.go` має покрити «draft course belonging to other user in same org → returns ErrNotFound».
  3. **SSRF через `video_embed.url` / `cover_image_url`** → allowlist provider-host-ів (YouTube, Vimeo) на pre-validation step. Конкретний allowlist — OQ-1 у §8. Сервер **не** робить outbound fetch на URL у v1 (no metadata extraction).
  4. **Spam-create flood** на `POST /courses` → rate-limit **30 req/min per user** (mentorship parity); після ліміту 429 `rate_limited`. Реалізація — Redis token-bucket у наявному middleware-стеці.
  5. **Sequence-reorder DoS / large payload** на `PATCH /courses/{id}/lessons/reorder` → bound payload розміру `len(items) ≤ 50`; інакше 400 `validation.reorder_payload_too_large`. Захист від O(N²)-фігур у repo-update.
  6. **Peer-completion deanonymization у малих org** → anti-fingerprinting threshold `count < 3` ховає список (AC-15). Mitigation для випадку, коли в org N=2 members і 1 completion → точно ідентифікує completer-а навіть із `private` preference. Threshold value — OQ-7.
  7. **Comment XSS** → server-side HTML escape перед persist; client рендерить через text-only renderer (no `dangerouslySetInnerHTML`). Markdown у comments **out of scope** v1 (plain text only). Конкретна sanitization policy узгоджена з lesson-body OQ-3.
  8. **Comment spam / flood** → rate-limit **10 comments / hour / user** на `POST /lessons/{id}/comments` (AC-17); після ліміту 429 `rate_limited`. Реалізація — Redis token-bucket (re-use mentorship-овської інфраструктури).
- **XSS у lesson body:** policy для `text` / `code` блоків (markdown vs sanitized HTML allowlist; client-side vs server-side highlight) — OQ-3 у §8. До закриття OQ-3 за замовчуванням обираємо plain text + server-side escape; код-блок renders-иться як `<pre><code>`-pair без виконання.
- **Security review verdict:** **Required + elevated**. Нові endpoint-и + authz-boundary + свідома девіація на 404 + GDPR consent flow + anti-fingerprinting threshold + user-generated content (comments) → SecEng review перед merge; додатково PrivacyEng review для peer-visibility + audit-log design.

## 7. KPIs

| KPI | Baseline | Target | Timeframe | Measurement |
|---|---|---|---|---|
| **Methodist adoption** | 0 % (нова фіча, no production data) | ≥ **40 %** активних methodists мають ≥ 1 `published` course | 60 днів після релізу | SQL: `COUNT(DISTINCT course_owner_id WHERE status='published') / COUNT(DISTINCT user_id WHERE is_methodist=true AND active_30d)`. |
| **Published courses count** | 0 | ≥ **3** published courses across all pilot orgs | 30 днів після релізу | SQL: `COUNT(courses WHERE status='published' AND published_at >= release_date)`. Закриває idea-brief devilʼs-vector #1 («methodist ghosts after first course»). |
| **Peer-completion engagement** | 0 % | ≥ **40 %** members з ≥ 1 lesson view у published course своєї org мають ≥ 1 `lesson_completion` запис | 60 днів після релізу | SQL: `COUNT(DISTINCT user_id у lesson_completions) / COUNT(DISTINCT user_id у lesson.viewed)`. Direct measure Approach C social-completion hypothesis: чи completion-button + peer-signal реально drive-ять completion (бо без social proof був би lower). |
| **Public-visibility opt-in rate** | 0 % (default private) | ≥ **25 %** members зі ≥ 1 completion опт-іnyуть `peer_visibility="public"` | 60 днів після релізу | SQL: `COUNT(user WHERE peer_visibility='public' AND has_completion) / COUNT(user WHERE has_completion)`. Перевіряє, чи bandwagon-механіка взагалі працює (якщо <25%, peer-list завжди пустий, signal не landing). |
| **Comment engagement** | 0 | ≥ **15 %** published lesson-ів мають ≥ 1 comment | 60 днів після релізу | SQL: `COUNT(DISTINCT lesson_id у comments WHERE status='visible') / COUNT(lesson WHERE status='published')`. Перевіряє, чи commenting затребуване (якщо <15%, threading у v2 під сумнівом). |

## 8. Open questions

- [ ] **OQ-1 — `embed_url` allowlist для `video_embed` блоку:** YouTube + Vimeo only чи broader (e.g., Loom, Wistia, Mux)? Закриває SSRF / unauthorized-host-vector. **Owner:** TL · **Due:** 2026-05-28.
- [ ] **OQ-2 — Image-block storage strategy:** тільки external embed URL (allowlist-ed CDN-и) чи також signed upload у S3-compatible bucket? Впливає на storage-cost-модель і access-control. **Owner:** TL · **Due:** 2026-05-28.
- [ ] **OQ-3 — Text- / code-block sanitization policy:** для `text` блоку — markdown vs sanitized HTML allowlist vs plain text? Для `code` блоку — список дозволених `language` value-ів, server-side highlight (chroma) vs client-side (highlight.js). Закриває XSS-vector. **Owner:** TL · **Due:** 2026-05-28.
- [ ] **OQ-4 — Lesson sequence numbering convention:** dense 1-based (1, 2, 3, ...) із re-numbering при reorder, чи allow-gaps (1, 10, 20 — insert-friendly без re-numbering)? Впливає на API contract `PATCH /lessons/{id}` + reorder UX. **Owner:** PM + TL · **Due:** 2026-06-05.
- [ ] **OQ-5 — Peer-visibility default + GDPR consent UX:** AC-13 фіксує `private` як default (privacy-by-default). Чи показуємо learner-у nudge-prompt «Ваше ім'я не з'являється у peer-list — opt-in?» при першому completion? Якщо так — копія prompt-у + log explicit consent у `user_preference_audit`. **Owner:** PM + PrivacyEng · **Due:** 2026-05-30.
- [ ] **OQ-6 — Comment moderation policy:** report-and-hide-by-admin (поточний AC-18) vs pre-publish review queue для нових member-ів (первомісячний bias)? Який ownership для moderation у org без admin (single-methodist org)? **Owner:** PM · **Due:** 2026-06-05.
- [ ] **OQ-7 — Anti-fingerprinting threshold для peer-completion count:** AC-15 use `count < 3` (показуємо `null` для малих лічильників). Чи 3 правильна цифра, чи краще 5 (більше hide, але pessimistic для small orgs)? **Owner:** PrivacyEng · **Due:** 2026-05-30.
- [ ] **OQ-8 — Peer-completion cache invalidation strategy:** §6 NFR caches peer-blob у Redis із 60s TTL. Чи цей TTL прийнятний для UX (60s stale `count`), чи треба invalidate-on-write із fan-out? Впливає на write-amplification. **Owner:** TL · **Due:** 2026-06-05.
