# DEPLOY.md · notify-hub на власному VPS

Покрокова шпаргалка до лекції 8.12: від локального коду до `✔ Connected` з публічного URL.

Знадобиться: VPS з встановленим Docker (підійде будь-який - Hetzner, DigitalOcean, OVH тощо), SSH-доступ до нього і, опційно для TLS, домен, A-запис якого дивиться на VPS.

## 0. Локальна готовність

Спершу перевіряємо все локально - у проді дебажити дорожче:

```bash
make test                                  # всі тести зелені
docker build -t notify-hub .
docker run --rm -p 3334:3334 notify-hub    # або: docker compose up --build
curl localhost:3334/healthz                # → {"ok":true,...}
```

## 1. Доставка образу на VPS

**Варіант А - через registry** (GHCR; потрібен `docker login ghcr.io`):

```bash
docker tag notify-hub ghcr.io/<нік>/notify-hub:latest
docker push ghcr.io/<нік>/notify-hub:latest
ssh user@vps "docker pull ghcr.io/<нік>/notify-hub:latest"
```

**Варіант Б - без registry** (образ їде напряму по SSH):

```bash
docker save notify-hub | gzip | ssh user@vps "gunzip | docker load"
```

## 2. Конфіг і запуск на VPS

```bash
scp .env user@vps:~/notify-hub.env    # WEBHOOK_SECRET, опційно TELEGRAM_*
ssh user@vps
docker run -d --name notify-hub \
  --restart unless-stopped \
  -p 3334:3334 \
  --env-file ~/notify-hub.env \
  -v notify-data:/app/data \
  notify-hub
```

`-v notify-data:/app/data` - черга подій переживає перезапуск контейнера.

## 3. Перевірка з зовнішнього світу

```bash
curl http://<vps-host>:3334/healthz    # → {"ok":true,...}
```

## 4. (Опційно) Caddy: реверс-проксі з авто-TLS

Якщо є домен, Caddy сам отримує і оновлює сертифікат Let's Encrypt. Весь конфіг (`/etc/caddy/Caddyfile`) - два рядки:

```
mcp.example.com {
    reverse_proxy localhost:3334
}
```

```bash
sudo apt install caddy && sudo systemctl reload caddy
curl https://mcp.example.com/healthz    # TLS вже працює
```

## 5. Підключення Claude Code

```bash
claude mcp add --transport http notify-hub https://mcp.example.com/mcp
claude mcp list    # → notify-hub ... ✔ Connected
```

Без домена: `claude mcp add --transport http notify-hub http://<vps-host>:3334/mcp`.

## 6. (Опційно) Живі webhooks замість make seed

GitHub: репозиторій → Settings → Webhooks → Add webhook:

- Payload URL: `https://mcp.example.com/webhook`
- Content type: `application/json`
- Secret: те саме значення, що у `WEBHOOK_SECRET` на VPS

Після першого PR або падіння CI подія сама ляже у чергу - далі її розбирає агент через `/mcp`.
