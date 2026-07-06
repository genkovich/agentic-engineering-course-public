# DEPLOY.md · task-store на власному VPS

Покрокова шпаргалка до лекції 8.12: від локального коду до `✔ Connected` з публічного URL. Деплоїмо HTTP-варіант task-store (`make run-http`, `src/server-http.ts`) - одну спільну інстанцію, до якої ходять агенти всієї команди і CI-машини замість локальної копії в кожного.

Знадобиться: VPS з встановленим Docker (підійде будь-який - Hetzner, DigitalOcean, OVH тощо), SSH-доступ до нього і, опційно для TLS, домен, A-запис якого дивиться на VPS.

## 0. Локальна готовність

Спершу перевіряємо все локально - у проді дебажити дорожче:

```bash
make test                                    # всі тести зелені
docker build -t task-store .
docker run --rm -p 3335:3335 task-store      # або: docker compose up --build
curl localhost:3335/healthz                  # → {"ok":true,"tasks":0}
```

## 1. Доставка образу на VPS

**Варіант А - через registry** (GHCR; потрібен `docker login ghcr.io`):

```bash
docker tag task-store ghcr.io/<нік>/task-store:latest
docker push ghcr.io/<нік>/task-store:latest
ssh user@vps "docker pull ghcr.io/<нік>/task-store:latest"
```

**Варіант Б - без registry** (образ їде напряму по SSH):

```bash
docker save task-store | gzip | ssh user@vps "gunzip | docker load"
```

## 2. Конфіг і запуск на VPS

```bash
ssh user@vps
docker run -d --name task-store \
  --restart unless-stopped \
  -p 3335:3335 \
  -v task-data:/app/data \
  task-store
```

`-v task-data:/app/data` - задачі (`data/tasks.json`) переживають перезапуск контейнера. Транспорт у task-store stateless, а дані - ні: саме тому потрібен volume.

## 3. Перевірка з зовнішнього світу

```bash
curl http://<vps-host>:3335/healthz    # → {"ok":true,"tasks":0}
```

## 4. (Опційно) Caddy: реверс-проксі з авто-TLS

Якщо є домен, Caddy сам отримує і оновлює сертифікат Let's Encrypt. Весь конфіг (`/etc/caddy/Caddyfile`) - два рядки:

```
mcp.example.com {
    reverse_proxy localhost:3335
}
```

```bash
sudo apt install caddy && sudo systemctl reload caddy
curl https://mcp.example.com/healthz    # TLS вже працює
```

## 5. Підключення Claude Code

```bash
claude mcp add --transport http task-store https://mcp.example.com/mcp
claude mcp list    # → task-store ... ✔ Connected
```

Без домена: `claude mcp add --transport http task-store http://<vps-host>:3335/mcp`.

## 6. Перший живий вхід замість make seed

`make seed` кладе кілька демо-задач локально перед збіркою образу. На задеплоєному сервері перша жива задача приходить уже через MCP - тим самим каналом, яким її потім читають агенти:

- з Claude Code: «додай задачу підготувати реліз з high пріоритетом» викличе `add_task`;
- або через MCP Inspector проти публічного URL:

```bash
npx @modelcontextprotocol/inspector --cli \
  --transport http --server-url https://mcp.example.com/mcp \
  --method tools/call --tool-name add_task \
  --tool-arg title="перша жива задача" --tool-arg priority=high
```

Після цього `curl https://mcp.example.com/healthz` покаже `{"ok":true,"tasks":1}`, а `list_tasks` поверне задачу будь-якому підключеному агенту.
