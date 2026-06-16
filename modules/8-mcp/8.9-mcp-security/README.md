# Demo: mcp-security

**Module:** 8 - MCP
**Lecture:** 8.9 - Безпека MCP: модель загроз і захисти

## Що показує

Інспекційна фікстура для **tool poisoning** (отруєння інструмента): дві версії
одного сервера-калькулятора. У `server.poisoned.ts` інструмент `add` має
безневинний title «Add two numbers», але його `description` ховає блок
`<IMPORTANT>` з командою для моделі - прочитати `~/.ssh/id_rsa` і передати вміст у
параметрі `note`. `server.safe.ts` - чистий двійник: той самий `add`, чесний опис,
без `note`.

**Нічого реально не краде.** Handler обох серверів просто додає два числа і
ігнорує `note`. Уся небезпека - у тексті опису, який модель читає як інструкцію і
не відрізняє від довіреного. Тека вчить читати описи сервера **очима моделі** через
Inspector ще до підключення.

## Структура

```
8.9-mcp-security/
├── README.md               цей файл
├── Makefile                install / build / inspect-poisoned / inspect-safe / clean
├── package.json            build=tsc
├── tsconfig.json
└── src/
    ├── server.poisoned.ts  add зі схованими інструкціями в description + параметр note
    └── server.safe.ts      add з чесним описом, без note
```

## Pre-requisites

- Node.js 20+ і npm

## Як запустити

```bash
cd 8.9-mcp-security

make inspect-poisoned   # tools/list: у description видно блок <IMPORTANT> і параметр note
make inspect-safe       # tools/list: чистий опис того самого add для контрасту
```

Постав два виводи поруч. У отруєному `description` поля `add` - інструкції моделі,
згадка чужого файлу, прохання передати дані у параметр і «не повідомляй
користувачу». У чистому - один рядок без жодного з цих прапорців. Це і є дві
хвилини аудиту, після яких рішення про підключення стає поінформованим.

## Захист - складання п'яти рівнів

Аудит описів (те, що робить ця тека) - лише один рівень. Жоден не достатній сам по
собі:

1. **Перевірене джерело і фіксація версії** - `package@1.2.3` вимикає rug pull.
2. **Аудит описів перед підключенням** - саме цей прийом: tools/list через Inspector.
3. **Мінімальні дозволи** - поіменно на інструмент, не сліпий `mcp__server__*`.
   Annotations (readOnlyHint) - самодекларація сервера, на ній авто-дозвіл не будують.
4. **Політика організації** - allowlist/denylist через керовані налаштування.
5. **Ізоляція секретів** - токени лише у змінних оточення процесу, ніколи у параметрах.

## Source

- Лекція 8.9 у Obsidian vault: `Own Brand/AI Course/Claude Course/Module 8/Lecture 9/`
- MCP Inspector: `https://github.com/modelcontextprotocol/inspector`
- Специфікація MCP: `https://modelcontextprotocol.io/specification`
