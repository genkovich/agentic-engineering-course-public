# Demo: what-is-mcp

**Module:** 8 - MCP
**Lecture:** 8.1 - Що таке MCP: архітектура клієнт-сервер

## Що показує

Конфіг-кит без власного коду. Лекція концептуальна, тож тут немає сервера для
збірки - є один спосіб **побачити архітектуру клієнт-сервер живою** за хвилину:
підключаємось до готового публічного MCP-сервера (Context7, працює без ключа) і
дивимось його очима клієнта через MCP Inspector у CLI-режимі.

Один виклик `make inspect` проганяє кроки 1-3 з 12-крокового flow лекції:

1. Inspector стартує сервер Context7 дочірнім процесом (транспорт stdio).
2. Робить `initialize` - узгодження версій протоколу.
3. Робить `tools/list` - той самий **ListToolsRequest**, що й Claude Code на старті.

У відповіді ти бачиш два інструменти сервера - `resolve-library-id` і
`query-docs` - рівно так, як їх отримує модель: ім'я, опис, схема параметрів.
Це і є MCP-сервер як «упакована інтеграція»: схеми вже написані за тебе.

## Структура

```
8.1-what-is-mcp/
├── README.md            цей файл
├── Makefile             make inspect
└── .mcp.json.example    конфіг Context7 для підключення у Claude Code
```

## Pre-requisites

- Node.js 20+ і `npx` (Inspector і сервер тягнуться через npx, нічого ставити не треба)
- Доступ до мережі (npx підтягує пакети)

API-ключ не потрібен: Context7 - публічний сервер.

## Як запустити

```bash
cd 8.1-what-is-mcp
make inspect      # tools/list публічного Context7: побачиш ListTools і два інструменти
```

Хочеш те саме у живому Claude Code - скопіюй `.mcp.json.example` у корінь свого
проекту як `.mcp.json` і виконай `/mcp` у сесії. Повний розбір підключення -
в уроці 8.3.

## Namespacing

У Claude Code інструменти підключеного сервера видно за конвенцією імен
`mcp__<server>__<tool>` - подвійне підкреслення розділяє префікс, ім'я сервера і
ім'я інструмента. Для Context7 це буде `mcp__context7__resolve-library-id` і
`mcp__context7__query-docs`. Inspector показує «голі» імена (`resolve-library-id`),
бо namespacing додає вже клієнт.

## Source

- Офіційна документація MCP: `https://modelcontextprotocol.io`
- Context7: `https://github.com/upstash/context7`
- MCP Inspector: `https://github.com/modelcontextprotocol/inspector`
