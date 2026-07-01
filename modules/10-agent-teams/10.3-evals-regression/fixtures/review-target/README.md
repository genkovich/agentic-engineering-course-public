# review-target fixture

Дрібний код (`src/discount.js`) для golden-task `subagent-tools-allowlist`.

`setup.sh` робить git-репо й засаджує зміну в історію (HEAD~1..HEAD), щоб read-only
агенту `ro-reviewer` було що рев'ювати. Allowlist інструментів агента (Read, Grep, Glob,
Bash — без Write/Edit) — це предмет eval: рев'юер має згенерувати рев'ю, але НЕ змінити файли.
`check.sh` асертить `git status`/`git diff` по `src/` порожній.
