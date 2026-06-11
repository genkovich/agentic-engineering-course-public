# notify-hub: образ для лекції 8.12 (деплой на свій VPS, шпаргалка - DEPLOY.md).
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
# Черга персистить у /app/data - щоб переживала перезапуск контейнера, монтуй volume
RUN mkdir -p data
EXPOSE 3334
CMD ["node", "dist/server.js"]
