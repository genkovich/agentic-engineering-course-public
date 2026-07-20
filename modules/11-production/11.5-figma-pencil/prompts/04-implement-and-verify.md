# Prompt 04 · Approved design → code → browser

Для Official/Console використовуй frame URLs. Для Pencil заміни `DESIGN_SOURCE` на
`design/main-screen.pen`.

```text
Implement the approved design from DESIGN_SOURCE in this repository.

Figma references when applicable:
- desktop: <DESKTOP_FRAME_URL>
- mobile: <MOBILE_FRAME_URL>

Before editing:
1. read design/brief.md and design/definition-of-done.md;
2. inspect the current screen and identify its existing owner;
3. inspect the approved desktop and mobile design;
4. list the small set of files you plan to change.

Implementation rules:
- preserve the working behavior named in the brief;
- reuse existing project components, styles, and conventions;
- do not add a new UI library without explicit approval;
- implement desktop and mobile from one responsive screen;
- include all applicable states from the brief;
- modify the real current screen, not a separate demo route.

After editing:
- discover and run the typecheck, lint, tests, and build commands that actually exist in this repo;
- start the application at <APP_URL>;
- capture desktop 1440px and mobile 390px screenshots;
- compare them with the approved design;
- verify the existing behavior from the Keep section;
- report changed files and remaining differences.

Do not claim completion only from the agent summary. Return command output,
browser evidence, and git diff summary.
```
