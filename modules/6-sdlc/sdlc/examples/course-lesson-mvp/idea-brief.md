---
status: Confirmed
owner: "genkovich"
reviewers: []
updated_at: "2026-05-21"
feature_size: M
stage: "01"
ticket: "<!-- TBD -->"
value_score:
  rice: 81
  state: confirmed
  confirmed_at: "2026-05-21"
feasibility_state: confirmed
---

<!-- Anti-pattern enforcement (Claude self-check, не user-visible):
     Заборонені терміни у тілі: Postgres, Redis, Kafka, конкретні library names,
     SM-2/FSRS/Leitner, схеми таблиць, API endpoints, latency targets, SLOs.
     Це PRODUCT brief. Tech живе у SPEC §6 + architecture-brief + ADR (gate 3+). -->

# Idea brief — course-lesson-mvp

## 1. Raw idea

MVP уроку курсу всередині BeerLMS: дати методистам місце, де можна спакувати знання у послідовність уроків (текст + embed-відео) і опублікувати для членів своєї org. Це наступний крок після mentorship-модуля: продукт перестає бути 1-on-1-інструментом і стає платформою з двома способами доставки контенту — синхронним mentorship і асинхронним курсом — в одному org-scoped продукті.

## 2. Problem

Сьогодні BeerLMS без course-lesson — це mentorship-tool, а не повноцінний LMS: це core feature gap, який блокує product completeness. Course delivery фрагментований по Notion / Slack threads / ad-hoc docs; методисти витрачають дні на верстку одного уроку поза платформою. Студенти втрачають context і мотивацію між фрагментами; org-membership і шар mentorship губляться, бо матеріал живе зовні.

## 3. Users

- ~80 active learners в організації (споживачі контенту)
- 5-10 course authors (методистів) — пакують знання у курси
- 2-3 admins — керують доступом і батч-аналітикою

Severity: обидва сегменти однаково страждають (authors блокують swap-out з Notion, learners втрачають продовження). Segmentation learners: 60% активний прогрес, 30% return-after-pause, 10% new joiners.

## 4. Why now

Без course-lesson BeerLMS лишається mentorship-only — і наступний product-step (платні курси, аналітика, cross-org) заблокований. Mentorship module shipped 5 тижнів тому — це доводить, що команда має capability на content-delivery feature з реюзом auth, org-membership і DDD layout. Q3 onboarding cycle потребує асинхронної доставки знань як must-have.

## 5. Out of scope

- Native video upload (constraint: немає video storage у v1; embed-URL only)
- Dashboards / аналітика прогресу студентів
- Multi-tenant cross-org subscription
- Mobile native застосунок
- Сертифікація і iframe-вбудовування
- Payment integration і ціна-як-атрибут
- Edit-after-publish workflow з версіонуванням (deferred to v2)
- Email / push notification про новий курс (deferred to v2)
- Search / course catalog (deferred — поки <10 courses не потрібен)

## 6. Competitive analysis

| # | Product · URL | Features | Value per feature (1-5) | Gap |
|---|---|---|---|---|
| 1 | Teachable · https://teachable.com | course bundles; drip content; payment | 4 / 3 / 5 | external SaaS; нема org-membership / mentorship інтеграції |
| 2 | Thinkific · https://thinkific.com | course delivery; quizzes; certificates | 4 / 4 / 3 | external SaaS, без internal-team focus |
| 3 | Notion / Google Docs combo · https://notion.so | rich editing; collaboration; wiki | 5 / 5 / 2 | немає lesson-progression, completion tracking, peer signals |
| 4 | Chamilo / Moodle · https://chamilo.org | full LMS; self-hosted; mature | 4 / 5 / 3 | окремий silo system; не tied до BeerLMS auth/mentorship/org |
| 5 | iSpring · https://ispringsolutions.com | corporate LMS; compliance | 5 / 4 / 3 | enterprise overkill; нема mentorship layer |

Footnotes: WebSearch виконано 2026-05-21: "best lightweight LMS for small internal teams 2026", "course authoring tool internal company training 2026", "Notion vs LMS internal team training 2026", "simple lesson builder embed video markdown 2026".

## 7. Strategic approaches

### Approach A — Sequential Content with URLs
- **Thesis**: методисти створюють lesson sequences з тексту і опційного embed-video URL; мінімальні нові entities (course, lesson), reuse mentorship DDD layout.
- **For whom**: methodists, які хочуть швидкого swap-out з Notion; learners з лінійним consume-flow.
- **Outcome metric**: 3 опубліковані курси у перший місяць (baseline 0).
- **Key trade-off**: feature parity, не differentiation — нема engagement signal для авторів.
- **Effort signal**: S/M (3-5 person-weeks)
- **Recommended?** ◯

### Approach B — Mentorship-Anchored Course Progression
- **Thesis**: уроки стають mentoring checkpoints; mentor посилається на lesson у session notes; learner бачить "book mentorship from this lesson" CTA.
- **For whom**: methodists, які поєднують async + 1-on-1 pedagogy (leadership, coaching, technical depth).
- **Outcome metric**: ≥40% mentorship sessions reference lesson (baseline 0%).
- **Key trade-off**: tight coupling mentorship+lesson sticky, hardest to unship.
- **Effort signal**: M/L (5-7 person-weeks)
- **Recommended?** ◯

### Approach C — Progressive Async Learning + Social Completion
- **Thesis**: Approach A core + lightweight peer completion visibility ("3 people finished this today") з public/private toggle per learner.
- **For whom**: усі сегменти; addresses devil's vector #1 (methodist ghosting) via social signal.
- **Outcome metric**: 3 опубліковані курси + ≥40% methodist activation у 60 днів.
- **Key trade-off**: empty-state demotivation на старті (0 finished); privacy/consent policy work.
- **Effort signal**: M (3-5 person-weeks)
- **Recommended?** ●

## 8. Multi-perspective feedback

### Engineer
- A: мінімальний data shape; reuse existing state-machine; найнижчий integration risk
- B: highest coupling — зміна mentorship contract ripples у lesson; bidirectional cycle ризик
- C: одна додаткова entity на hot write path; peer-visibility privacy boundary; reversible якщо unused
- Across all: authz surface критичний (org-scoped read; methodist-only write); embed-URL allowlist sanitization

### Executive
- A: fastest path до feature parity з Teachable/Notion; defensive, не sells; нема premium pricing lever
- B: найсильніший moat — unique для BeerLMS; виправдовує higher ACV; misses month-1 KPI ризик
- C: best risk-adjusted ROI; demo-able social proof; sets up next-sellable analytics
- Across all: 3 published courses у місяць 1 = adoption proof для наступного sales cycle

### UX-researcher
- A: lowest friction але fragile completion psychology — abandonment risk high після lesson 2-3
- B: steep onboarding — decision fatigue per lesson; learners можуть substitute mentorship за completion
- C: bandwagon effect посилює completion; private toggle respects autonomy; risk = "0 finished" demotivates early
- Across all: mobile experience і a11y — 35%+ access from phone; embed iframes notoriously bad mobile

### Synthesis matrix
|         | Engineer | Executive | UX |
|---------|:--------:|:---------:|:--:|
| App. A  | +        | 0         | 0  |
| App. B  | -        | +         | -  |
| App. C  | 0        | +         | +  |

6-word justifications:
- A+Engineer: minimal data, reusable patterns, low risk
- A+Executive: closes gap defensively, no moat
- A+UX: low friction, weak completion psychology
- B+Engineer: high coupling, sticky, hardest unship
- B+Executive: strongest moat, premium pricing lever
- B+UX: steep onboarding, decision fatigue lessons
- C+Engineer: one bounded surface, reversible risk
- C+Executive: best risk-adjusted ROI, demo-able
- C+UX: strongest completion via social proof

## 9. Trade-offs and edge cases

### Trade-offs per approach
| Approach | Pros | Cons |
|---|---|---|
| A | shortest path; reuses mentorship; zero new infra | no engagement signal; defensive only |
| B | strongest moat; compounds mentorship ROI; defensible | overshoot timeline; coupling sticky; doubles test matrix |
| C | balanced TTM з differentiation hook; reversible | empty-state demotivation; privacy/consent extra scope |

### Edge cases
- Cold start: course publishes з 0 lessons — empty TOC for learner
- Embed-URL broken (YouTube link deleted / corporate proxy blocks) — black box у lesson reader
- Author edits published lesson — learner returning to changed content без notification
- Sequence conflict — два автори reorder одночасно
- Cross-org leak: lesson URL shared у Slack потрапляє до non-member; має 404, не 403
- Mobile reading (35%+ users) — embed iframes responsive
- Accessibility: screen reader friendly heading hierarchy; video транскрипти deferred
- Returning learner після 6 місяців — "resume from where I left off?" pointer
- Empty-state social count: "0 finished" demotivates cohort

## 10. Risks

- **Methodist ghosts після course #1** (devil's top vector): success metric "3 published courses" вимірює launch, не retention; without engagement signal autori revert до Notion. Mitigation: Approach C social completion дає авторам real-time engagement feedback; pilot з 1 курсом за 4 тижні і check 2nd-course completion за тиждень.
- **No completion signal** на lesson level: без mark-as-read CTA learners не знають що finished; methodist бачить empty dashboard. Mitigation: Approach C lesson_completion entity = explicit signal.
- **Embed-video breakage у corporate networks**: ~20-40% learners бачать black box. Mitigation: open-in-tab fallback + clear "video unavailable" UI.
- **Cross-org leak** через shared URL: tenant scoping bug на route layer. Mitigation: org-scoped filter як invariant на repo рівні (mentorship pattern), E2E test cross-org.
- **One-way publish trap**: methodist publishes з typo, panic-unpublishes, learners втрачають progress. Mitigation: invariant "published lesson не deletable", edit-after-publish deferred до v2 з versioning.
- **Reorder corrupts progress**: якщо completion key = (user, position), reorder ламає state. Mitigation: completion key = (user, lesson_id), не position.

## 11. RICE — Claude proposed

- **Reach (R) = 90** — 5-10 active methodists + ~80 learners affected per quarter (cite §3 Users; обидва сегменти однаково страждають per Phase 2)
- **Impact (I) = 3 (massive)** — core feature gap; без course-lesson BeerLMS = mentorship-tool, не повноцінний LMS (cite §2 Problem + Executive perspective §8: "closes Notion+Teachable gaps defensively")
- **Confidence (C) = 0.9** — high signal: mentorship adjacent shipped 5w ago (proven capability); WebSearch confirms competitive gap; 5 open questions remain (§15), але не блокують direction
- **Effort (E) = 3 person-weeks** — Approach C lower-bound під reuse-pressure mentorship DDD patterns + simple completion entity; tight bound (cite §7 Effort signal M)
- **RICE = 90 × 3 × 0.9 / 3 = 81**
- **State**: confirmed

## 12. Feasibility — Claude proposed

- [☐] **Tech**: немає video storage у v1 → native upload неможливий; для Approach C embed-only model обходить це обмеження, але explicitly bounds scope. Реюз mentorship/org/auth DDD patterns знімає інші tech ризики.
- [☑] **Skills**: команда shipped mentorship 5 тижнів тому з ідентичним DDD layout (domain/app/ports/infra); FE FSD live (entities/features/pages); нема нових технологій для Approach C.
- [☑] **Time**: 3 person-weeks fits у timeline 4-6w; mentorship reference baseline (5w) дає proof of velocity; reuse patterns зменшують unknowns.
- **State**: confirmed

## 13. Recommendation

**Selected: Approach C — Progressive Async Learning + Social Completion**

Rationale: RICE = 81 (§11) — strong value/effort ratio з aggressive E=3 weeks bound і I=3 max. Feasibility 2/3 ☑ (§12) — Skills+Time confirmed; Tech ☐ через no video storage прийнятно бо Approach C embed-only design bypasses constraint. §8 synthesis matrix: C+Executive **+** ("best risk-adjusted ROI, demo-able") і C+UX **+** ("strongest completion via social proof") — найкращий cross-persona balance; addresses devil's vector #1 (methodist ghosts після course #1) через lightweight social signal який дає авторам engagement feedback. Закриває §6 competitive gaps одночасно: Notion (no lesson progression + no completion tracking) AND Teachable/Thinkific (no org-membership integration) — peer completion uniquely можливий бо BeerLMS має shared org-membership identity.

**Locked-in pointer**: write-spec phase commits to text-first content model з embedded-media URL support + lesson_completion entity з public/private toggle per learner. No native video, no notification, no search в v1.

## 14. Parked & rejected approaches

| # | Approach | Status | Reason | Revisit trigger |
|---|---|:---:|---|---|
| A | Sequential Content with URLs | parked | superset без social-completion seed; missing engagement signal | if C empty-state demotivates після 60 днів і social proof не landing |
| B | Mentorship-Anchored Course Progression | parked | M-L effort overshoot 4-6w timeline; tight mentorship coupling | revisit після C ships і коли є capacity на cross-module integration |
| - | Native video upload | rejected | no video storage у v1; embed-URL valid path | якщо storage infra ships і >80% lessons потребують native player |
| - | Notion-style WYSIWYG editor | rejected | XL scope, beyond MVP capability | якщо avg lesson > 30 хв reading time і rich formatting blocks UX |

## 15. Open questions

- [ ] Rich-text формат: markdown vs structured blocks vs sanitized HTML allowlist? — owner: TL, due: 2026-05-28
- [ ] Embed-URL allowlist policy: тільки YouTube/Vimeo чи broader? — owner: TL, due: 2026-05-28
- [ ] Maximum size для image attachments у lesson body? — owner: PM, due: 2026-05-28
- [ ] Lesson completion: explicit "Mark complete" button vs auto-on-scroll-bottom? — owner: PM + TL, due: 2026-06-05
- [ ] Privacy toggle default: public-by-default чи private-by-default (GDPR consideration)? — owner: PM, due: 2026-05-28
- [ ] Cold-start strategy: launch з 3 seed courses чи з порожнім каталогом? — owner: PM, due: 2026-06-05

## Related

- [CONTEXT.md](./CONTEXT.md) — domain glossary (course, lesson, methodist, draft, published, content_type, sequence, cover_image, description, course_owner)
- [PRD.md](./PRD.md) — Stage 03 product requirements (existing)
- [idea-brief.v1.md](./idea-brief.v1.md) — попередня версія (Approach A recommendation, для порівняння)
- Mentorship module (adjacent shipped, reference для Tech/Skills/Time feasibility)
- BeerLMS Q3 onboarding cycle

## DoD self-check

- [x] 15 sections present
- [x] No anti-pattern terms (Postgres/Redis/SM-2/etc.)
- [x] Length ≤ 5 pages (~2200 words)
- [x] Frontmatter status: Confirmed
- [x] RICE confirmed (state: confirmed)
- [x] Feasibility confirmed (state: confirmed)
- [x] Recommendation cites §6, §8, §11, §12
