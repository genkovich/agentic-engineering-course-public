# task-store: образ для лекції 8.12 (деплой на свій VPS, шпаргалка - DEPLOY.md).
# Деплоїмо HTTP-варіант сервера (src/server-http.ts → dist/server-http.js):
# саме він слухає порт і віддає /mcp та /healthz. stdio-сервер тут не потрібен.
# Дві стадії: build з повними devDependencies для tsc,
# runtime тільки з прод-залежностями і dist/.

FROM node:22-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

FROM node:22-slim
ENV NODE_ENV=production
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist
# Задачі персистять у /app/data (data/tasks.json) - щоб переживали перезапуск
# контейнера, монтуй volume. Транспорт stateless, дані - ні (лекція 8.12).
RUN mkdir -p data
EXPOSE 3335
CMD ["node", "dist/server-http.js"]
