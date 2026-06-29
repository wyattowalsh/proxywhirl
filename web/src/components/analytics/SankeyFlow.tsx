import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { CHART_COLORS, getSeriesColor } from "@/lib/chart-tokens"
import { PROTOCOL_COLORS } from "@/types"
import type { SourceFlowEntry } from "@/types"

interface SankeyFlowProps {
  sourceFlow: SourceFlowEntry[]
}

interface FlowData {
  sources: Array<{ name: string; count: number; color: string }>
  protocols: Array<{ name: string; count: number; color: string }>
  countries: Array<{ code: string; name: string; count: number }>
  flows: Array<{ source: string; protocol: string; country: string; count: number }>
}

export function SankeyFlow({ sourceFlow }: SankeyFlowProps) {
  const data = useMemo((): FlowData => {
    if (!sourceFlow || sourceFlow.length === 0) {
      return { sources: [], protocols: [], countries: [], flows: [] }
    }

    const sourceCounts: Record<string, number> = {}
    const protocolCounts: Record<string, number> = {}
    const countryCounts: Record<string, number> = {}

    sourceFlow.forEach((f) => {
      sourceCounts[f.source] = (sourceCounts[f.source] || 0) + f.count
      protocolCounts[f.protocol] = (protocolCounts[f.protocol] || 0) + f.count
      countryCounts[f.country] = (countryCounts[f.country] || 0) + f.count
    })

    const sources = Object.entries(sourceCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([name, count], i) => ({
        name: name.length > 15 ? name.slice(0, 13) + "…" : name,
        count,
        color: getSeriesColor(i),
      }))

    const protocols = Object.entries(protocolCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([name, count]) => ({
        name: name.toUpperCase(),
        count,
        color: PROTOCOL_COLORS[name as keyof typeof PROTOCOL_COLORS] || CHART_COLORS.muted,
      }))

    const countries = Object.entries(countryCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([code, count]) => ({
        code,
        name: code,
        count,
      }))

    return {
      sources,
      protocols,
      countries,
      flows: sourceFlow,
    }
  }, [sourceFlow])

  if (data.sources.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Proxy Flow</CardTitle>
        </CardHeader>
        <CardContent className="h-[300px] flex items-center justify-center">
          <p className="text-muted-foreground">No flow data available</p>
        </CardContent>
      </Card>
    )
  }

  const maxSourceCount = Math.max(...data.sources.map((s) => s.count))
  const maxProtocolCount = Math.max(...data.protocols.map((p) => p.count))
  const maxCountryCount = Math.max(...data.countries.map((c) => c.count))

  return (
    <Card>
      <CardHeader>
        <CardTitle id="sankey-flow-title">Proxy Flow</CardTitle>
        <CardDescription id="sankey-flow-desc">
          Source → Protocol → Country distribution
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          role="img"
          aria-labelledby="sankey-flow-title sankey-flow-desc"
          className="flex justify-between gap-4 min-h-[300px]"
        >
          <div className="flex-1 space-y-2">
            <p className="text-xs font-medium text-muted-foreground text-center mb-3">Sources</p>
            {data.sources.map((source) => (
              <div key={source.name} className="relative">
                <div
                  className="h-8 rounded-md flex items-center px-2 text-xs font-medium text-white overflow-hidden motion-reduce:transition-none"
                  style={{
                    backgroundColor: source.color,
                    width: `${(source.count / maxSourceCount) * 100}%`,
                    minWidth: "60px",
                  }}
                >
                  <span className="truncate">{source.name}</span>
                </div>
                <span className="absolute right-0 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
                  {source.count.toLocaleString()}
                </span>
              </div>
            ))}
          </div>

          <div className="flex-1 space-y-2">
            <p className="text-xs font-medium text-muted-foreground text-center mb-3">Protocols</p>
            {data.protocols.map((protocol) => (
              <div key={protocol.name} className="relative">
                <div
                  className="h-8 rounded-md flex items-center justify-center px-2 text-xs font-medium text-white motion-reduce:transition-none"
                  style={{
                    backgroundColor: protocol.color,
                    width: `${(protocol.count / maxProtocolCount) * 100}%`,
                    minWidth: "60px",
                    marginLeft: "auto",
                    marginRight: "auto",
                  }}
                >
                  {protocol.name}
                </div>
                <span className="absolute right-0 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
                  {protocol.count.toLocaleString()}
                </span>
              </div>
            ))}
          </div>

          <div className="flex-1 space-y-2">
            <p className="text-xs font-medium text-muted-foreground text-center mb-3">Countries</p>
            {data.countries.map((country) => (
              <div key={country.code} className="relative flex justify-end">
                <div
                  className="h-8 rounded-md flex items-center justify-end px-2 text-xs font-medium text-white overflow-hidden motion-reduce:transition-none"
                  style={{
                    backgroundColor: `hsl(${country.code.charCodeAt(0) * 5}, 60%, 45%)`,
                    width: `${(country.count / maxCountryCount) * 100}%`,
                    minWidth: "60px",
                  }}
                >
                  <span>{country.code}</span>
                </div>
                <span className="absolute left-0 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
                  {country.count.toLocaleString()}
                </span>
              </div>
            ))}
          </div>

          <table className="sr-only">
            <caption>Proxy flow from sources through protocols to countries</caption>
            <thead>
              <tr>
                <th scope="col">Source</th>
                <th scope="col">Protocol</th>
                <th scope="col">Country</th>
                <th scope="col">Count</th>
              </tr>
            </thead>
            <tbody>
              {data.flows.slice(0, 50).map((flow, i) => (
                <tr key={`${flow.source}-${flow.protocol}-${flow.country}-${i}`}>
                  <td>{flow.source}</td>
                  <td>{flow.protocol}</td>
                  <td>{flow.country}</td>
                  <td>{flow.count.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}