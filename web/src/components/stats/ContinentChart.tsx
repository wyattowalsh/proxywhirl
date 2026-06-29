import { useMemo } from "react"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { EmptyState } from "@/components/ui/empty-state"
import { Globe } from "lucide-react"
import { CHART_COLORS } from "@/lib/chart-tokens"
import { CONTINENT_COLORS } from "@/types"
import type { Proxy, Stats } from "@/types"

interface ContinentChartProps {
  proxies: Proxy[]
  stats?: Stats | null
}

const CONTINENT_CONFIG: Record<string, { name: string; color: string }> = {
  AS: { name: "Asia", color: CONTINENT_COLORS.AS },
  EU: { name: "Europe", color: CONTINENT_COLORS.EU },
  NA: { name: "North America", color: CONTINENT_COLORS.NA },
  SA: { name: "South America", color: CONTINENT_COLORS.SA },
  AF: { name: "Africa", color: CONTINENT_COLORS.AF },
  OC: { name: "Oceania", color: CONTINENT_COLORS.OC },
  AN: { name: "Antarctica", color: CONTINENT_COLORS.AN },
}

const COUNTRY_TO_CONTINENT: Record<string, string> = {
  DZ: "AF", AO: "AF", BJ: "AF", BW: "AF", BF: "AF", BI: "AF", CM: "AF", CV: "AF",
  CF: "AF", TD: "AF", KM: "AF", CG: "AF", CD: "AF", CI: "AF", DJ: "AF", EG: "AF",
  GQ: "AF", ER: "AF", SZ: "AF", ET: "AF", GA: "AF", GM: "AF", GH: "AF", GN: "AF",
  GW: "AF", KE: "AF", LS: "AF", LR: "AF", LY: "AF", MG: "AF", MW: "AF", ML: "AF",
  MR: "AF", MU: "AF", MA: "AF", MZ: "AF", NA: "AF", NE: "AF", NG: "AF", RW: "AF",
  ST: "AF", SN: "AF", SC: "AF", SL: "AF", SO: "AF", ZA: "AF", SS: "AF", SD: "AF",
  TZ: "AF", TG: "AF", TN: "AF", UG: "AF", ZM: "AF", ZW: "AF", RE: "AF", YT: "AF",
  AF: "AS", AM: "AS", AZ: "AS", BH: "AS", BD: "AS", BT: "AS", BN: "AS", KH: "AS",
  CN: "AS", CY: "AS", GE: "AS", HK: "AS", IN: "AS", ID: "AS", IR: "AS", IQ: "AS",
  IL: "AS", JP: "AS", JO: "AS", KZ: "AS", KW: "AS", KG: "AS", LA: "AS", LB: "AS",
  MO: "AS", MY: "AS", MV: "AS", MN: "AS", MM: "AS", NP: "AS", KP: "AS", OM: "AS",
  PK: "AS", PS: "AS", PH: "AS", QA: "AS", SA: "AS", SG: "AS", KR: "AS", LK: "AS",
  SY: "AS", TW: "AS", TJ: "AS", TH: "AS", TL: "AS", TR: "AS", TM: "AS", AE: "AS",
  UZ: "AS", VN: "AS", YE: "AS",
  AL: "EU", AD: "EU", AT: "EU", BY: "EU", BE: "EU", BA: "EU", BG: "EU", HR: "EU",
  CZ: "EU", DK: "EU", EE: "EU", FI: "EU", FR: "EU", DE: "EU", GR: "EU", HU: "EU",
  IS: "EU", IE: "EU", IT: "EU", XK: "EU", LV: "EU", LI: "EU", LT: "EU", LU: "EU",
  MT: "EU", MD: "EU", MC: "EU", ME: "EU", NL: "EU", MK: "EU", NO: "EU", PL: "EU",
  PT: "EU", RO: "EU", RU: "EU", SM: "EU", RS: "EU", SK: "EU", SI: "EU", ES: "EU",
  SE: "EU", CH: "EU", UA: "EU", GB: "EU", VA: "EU", FO: "EU", GI: "EU", GG: "EU",
  IM: "EU", JE: "EU",
  AG: "NA", BS: "NA", BB: "NA", BZ: "NA", CA: "NA", CR: "NA", CU: "NA", DM: "NA",
  DO: "NA", SV: "NA", GD: "NA", GT: "NA", HT: "NA", HN: "NA", JM: "NA", MX: "NA",
  NI: "NA", PA: "NA", KN: "NA", LC: "NA", VC: "NA", TT: "NA", US: "NA", AW: "NA",
  BM: "NA", KY: "NA", CW: "NA", GL: "NA", GP: "NA", MQ: "NA", MS: "NA", PR: "NA",
  SX: "NA", TC: "NA", VG: "NA", VI: "NA",
  AR: "SA", BO: "SA", BR: "SA", CL: "SA", CO: "SA", EC: "SA", FK: "SA", GF: "SA",
  GY: "SA", PY: "SA", PE: "SA", SR: "SA", UY: "SA", VE: "SA",
  AU: "OC", FJ: "OC", KI: "OC", MH: "OC", FM: "OC", NR: "OC", NZ: "OC", PW: "OC",
  PG: "OC", WS: "OC", SB: "OC", TO: "OC", TV: "OC", VU: "OC", NC: "OC", PF: "OC",
  GU: "OC", AS: "OC", CK: "OC", NU: "OC", TK: "OC", WF: "OC",
  AQ: "AN",
}

export function ContinentChart({ proxies, stats }: ContinentChartProps) {
  const data = useMemo(() => {
    const precomputed = stats?.aggregations?.by_continent
    if (precomputed && Object.keys(precomputed).length > 0) {
      return Object.entries(precomputed)
        .map(([code, count]) => ({
          code,
          name: CONTINENT_CONFIG[code]?.name || code,
          value: count,
          color: CONTINENT_CONFIG[code]?.color || CHART_COLORS.muted,
        }))
        .sort((a, b) => b.value - a.value)
    }

    const counts: Record<string, number> = {}
    proxies.forEach((proxy) => {
      const continentCode =
        proxy.continent_code ||
        (proxy.country_code ? COUNTRY_TO_CONTINENT[proxy.country_code] : undefined)
      if (continentCode) {
        counts[continentCode] = (counts[continentCode] || 0) + 1
      }
    })

    return Object.entries(counts)
      .map(([code, count]) => ({
        code,
        name: CONTINENT_CONFIG[code]?.name || code,
        value: count,
        color: CONTINENT_CONFIG[code]?.color || CHART_COLORS.muted,
      }))
      .sort((a, b) => b.value - a.value)
  }, [proxies, stats])

  const total = data.reduce((sum, d) => sum + d.value, 0)

  if (total === 0) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle>Continents</CardTitle>
        </CardHeader>
        <CardContent>
          <EmptyState
            icon={Globe}
            title="No geographic data available"
            description="Location data not available for proxies"
            className="h-[180px]"
          />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle id="continent-chart-title">Continents</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          role="img"
          aria-labelledby="continent-chart-title"
          className="flex flex-col sm:flex-row items-center gap-4"
        >
          <div className="h-[180px] w-[180px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                  isAnimationActive={false}
                >
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number, _name, props) => [
                    `${value.toLocaleString()} (${((value / total) * 100).toFixed(1)}%)`,
                    props.payload.name,
                  ]}
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "var(--radius)",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1 w-full space-y-2">
            {data.slice(0, 5).map((item) => (
              <div key={item.code} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                    aria-hidden="true"
                  />
                  <span>{item.code} {item.name}</span>
                </div>
                <span className="font-medium tabular-nums">
                  {((item.value / total) * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
          <table className="sr-only">
            <caption>Continent distribution</caption>
            <thead>
              <tr>
                <th scope="col">Continent</th>
                <th scope="col">Proxies</th>
                <th scope="col">Share</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item) => (
                <tr key={item.code}>
                  <td>{item.name}</td>
                  <td>{item.value.toLocaleString()}</td>
                  <td>{((item.value / total) * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}