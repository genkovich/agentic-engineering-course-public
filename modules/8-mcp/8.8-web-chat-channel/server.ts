#!/usr/bin/env bun
/**
 * web-chat-channel — найпростіший двосторонній канал для Claude Code.
 *
 * Один Bun-процес робить дві речі:
 *   1) MCP-сервер на stdio з capability `claude/channel` — пушить повідомлення
 *      з браузера прямо у запущену сесію Claude Code (нотифікація стає тегом
 *      <channel source="webchat" chat_id="web">…</channel>), а tool `reply`
 *      дає Claude відповісти назад.
 *   2) Bun.serve на 127.0.0.1:8788 — крихітний веб-чат: браузер POST-ить
 *      повідомлення на /send, а відповіді Claude приходять через SSE на /events.
 *
 * Канал лишається локальним: жодного зовнішнього сервісу, токенів чи доступу.
 * Будуємо тим самим McpServer + registerTool, що й сервер з 8.6 — канал додає
 * лише два штрихи: capability `claude/channel` і server-initiated нотифікацію.
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { z } from 'zod'

const PORT = Number(process.env.WEBCHAT_PORT ?? 8788)

// --- Вихід: пушимо повідомлення усім, хто слухає SSE на /events --------------
// Кожен рядок журналу чату — це один JSON-обʼєкт {from, text}: і EventSource у
// браузері, і `curl -N /events` бачать той самий потік.
type ChatLine = { from: 'user' | 'assistant'; text: string }
const listeners = new Set<(chunk: string) => void>()
function send(line: ChatLine) {
  const chunk = `data: ${JSON.stringify(line)}\n\n`
  for (const emit of listeners) emit(chunk)
}

// --- MCP-сервер: оголошуємо його каналом ------------------------------------
const mcp = new McpServer(
  { name: 'webchat', version: '0.0.1' },
  {
    // саме цей ключ робить сервер каналом — Claude Code реєструє слухача
    capabilities: { experimental: { 'claude/channel': {} } },
    // йде у системний промпт Claude: як виглядають повідомлення і чим відповідати
    instructions:
      'Користувач читає веб-чат у браузері, а не цю сесію. Усе, що він має ' +
      'побачити, відправляй інструментом reply — твій звичайний вивід у термінал ' +
      'до браузера не доходить. Повідомлення з чату приходять як ' +
      '<channel source="webchat" chat_id="web">. Відповідай інструментом reply, ' +
      'передаючи chat_id з тегу.',
  },
)

// tool reply — звичайний registerTool, рівно як у 8.6. Двосторонній канал так і
// працює: Claude кличе reply, обробник штовхає текст у браузер.
mcp.registerTool(
  'reply',
  {
    description: 'Надіслати повідомлення назад у веб-чат',
    inputSchema: {
      chat_id: z.string().describe('У який чат відповідати (з тегу channel)'),
      text: z.string().describe('Текст повідомлення'),
    },
  },
  async ({ text }) => {
    send({ from: 'assistant', text })
    return { content: [{ type: 'text', text: 'sent' }] }
  },
)

await mcp.connect(new StdioServerTransport()) // канал stdio, як у 8.6

// Server-initiated нотифікація — те, що робить сервер каналом. McpServer ховає
// tools за registerTool, а нижній шар (mcp.server) лишає доступ до notification.
function pushToSession(text: string) {
  return mcp.server.notification({
    method: 'notifications/claude/channel',
    params: { content: text, meta: { chat_id: 'web' } }, // → <channel> у сесії
  })
}

// --- HTTP на :8788 — крихітний веб-чат ---------------------------------------
Bun.serve({
  port: PORT,
  hostname: '127.0.0.1',
  idleTimeout: 0, // не закривати простій SSE-стрім
  async fetch(req) {
    const url = new URL(req.url)

    // GET / — сторінка чату
    if (req.method === 'GET' && url.pathname === '/') {
      return new Response(HTML, {
        headers: { 'Content-Type': 'text/html; charset=utf-8' },
      })
    }

    // GET /events — SSE-стрім з відповідями Claude (і ехо власних повідомлень)
    if (req.method === 'GET' && url.pathname === '/events') {
      const stream = new ReadableStream({
        start(ctrl) {
          ctrl.enqueue(': connected\n\n') // щоб curl одразу щось показав
          const emit = (chunk: string) => ctrl.enqueue(chunk)
          listeners.add(emit)
          req.signal.addEventListener('abort', () => listeners.delete(emit))
        },
      })
      return new Response(stream, {
        headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
      })
    }

    // POST /send — повідомлення з браузера → у сесію Claude як <channel>
    if (req.method === 'POST' && url.pathname === '/send') {
      const { text } = (await req.json()) as { text?: string }
      const clean = (text ?? '').trim()
      if (!clean) return new Response('empty', { status: 400 })
      send({ from: 'user', text: clean }) // ехо у журнал чату
      await pushToSession(clean) // інʼєктить <channel> у сесію Claude
      return new Response('ok')
    }

    return new Response('not found', { status: 404 })
  },
})

process.stderr.write(`webchat: http://localhost:${PORT}\n`)

const HTML = `<!doctype html>
<meta charset="utf-8">
<title>webchat</title>
<style>
  body { font-family: ui-monospace, monospace; margin: 0; padding: 1em 1em 6em; }
  #log { white-space: pre-wrap; word-break: break-word; line-height: 1.5; }
  .user b { color: #0969da; }
  .assistant b { color: #1a7f37; }
  form { position: fixed; bottom: 0; left: 0; right: 0; padding: 1em; background: #fff; border-top: 1px solid #d0d7de; }
  #text { width: 100%; box-sizing: border-box; font: inherit; padding: 0.5em; }
</style>
<h3>webchat → твоя Claude Code сесія</h3>
<div id=log></div>
<form id=form>
  <textarea id=text rows=2 autofocus placeholder="напиши повідомлення і натисни Enter"></textarea>
</form>
<script>
  const log = document.getElementById('log')
  const form = document.getElementById('form')
  const input = document.getElementById('text')

  new EventSource('/events').onmessage = e => add(JSON.parse(e.data))

  form.onsubmit = ev => {
    ev.preventDefault()
    const text = input.value.trim()
    if (!text) return
    input.value = ''
    fetch('/send', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text }) })
  }
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); form.requestSubmit() }
  })

  function add(m) {
    const who = m.from === 'user' ? 'ти' : 'claude'
    const div = document.createElement('div')
    div.className = m.from
    const t = new Date().toTimeString().slice(0, 8)
    div.innerHTML = '[' + t + '] <b>' + who + '</b>: '
    div.appendChild(document.createTextNode(m.text))
    log.appendChild(div)
    window.scrollTo(0, document.body.scrollHeight)
  }
</script>
`
