import { Globe, Shield, Zap, Server } from "lucide-react"
import { StatsCard } from "./StatsCard"
import { formatNumber } from "@/lib/utils"
import type { Stats } from "@/types"
import { PROTOCOL_COLORS } from "@/types"

interface StatsGridProps {
  stats: Stats
}

export function StatsGrid({ stats }: StatsGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        title="Total Proxies"
        value={formatNumber(stats.proxies.total)}
        description={`From ${stats.sources.total} sources`}
        icon={Server}
      />
      <StatsCard
        title="HTTP Proxies"
        value={formatNumber(stats.proxies.by_protocol.http)}
        icon={Globe}
        color={PROTOCOL_COLORS.http}
      />
      <StatsCard
        title="SOCKS4 Proxies"
        value={formatNumber(stats.proxies.by_protocol.socks4)}
        icon={Shield}
        color={PROTOCOL_COLORS.socks4}
      />
      <StatsCard
        title="SOCKS5 Proxies"
        value={formatNumber(stats.proxies.by_protocol.socks5)}
        icon={Zap}
        color={PROTOCOL_COLORS.socks5}
      />
    </div>
  )
}
