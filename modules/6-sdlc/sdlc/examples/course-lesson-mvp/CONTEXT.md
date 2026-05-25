---
status: Living
updated_at: "2026-05-21"
---

# Domain Context — Course Lesson MVP

<!--
Це доменний словник фічі course-lesson-mvp для BeerLMS. У ньому живуть лише доменні
слова, якими говорить команда: course, lesson, methodist, draft, published тощо.
Кожен запис фіксує одне канонічне значення і одне NOT-посилання на найближчий
омонім — щоб через шість місяців «lesson» не перетворилось на «mentorship-session»
у новому коммітs або у новій Claude-сесії.

Записи зʼявляються інкрементально: у мить, коли термін виринає в інтервʼю,
brainstorm чи SPEC — fix-term зупиняє розмову і дописує рядок сюди. Деталі
імплементації (схема Postgres, S3-bucket, конкретні бібліотеки) сюди не йдуть —
їм місце в `architecture-brief.md` або `SPEC.md`.

Назви термінів лишаються англійською (так вони зʼявляться в коді як ідентифікатори:
`Course`, `Lesson`, `Methodist`); описи — українською, для україномовної команди і
студентів курсу.
-->

## Glossary

- course — публікований методистом bundle уроків зі сталою назвою і описом. NOT mentorship-session: mentorship-session — це 1-on-1 живий синхронний таймслот між ментором і менті; course — асинхронний навчальний пакет, який споживає будь-який член org без присутності автора.
- lesson — атомарна одиниця контенту всередині курсу (текст або URL на відео). NOT mentorship-session-note: нотатка з ментор-сесії — особисті записи про живу зустріч; lesson — публічний навчальний крок, який автор готує наперед і публікує для аудиторії.
- methodist — користувач з правом створювати і публікувати курси у своїй org. NOT mentor: ментор веде 1-on-1 mentorship-сесії з менті; методист створює асинхронний курсовий контент для всієї org.
- draft — статус курсу/уроку, видимий тільки автору. NOT private: private — це загальна категорія видимості («не публічно»); draft — конкретний стан життєвого циклу контенту до публікації, що знає workflow перевести у published.
- published — статус курсу/уроку, видимий усім членам org. NOT public: public — це загальна категорія видимості («доступно всім»); published — конкретний стан життєвого циклу контенту, який пройшов перевірку автора і відкритий для членів org (але не для не-членів).
- content_type — тип контенту уроку: text / video_embed / mixed. NOT format: format — це загальне слово про вигляд (markdown, HTML, video); content_type — фіксований enum з трьох значень, що визначає рендеринг lesson-сторінки.
- sequence — порядок уроків у курсі (integer ordering). NOT priority: priority — це шкала важливості з різним семантикою; sequence — позиційне число (1, 2, 3...) у послідовному списку уроків, на яке покладається UI рендеру.
- cover_image — preview зображення курсу для списку курсів і shared-карток. NOT thumbnail: thumbnail — це згенерована превʼюшка з відео; cover_image — навмисно завантажене методистом зображення, що репрезентує курс як ціле.
- description — короткий опис курсу (≤500 символів) для списків і пошуку. NOT bio: bio — це опис користувача-методиста як особистості; description — опис конкретного курсу як продукту.
- course_owner — методист, який створив курс і має повні права на редагування та публікацію. NOT admin: admin — це оператор org з правами на біллінг і tenant-management; course_owner оперує лише в межах своїх курсів.

## Invariants

- Кожен `lesson` належить рівно одному `course`; видалення курсу каскадно знищує його уроки.
- Курс можна перевести у `published` тільки якщо у ньому хоча б один опублікований урок.
- `sequence` унікальний у межах одного курсу і не змінюється автоматично при додаванні нових уроків — методист явно перевпорядковує список.

## Sentinel errors

Доменні sentinel errors (snake_case `module.error_name`), які повертає `internal/modules/lessons/` і мапляться у ports у HTTP-коди.

```
- lesson.not_found
- lesson.sequence_conflict
- course.not_found
- block.invalid_type
- block.sequence_conflict
```

## Org-filter invariant

Бізнес-правило, не SQL-level constraint:
- Усі `SELECT` у repo фільтрують `WHERE org_id = $1` (org context з middleware).
- Cross-org lookup → `ErrLessonNotFound` (existence-hiding, PRD AC-07).

## Out of scope

- Native video upload зі сторінки методиста — v1 тримаємо тільки `video_embed` URL (YouTube/Vimeo); власне сховище — окрема ініціатива.
- Платні курси, payment gateway, ціна-як-атрибут — поза скоупом v1; всі курси у v1 видимі всім членам org однаково.
- Cross-org subscription (не-член org бачить опублікований курс) — поза скоупом v1; видимість обмежена membership у тій самій org.
