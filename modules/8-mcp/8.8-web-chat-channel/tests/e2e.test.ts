/**
 * E2E-тест контракту каналу — без живої Claude-сесії.
 *
 * Піднімаємо server.ts як subprocess, підключаємося MCP-клієнтом по stdio
 * (рівно те, що робить Claude Code), і перевіряємо весь контракт:
 *   1) listTools бачить tool `reply`;
 *   2) POST /send ехом кладе повідомлення користувача у SSE-стрім /events;
 *   3) виклик tool `reply` пушить відповідь Claude у той самий SSE-стрім.
 *
 * Живу інʼєкцію тегу <channel> у сесію перевіряє скринкаст, не цей тест.
 */
import { test, expect, beforeAll, afterAll } from 'bun:test'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'

const PORT = 8799
const BASE = `http://127.0.0.1:${PORT}`
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')

const transport = new StdioClientTransport({
  command: 'bun',
  args: ['server.ts'],
  cwd: ROOT,
  env: { ...process.env, WEBCHAT_PORT: String(PORT) },
})
const client = new Client({ name: 'e2e', version: '0.0.0' }, { capabilities: {} })

// Журнал усіх SSE-рядків, що прилетіли на /events.
const seen: { from: string; text: string }[] = []
let sse: AbortController

beforeAll(async () => {
  await client.connect(transport)
  await waitForHttp()
  sse = openSse()
  // дати стріму під'єднатися до того, як почнемо слати
  await delay(200)
})

afterAll(async () => {
  sse?.abort()
  await client.close()
})

test('listTools віддає tool reply', async () => {
  const { tools } = await client.listTools()
  expect(tools.map(t => t.name)).toContain('reply')
})

test('POST /send ехом кладе повідомлення користувача у SSE', async () => {
  const text = 'що в цьому репо?'
  const res = await fetch(`${BASE}/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
  expect(res.ok).toBe(true)
  await waitFor(l => l.from === 'user' && l.text === text)
})

test('виклик tool reply пушить відповідь у SSE', async () => {
  const text = 'тут лежить демо каналу web-chat-channel'
  await client.callTool({ name: 'reply', arguments: { chat_id: 'web', text } })
  await waitFor(l => l.from === 'assistant' && l.text === text)
})

// --- helpers -----------------------------------------------------------------
function delay(ms: number) {
  return new Promise(r => setTimeout(r, ms))
}

async function waitForHttp() {
  for (let i = 0; i < 100; i++) {
    try {
      const r = await fetch(`${BASE}/`)
      if (r.ok) return
    } catch {}
    await delay(100)
  }
  throw new Error('HTTP-сервер не піднявся')
}

function openSse() {
  const ctrl = new AbortController()
  ;(async () => {
    const res = await fetch(`${BASE}/events`, { signal: ctrl.signal })
    const reader = res.body!.getReader()
    const dec = new TextDecoder()
    let buf = ''
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buf += dec.decode(value, { stream: true })
      let idx: number
      while ((idx = buf.indexOf('\n\n')) >= 0) {
        const block = buf.slice(0, idx)
        buf = buf.slice(idx + 2)
        for (const line of block.split('\n')) {
          if (line.startsWith('data: ')) {
            try {
              seen.push(JSON.parse(line.slice(6)))
            } catch {}
          }
        }
      }
    }
  })().catch(() => {})
  return ctrl
}

async function waitFor(pred: (l: { from: string; text: string }) => boolean) {
  for (let i = 0; i < 50; i++) {
    if (seen.some(pred)) return
    await delay(100)
  }
  throw new Error(`SSE не отримав очікуване повідомлення; маємо: ${JSON.stringify(seen)}`)
}
