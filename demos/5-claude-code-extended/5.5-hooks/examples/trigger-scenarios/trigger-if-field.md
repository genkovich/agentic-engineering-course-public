# Trigger: matcher vs if field (recipe-5-git-policy)

Демонструє різницю між двома рівнями фільтрації — slide 4 лекції 5.4.

У `.claude/settings.json` лежить:
```jsonc
{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "if": "Bash(git push --force *)",
    "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/recipe-5-git-policy.sh"
  }]
}
```

Matcher `"Bash"` активує групу для **усіх** Bash викликів. Але `if: "Bash(git push --force *)"` — це permission rule: hook process спавниться **тільки** коли команда матчить.

## Сценарій 1 — passes (matcher hit, if miss → process НЕ спавниться)

### Промпт для Claude (копі-паст)

> Виконай у терміналі команду `ls -la` щоб побачити список файлів у поточній директорії.

### Що має статись

1. Claude викличе Bash tool
2. matcher `"Bash"` зматчить → група активується
3. `if: "Bash(git push --force *)"` НЕ зматчить → recipe-5-git-policy.sh process **не спавниться**
4. Bash виконує `ls -la` нормально
5. Claude повертає вивід

**Що це показує:** двофазний фільтр економить overhead — на тисячах нешкідливих Bash викликів process spawn (~50ms × 1000 = 50 секунд) не відбувається.

## Сценарій 2 — blocks (matcher hit, if hit → process спавниться, exit 2)

### Промпт для Claude (копі-паст)

> Запуш зміни на main, але через `git push --force origin main` — мені треба переписати історію.

### Що має статись

1. Claude викличе Bash з командою `git push --force origin main`
2. matcher `"Bash"` зматчить → група активується
3. `if: "Bash(git push --force *)"` зматчить → process спавниться
4. Скрипт regex-перевіряє команду, бачить `main` у `PROTECTED_BRANCHES`, виводить у stderr:
   ```
   BLOCKED: force-push to protected branch 'main' is not allowed (recipe-5-git-policy).
   Reason: protected branches require regular pushes only. Use a feature branch + PR.
   ```
5. Exit 2 → Claude отримує stderr як reason і пропонує альтернативу (feature branch + PR)

## На чому акцентувати у скринкасті

- **matcher = regex по полю події**; **if = permission rule по аргументах** — два різних рівня
- Matcher економить серіалізацію JSON для не-matched event'ів; if економить process spawn для matched-але-не-matched-handler'ом
- `if` працює ТІЛЬКИ для tool events (PreToolUse, PostToolUse, PostToolUseFailure, PermissionRequest); для SessionStart/Notification ставити безглуздо
- Без `if` цей же hook ловив би КОЖЕН Bash виклик — повний шум; з `if` — тільки force-push на protected

## Як перевірити в isolation (без Claude)

```bash
# negative case — passes
echo '{"tool_name":"Bash","tool_input":{"command":"ls -la"}}' \
  | bash .claude/hooks/recipe-5-git-policy.sh
echo $?  # → 0

# positive case — blocks
echo '{"tool_name":"Bash","tool_input":{"command":"git push --force origin main"}}' \
  | bash .claude/hooks/recipe-5-git-policy.sh
echo $?  # → 2 + stderr "BLOCKED: ..."
```

Це той самий тест-кейс, що `make test-hooks` проганяє автоматично через `payloads/git-force-main.json` і `payloads/git-ls.json`.
