# Trigger: session re-inject (recipe-4)

Демонструє slide 6.4 — SessionStart matcher=compact: усе, що скрипт виводить у stdout, додається у контекст Claude **після** compaction.

## Що таке /compact

Коли context window заповнюється, Claude Code пропонує (або сам викликає) compaction — стискає історію розмови у summary, звільняє місце. При цьому губляться деталі: які конвенції проекту, що зараз робиш, які tools використовуєш. SessionStart matcher=compact — точка для re-injection.

## Як викликати /compact у Claude Code

1. Або довести сесію до 70-80% context window (Claude автоматично запропонує compact)
2. Або викликати команду явно: набрати `/compact` у вікні Claude Code

Після compact — recipe-4 спрацьовує і додає у контекст вміст stdout. У наступних повідомленнях Claude вже знає, що це за проект, не питатиме «який стек?», «які конвенції?», «над чим я зараз працював?»

## Промпт для скринкасту (копі-паст)

> Розкажи мені про архітектуру цього проєкту: які hooks тут налаштовані, які умовні позначення (`_slide` коментарі), і чому recipe-2 і recipe-3 — блокуючі, а recipe-1 і analytics — async.

(Навмисно довге питання, щоб згенерувати кілька великих відповідей і наблизитись до compaction. Якщо одне питання не доводить до compact — задай ще 2-3 у тому ж дусі.)

Потім:

> /compact

## Що має статись

1. Claude викликає compact handler — стискає попередню розмову у summary
2. Claude Code запускає SessionStart hooks з matcher=compact
3. recipe-4-session-context.sh виводить у stdout:
   ```
   [session-context reminder — re-injected after compact]
   
   Active demo: hooks-toolkit (lecture 5.4 — Claude Code Hooks).
   Conventions:
     - всі hook scripts у .claude/hooks/, executable, читають stdin JSON
     - блокуючі hooks → exit 2 + stderr; observability → "async": true
     - secrets-strip.py застосовуй ПЕРЕД будь-яким зовнішнім POST/append до trace
     - не редагуй .env/.git — recipe-2 заблокує
   
   Recent commits:
   <git log --oneline -5>
   ```
4. Цей текст додається у контекст Claude як system-приставка перед першим post-compact повідомленням
5. Перевірка: задай питання про project conventions — Claude відповість одразу, без re-discovery з summary

## Expected output (для звірки)

Перші 4 рядки stdout мають бути стабільні (heredoc у скрипті). `Recent commits` залежить від того, що ти комітив — для скринкасту достатньо побачити, що рядок `Recent commits:` з'являється, і під ним є git-history.

```
[session-context reminder — re-injected after compact]

Active demo: hooks-toolkit (lecture 5.4 — Claude Code Hooks).
Conventions:
  - всі hook scripts у .claude/hooks/, executable, читають stdin JSON
  - блокуючі hooks → exit 2 + stderr; observability → "async": true
  - secrets-strip.py застосовуй ПЕРЕД будь-яким зовнішнім POST/append до trace
  - не редагуй .env/.git — recipe-2 заблокує

Recent commits:
<git output here>
```

## На чому акцентувати у скринкасті

- **SessionStart hooks мають кілька matcher'ів**: `startup` (новий запуск), `resume` (продовження), `clear` (`/clear`), `compact` (`/compact`). Цей рецепт — тільки на `compact`
- **stdout, не stderr** — `compact` event робить stdout = injection. Помилка зі stderr ігнорується (slide 5)
- **Динаміка через git log** — рядок `git log --oneline -5` показує останні 5 комітів. Можна замінити на `cat reminders.md`, `gh issue list`, або будь-що, що дає актуальний state

## Як перевірити в isolation (без Claude)

```bash
# Симулюй compact event
echo '{"matcher":"compact"}' | bash .claude/hooks/recipe-4-session-context.sh
echo $?  # → 0
```

Усе, що друкує цей рядок — те саме, що Claude отримає у контекст після compact. Ідеальний baseline для відлагодження повідомлень: спочатку перевір тут, потім `/compact` у живій сесії.

`make recipes-tour` також виконує recipe-4 у блоці «Recipe 4/4» і друкує отриманий stdout у тому ж форматі — корисно для квартирного демо без compaction-сетапу.
