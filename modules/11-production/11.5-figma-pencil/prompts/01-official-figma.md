# Prompt 01 · Official Figma

Замінюй placeholder-и власними значеннями. Виконуй блоки по одному.

## A0. Connection check

```text
Use only the Official Figma integration. Do not modify Figma or code.

Inspect <FIGMA_FILE_URL> and return:
1. authenticated account;
2. file name;
3. page names;
4. edit capability;
5. available read and authoring capabilities.

Stop after the report.
```

## A1. Capture current screen

```text
Use the Official Figma code-to-canvas workflow.

The application is running at <APP_URL>.
Capture the current screen into <FIGMA_FILE_URL> on page "01 Current UI".
Name it "Current UI · desktop".

Do not redesign it. Wait for my confirmation before capture.
After capture, report the created frame name and node ID.
```

## A2. Variables

```text
Use Official Figma authoring in <FIGMA_FILE_URL>.

Read design/brief.md and inspect "Current UI · desktop".
On page "02 Components", create only the variables needed by this screen:
colors, spacing, and radii.

Do not create components or screens yet.
Read the variables back and report their names and values.
```

## A3. Components

```text
Continue in the same file on page "02 Components".

Create native reusable components for repeated controls in this screen.
Include the states listed in design/brief.md.
Use auto layout and the existing variables.

After writing, report component names, variants, and node IDs.
Stop for review.
```

## A4. Desktop and mobile

```text
Continue on page "03 New screen".

Using design/brief.md, the captured UI, variables, and component instances, create:
- "New screen · desktop" at 1440px width;
- "New screen · mobile" at 390px width.

Include all applicable states from the brief.
Do not detach component instances.

After writing, take screenshots, report layout problems, and stop for human approval.
```

Після approval скопіюй `Copy link to selection` для обох frames. Вони стануть
`<DESKTOP_FRAME_URL>` і `<MOBILE_FRAME_URL>` у prompt на implementation.
