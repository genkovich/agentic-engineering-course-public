# edit-loop

**Module:** 5 — Claude Code extended
**Lecture:** 5.5 — Plugins (скринкаст 4)

Before/after одного файлу `greet.md` — демонстрація dev-циклу правки плагіна без install і без рестарту сесії. У `after/` додано рівно одне речення (про `/reload-plugins`), решта файлу ідентична.

## 5-кроковий цикл

1. `claude --plugin-dir ./hello-plugin` — запустити сесію з плагіном
2. `/hello-plugin:greet` — викликати команду, побачити поточну поведінку
3. Поправити `hello-plugin/commands/greet.md` у редакторі (diff = `before/` → `after/`)
4. `/reload-plugins` — у тій самій сесії підхопити правку
5. `/hello-plugin:greet` — повторний виклик, побачити нову поведінку
