---
name: welcomer
description: >
  Greet a user starting a new project and walk them through a minimal onboarding
  checklist. Use when the user opens a fresh repo, says "let's start", "новий проєкт",
  "kickoff", or asks how to begin. Use even if the user does not mention onboarding
  or welcome by name.
allowed-tools: Read, Bash
---

# Welcomer

Універсальний onboarding skill (standalone версія — буде сконвертована в plugin у скринкасті 6).

## Workflow

1. Прочитай `README.md` у поточній директорії якщо існує — отримай контекст проєкту
2. Виконай `git log -1 --format="%h %s"` щоб зрозуміти останній стан репо
3. Запропонуй користувачу 3 наступні кроки на основі контексту:
   - Що варто прочитати першим
   - Яка команда дасть швидкий результат
   - На що звернути увагу в архітектурі
4. Заверши коротким підсумком у дві-три фрази

## Тон

Дружній, прямий, без зайвих формальностей. Українською якщо користувач писав українською, англійською — інакше.
