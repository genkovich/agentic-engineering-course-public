# debug-viewer

Три tail-обгортки для live-перегляду JSONL логів, які пишуть `debug-*` hooks.

| Скрипт | Файл логу | Що показує |
|---|---|---|
| `tail-trace.sh` | `.claude/logs/tool-trace.jsonl` | кожен PreToolUse/PostToolUse — назва tool, file_path або command |
| `tail-subagent.sh` | `.claude/logs/subagent.jsonl` | SubagentStart/Stop — type, description |
| `tail-transcript.sh` | `.claude/logs/transcript.jsonl` | UserPromptSubmit + Stop — preview промпта, stop reason |

## Як використовувати у скринкасті

```
термінал A:  make tail-trace
термінал B:  claude  →  виконати будь-яку задачу
```

В А полетять одна-за-одною лінії типу:

```
2026-05-07T10:14:21Z  PRE   Edit  /tmp/foo.ts
2026-05-07T10:14:21Z  POST  Edit  /tmp/foo.ts
2026-05-07T10:14:22Z  PRE   Bash  ls -la
```

`jq` рекомендується (`brew install jq`), але без нього скрипт просто покаже сирі JSONL рядки.

Дивись також `make tail-trace`, `make tail-subagent`, `make tail-transcript`.
