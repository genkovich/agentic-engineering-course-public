# Prompt 02 · Figma Console MCP

Console — optional advanced route. Перед prompts:

```bash
read -s FIGMA_ACCESS_TOKEN
export FIGMA_ACCESS_TOKEN

claude mcp add figma-console -s user \
  -e FIGMA_ACCESS_TOKEN="$FIGMA_ACCESS_TOKEN" \
  -e ENABLE_MCP_APPS=true \
  -- npx -y figma-console-mcp@latest

npx -y figma-console-mcp@latest --print-path
```

Імпортуй надрукований `manifest.json` через Figma Desktop:
`Plugins → Development → Import plugin from manifest…`, потім запусти Desktop Bridge.

## B0. Connection and write test

```text
Use only figma-console. Do not use Official Figma.

Report:
1. connection status;
2. active Figma file;
3. current page;
4. write capability.

Then create a temporary frame named "Bridge write test" at 320x120,
read it back, and delete it.
Stop after the report.
```

## B1. Create the design

```text
Use only figma-console in the active Figma file.

Read design/brief.md and inspect the current application at <APP_URL>.
Work in three separate checkpoints:
1. variables needed by the screen;
2. reusable native components and applicable states;
3. desktop 1440px and mobile 390px frames.

Use auto layout and attached component instances.
After each checkpoint, read the created nodes back and stop for review.
```

## Cleanup

Після роботи відклич PAT у Figma `Settings → Security`. Якщо Console більше не потрібен:

```bash
claude mcp remove figma-console -s user
```
