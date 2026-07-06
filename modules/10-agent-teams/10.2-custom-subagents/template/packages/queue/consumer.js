// Споживач черги в стилі RabbitMQ: експоненційний backoff + dead-letter.
// Обробляє повідомлення; при невдачі збільшує лічильник спроб і повертає його
// в чергу, а коли спроби вичерпано — відправляє в dead-letter.

const MAX_RETRIES = 3;
const BASE_DELAY_MS = 100;

function backoffDelay(attempt) {
  return BASE_DELAY_MS * 2 ** attempt; // 100, 200, 400, ...
}

// queues: { main: [], deadLetter: [] }. handle(message) кидає помилку при невдачі.
function processOnce(message, queues, handle) {
  try {
    handle(message);
    return { action: "ack" };
  } catch (err) {
    message.attempts = (message.attempts || 0) + 1;

    if (message.attempts >= MAX_RETRIES) {
      queues.deadLetter.push(message);
    }

    // BUG(queue): requeue безумовний. На межі attempts === MAX_RETRIES
    // повідомлення потрапляє І в deadLetter, І назад у main — тобто обробиться
    // ще раз (дубль). Коректно — повертати в чергу ЛИШЕ поки спроби не
    // вичерпані (else-гілка). Happy-path тести цього не ловлять — саме на цьому
    // reasoning-базі порівнюємо haiku проти opus у сценарії (c).
    queues.main.push(message);

    return { action: "requeue", delayMs: backoffDelay(message.attempts) };
  }
}

module.exports = { processOnce, backoffDelay, MAX_RETRIES, BASE_DELAY_MS };
