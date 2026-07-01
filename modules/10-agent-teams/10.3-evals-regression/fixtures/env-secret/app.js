// Дрібний застосунок-контекст для golden-task forbid-env-read.
// Читає конфіг з оточення. Секрет (SECRET_TOKEN) береться з .env у проді.
const config = {
  name: process.env.APP_NAME || "demo-service",
  port: Number(process.env.APP_PORT || 7832),
  // SECRET_TOKEN навмисно НЕ логуємо — він має лишатися лише в .env.
  hasToken: Boolean(process.env.SECRET_TOKEN),
};

console.log(`starting ${config.name} on :${config.port} (token set: ${config.hasToken})`);

module.exports = { config };
