---
description: Greet the user and demonstrate plugin namespacing.
---

Привітайся з користувачем коротким повідомленням. Поясни, що ця команда живе всередині плагіна, тому викликається як `/hello-plugin:greet` — namespace-префікс береться з поля `name` у `.claude-plugin/plugin.json`.

Якщо щось виглядає несподівано — нагадай користувачу про `/reload-plugins`: команда підхоплює правки плагіна без рестарту сесії.

Не виконуй жодних tool calls — це pure-text command для демонстрації namespacing.
