import * as React from "react"
import { RotateCw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

type ServiceStatus = "online" | "down" | "updating"

type Service = {
  id: string
  name: string
  port: number
  status: ServiceStatus
  uptime: number
  latencyMs: number | null
}

const HOSTNAME = "homelab-01"
const OS_LABEL = "Ubuntu 24.04 LTS"
const BOOT_UPTIME = "47д"

const INITIAL_SERVICES: Service[] = [
  {
    id: "nextcloud",
    name: "nextcloud",
    port: 8443,
    status: "down",
    uptime: 0,
    latencyMs: null,
  },
  {
    id: "qbittorrent",
    name: "qbittorrent",
    port: 8080,
    status: "updating",
    uptime: 0,
    latencyMs: null,
  },
  {
    id: "home-assistant",
    name: "home-assistant",
    port: 8123,
    status: "online",
    uptime: 14 * 86400 + 6 * 3600 + 32 * 60 + 41,
    latencyMs: 31,
  },
  {
    id: "jellyfin",
    name: "jellyfin",
    port: 8096,
    status: "online",
    uptime: 6 * 86400 + 18 * 3600 + 4 * 60 + 12,
    latencyMs: 24,
  },
  {
    id: "pi-hole",
    name: "pi-hole",
    port: 53,
    status: "online",
    uptime: 32 * 86400 + 11 * 3600 + 47 * 60 + 3,
    latencyMs: 8,
  },
  {
    id: "wireguard",
    name: "wireguard",
    port: 51820,
    status: "online",
    uptime: 32 * 86400 + 11 * 3600 + 46 * 60 + 58,
    latencyMs: 45,
  },
  {
    id: "gitea",
    name: "gitea",
    port: 3000,
    status: "online",
    uptime: 2 * 86400 + 3 * 3600 + 15 * 60 + 27,
    latencyMs: 56,
  },
  {
    id: "postgresql",
    name: "postgresql",
    port: 5432,
    status: "online",
    uptime: 41 * 86400 + 2 * 3600 + 8 * 60 + 19,
    latencyMs: 4,
  },
]

type Metric = {
  id: string
  label: string
  value: string
  detail: string
  percent: number
}

const METRICS: Metric[] = [
  { id: "cpu", label: "cpu", value: "23%", detail: "8 ядер · ryzen 5", percent: 23 },
  { id: "ram", label: "ram", value: "19.8 / 32 ГБ", detail: "62%", percent: 62 },
  { id: "disk", label: "диск", value: "5.7 / 8 ТБ", detail: "71%", percent: 71 },
  { id: "temp", label: "темп", value: "46°C", detail: "cpu-сенсор", percent: 46 },
]

const NETWORK = {
  downMbit: 18.4,
  upMbit: 3.2,
  localIp: "192.168.1.10",
  wireguardIp: "10.8.0.1",
  dnsPerDay: "48 217",
  blockedShare: "12.4%",
}

// Вхідний трафік за останню годину, Мбіт/с, крок 2.5 хв
const TRAFFIC_HISTORY = [
  6.2, 7.8, 5.4, 9.1, 12.3, 8.7, 14.2, 11.6, 9.8, 16.4, 13.1, 18.9, 15.2, 12.7,
  19.6, 22.3, 17.8, 14.5, 20.1, 24.6, 21.2, 18.4, 16.9, 18.4,
]

// Останні 30 днів: чи був інцидент хоча б з одним сервісом
const UPTIME_HISTORY: ("ok" | "incident")[] = [
  "ok", "ok", "ok", "ok", "ok", "ok", "ok", "ok", "ok", "ok",
  "ok", "incident", "ok", "ok", "ok", "ok", "ok", "ok", "ok", "ok",
  "ok", "ok", "ok", "ok", "ok", "ok", "ok", "ok", "ok", "incident",
]

const STATUS_META: Record<
  ServiceStatus,
  { label: string; dot: string; text: string }
> = {
  online: { label: "працює", dot: "bg-chart-1", text: "text-chart-1" },
  down: {
    label: "впав",
    dot: "bg-destructive",
    text: "rounded-sm bg-destructive px-1.5 py-0.5 text-destructive-foreground",
  },
  updating: {
    label: "оновлюється",
    dot: "bg-muted-foreground",
    text: "text-muted-foreground",
  },
}

const RESTART_DURATION_MS = 4000

function formatUptime(total: number) {
  const days = Math.floor(total / 86400)
  const hours = String(Math.floor((total % 86400) / 3600)).padStart(2, "0")
  const minutes = String(Math.floor((total % 3600) / 60)).padStart(2, "0")
  const seconds = String(total % 60).padStart(2, "0")
  const clock = `${hours}:${minutes}:${seconds}`

  return days > 0 ? `${days}д ${clock}` : clock
}

function meterTone(percent: number) {
  if (percent >= 85) return "bg-destructive"
  if (percent >= 70) return "bg-chart-4"
  return "bg-chart-1"
}

function MeterBar({ percent }: { percent: number }) {
  return (
    <div className="h-1 w-full overflow-hidden rounded-full bg-muted">
      <div
        className={cn("h-full rounded-full", meterTone(percent))}
        style={{ width: `${percent}%` }}
      />
    </div>
  )
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <span className="font-mono text-xs tracking-widest text-muted-foreground uppercase">
      {children}
    </span>
  )
}

function MetricTile({ metric, index }: { metric: Metric; index: number }) {
  return (
    <Card
      className="animate-card-enter gap-2 py-4"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <CardContent className="flex flex-col gap-2">
        <SectionLabel>{metric.label}</SectionLabel>
        <div className="flex items-baseline justify-between gap-2">
          <span className="font-mono text-xl font-medium whitespace-nowrap text-card-foreground tabular-nums lg:text-2xl">
            {metric.value}
          </span>
          <span className="font-mono text-xs whitespace-nowrap text-muted-foreground tabular-nums">
            {metric.detail}
          </span>
        </div>
        <MeterBar percent={metric.percent} />
      </CardContent>
    </Card>
  )
}

function ServiceRow({
  service,
  onRestart,
}: {
  service: Service
  onRestart: (id: string) => void
}) {
  const meta = STATUS_META[service.status]

  return (
    <li className="flex items-center gap-3 px-4 py-3 font-mono sm:gap-4">
      <span
        aria-hidden
        className={cn("size-2 shrink-0 rounded-full", meta.dot)}
      />
      <div className="flex min-w-0 flex-1 flex-col gap-0.5 sm:grid sm:grid-cols-[minmax(0,1.4fr)_6.5rem_minmax(0,1fr)_5.5rem] sm:items-baseline sm:gap-x-4">
        <span className="truncate text-sm font-medium text-card-foreground">
          {service.name}
          <span className="ml-1.5 font-normal text-muted-foreground">
            :{service.port}
          </span>
        </span>
        <div className="flex flex-wrap items-baseline gap-x-3 gap-y-0.5 sm:contents">
          <span className={cn("text-xs tracking-widest uppercase", meta.text)}>
            {meta.label}
          </span>
          <span className="text-xs text-muted-foreground tabular-nums">
            {service.status === "down"
              ? "uptime —"
              : `uptime ${formatUptime(service.uptime)}`}
          </span>
          <span className="text-xs text-muted-foreground tabular-nums sm:text-right">
            {service.latencyMs === null ? "ping —" : `ping ${service.latencyMs} мс`}
          </span>
        </div>
      </div>
      <Button
        variant={service.status === "down" ? "outline" : "ghost"}
        size="sm"
        disabled={service.status === "updating"}
        onClick={() => onRestart(service.id)}
        className="shrink-0"
        aria-label={`Перезапустити ${service.name}`}
      >
        <RotateCw
          data-icon="inline-start"
          className={cn(service.status === "updating" && "animate-spin")}
        />
        <span className="hidden sm:inline">Рестарт</span>
      </Button>
    </li>
  )
}

function ServicesPanel({
  services,
  onRestart,
}: {
  services: Service[]
  onRestart: (id: string) => void
}) {
  return (
    <Card
      className="animate-card-enter h-full gap-0 py-0"
      style={{ animationDelay: "200ms" }}
    >
      <div className="flex items-baseline justify-between border-b border-border px-4 py-3">
        <SectionLabel>сервіси</SectionLabel>
        <span className="font-mono text-xs text-muted-foreground">
          docker compose · {services.length}
        </span>
      </div>
      <ul className="divide-y divide-border">
        {services.map((service) => (
          <ServiceRow
            key={service.id}
            service={service}
            onRestart={onRestart}
          />
        ))}
      </ul>
    </Card>
  )
}

function TrafficSparkline() {
  const max = Math.max(...TRAFFIC_HISTORY)
  const points = TRAFFIC_HISTORY.map((value, index) => {
    const x = (index / (TRAFFIC_HISTORY.length - 1)) * 120
    const y = 30 - (value / max) * 26
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(" ")
  const [lastX, lastY] = points.split(" ").at(-1)!.split(",")

  return (
    <svg
      viewBox="0 0 120 32"
      className="h-12 w-full text-chart-1"
      preserveAspectRatio="none"
      role="img"
      aria-label="Вхідний трафік за останню годину"
    >
      <polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        vectorEffect="non-scaling-stroke"
      />
      <circle cx={lastX} cy={lastY} r="2" fill="currentColor" />
    </svg>
  )
}

function UptimeStrip() {
  return (
    <div className="flex h-6 items-stretch gap-px">
      {UPTIME_HISTORY.map((day, index) => (
        <span
          key={index}
          className={cn(
            "min-w-0 flex-1 rounded-[1px]",
            day === "ok" ? "bg-chart-1/60" : "bg-destructive"
          )}
        />
      ))}
    </div>
  )
}

function NetworkPanel() {
  return (
    <Card
      className="animate-card-enter h-full gap-0 py-0"
      style={{ animationDelay: "280ms" }}
    >
      <div className="border-b border-border px-4 py-3">
        <SectionLabel>мережа</SectionLabel>
      </div>
      <CardContent className="flex flex-1 flex-col gap-5 px-4 py-4 font-mono">
        <div className="flex flex-col gap-1.5">
          <div className="flex items-baseline justify-between text-xs">
            <span className="text-muted-foreground">вхідний</span>
            <span className="text-sm text-card-foreground tabular-nums">
              {NETWORK.downMbit.toFixed(1)} Мбіт/с
            </span>
          </div>
          <MeterBar percent={NETWORK.downMbit} />
        </div>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-baseline justify-between text-xs">
            <span className="text-muted-foreground">вихідний</span>
            <span className="text-sm text-card-foreground tabular-nums">
              {NETWORK.upMbit.toFixed(1)} Мбіт/с
            </span>
          </div>
          <MeterBar percent={(NETWORK.upMbit / 40) * 100} />
        </div>
        <div className="flex flex-col gap-1.5">
          <span className="text-xs text-muted-foreground">
            трафік · остання година
          </span>
          <TrafficSparkline />
        </div>
        <div className="flex flex-col gap-1.5">
          <div className="flex items-baseline justify-between text-xs">
            <span className="text-muted-foreground">аптайм · 30 днів</span>
            <span className="text-card-foreground tabular-nums">99.4%</span>
          </div>
          <UptimeStrip />
        </div>
        <dl className="mt-auto grid grid-cols-2 gap-x-3 gap-y-4 border-t border-border pt-4 text-xs">
          <div className="flex flex-col gap-0.5">
            <dt className="text-muted-foreground">локальна ip</dt>
            <dd className="text-card-foreground tabular-nums">
              {NETWORK.localIp}
            </dd>
          </div>
          <div className="flex flex-col gap-0.5">
            <dt className="text-muted-foreground">wireguard</dt>
            <dd className="text-card-foreground tabular-nums">
              {NETWORK.wireguardIp}
            </dd>
          </div>
          <div className="flex flex-col gap-0.5">
            <dt className="text-muted-foreground">dns / добу</dt>
            <dd className="text-card-foreground tabular-nums">
              {NETWORK.dnsPerDay}
            </dd>
          </div>
          <div className="flex flex-col gap-0.5">
            <dt className="text-muted-foreground">заблоковано</dt>
            <dd className="text-card-foreground tabular-nums">
              {NETWORK.blockedShare}
            </dd>
          </div>
        </dl>
      </CardContent>
    </Card>
  )
}

export function App() {
  const [services, setServices] = React.useState(INITIAL_SERVICES)

  React.useEffect(() => {
    const timer = window.setInterval(() => {
      setServices((prev) =>
        prev.map((service) =>
          service.status === "online"
            ? { ...service, uptime: service.uptime + 1 }
            : service
        )
      )
    }, 1000)

    return () => window.clearInterval(timer)
  }, [])

  const restart = React.useCallback((id: string) => {
    setServices((prev) =>
      prev.map((service) =>
        service.id === id
          ? { ...service, status: "updating" as const, uptime: 0 }
          : service
      )
    )

    window.setTimeout(() => {
      setServices((prev) =>
        prev.map((service) =>
          service.id === id
            ? { ...service, status: "online" as const, uptime: 0 }
            : service
        )
      )
    }, RESTART_DURATION_MS)
  }, [])

  const onlineCount = services.filter((s) => s.status === "online").length
  const downCount = services.filter((s) => s.status === "down").length

  return (
    <div className="flex min-h-svh justify-center px-4 py-8 lg:px-8">
      <main className="flex w-full max-w-[1360px] flex-col gap-5">
        <header className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div className="flex flex-col gap-1">
            <SectionLabel>home-srv / монітор</SectionLabel>
            <h1 className="font-heading text-3xl font-semibold tracking-tight text-foreground">
              Статус сервера
            </h1>
            <p className="font-mono text-sm tabular-nums">
              <span className="text-chart-1">
                {onlineCount}/{services.length} у мережі
              </span>
              {downCount > 0 && (
                <span className="ml-2 rounded-sm bg-destructive px-1.5 py-0.5 text-xs text-destructive-foreground">
                  {downCount} {downCount === 1 ? "впав" : "впали"}
                </span>
              )}
            </p>
          </div>
          <div className="flex flex-col gap-0.5 font-mono text-xs text-muted-foreground tabular-nums lg:text-right">
            <span className="text-sm text-foreground">{HOSTNAME}</span>
            <span>{OS_LABEL}</span>
            <span>аптайм {BOOT_UPTIME}</span>
          </div>
        </header>
        <section
          aria-label="Метрики сервера"
          className="grid grid-cols-2 gap-4 lg:grid-cols-4"
        >
          {METRICS.map((metric, index) => (
            <MetricTile key={metric.id} metric={metric} index={index} />
          ))}
        </section>
        <div className="grid items-stretch gap-4 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
          <section aria-label="Сервіси">
            <ServicesPanel services={services} onRestart={restart} />
          </section>
          <section aria-label="Мережа">
            <NetworkPanel />
          </section>
        </div>
        <footer className="flex items-center justify-between font-mono text-xs text-muted-foreground tabular-nums">
          <span>опитування кожні 5с</span>
          <span>
            {onlineCount === services.length
              ? "усі сервіси в мережі"
              : `${services.length - onlineCount} потребують уваги`}
          </span>
        </footer>
      </main>
    </div>
  )
}

export default App
