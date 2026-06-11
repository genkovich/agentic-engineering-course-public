// Відправка повідомлень у Telegram через Bot API.
// Якщо TELEGRAM_BOT_TOKEN або TELEGRAM_CHAT_ID не задані, працює dry-run:
// повідомлення йде у лог і у data/sent.json, у Telegram нічого не летить.
// Це дозволяє пройти повний demo-flow без реального токена.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";

export interface TelegramConfig {
  botToken?: string;
  chatId?: string;
  // Файл, куди пишемо журнал відправлених повідомлень (і dry-run, і реальних)
  sentFile: string;
}

export interface SendResult {
  ok: boolean;
  dryRun: boolean;
  error?: string;
}

interface SentRecord {
  text: string;
  sentAt: string;
  dryRun: boolean;
}

function appendSent(file: string, record: SentRecord): void {
  let records: SentRecord[] = [];
  if (existsSync(file)) {
    try {
      const parsed = JSON.parse(readFileSync(file, "utf8"));
      if (Array.isArray(parsed)) records = parsed;
    } catch {
      // битий файл перезапишемо з нуля
    }
  }
  records.push(record);
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, JSON.stringify(records, null, 2) + "\n", "utf8");
}

export async function sendTelegram(config: TelegramConfig, text: string): Promise<SendResult> {
  if (!config.botToken || !config.chatId) {
    console.log(`[telegram] dry-run (no token/chat_id): ${text}`);
    appendSent(config.sentFile, { text, sentAt: new Date().toISOString(), dryRun: true });
    return { ok: true, dryRun: true };
  }

  try {
    const response = await fetch(`https://api.telegram.org/bot${config.botToken}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: config.chatId, text }),
    });
    const body: any = await response.json();
    if (!response.ok || body?.ok !== true) {
      const error = body?.description ?? `HTTP ${response.status}`;
      console.error(`[telegram] send failed: ${error}`);
      return { ok: false, dryRun: false, error };
    }
    appendSent(config.sentFile, { text, sentAt: new Date().toISOString(), dryRun: false });
    return { ok: true, dryRun: false };
  } catch (err) {
    const error = err instanceof Error ? err.message : String(err);
    console.error(`[telegram] send failed: ${error}`);
    return { ok: false, dryRun: false, error };
  }
}
