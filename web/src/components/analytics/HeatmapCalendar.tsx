import { useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { CHART_COLORS, getHeatmapColor } from "@/lib/chart-tokens"
import type { Proxy, Stats } from "@/types"

interface HeatmapCalendarProps {
  proxies?: Proxy[]
  stats?: Stats | null
}

function formatDate(date: Date): string {
  return date.toISOString().split("T")[0]
}

function getTooltipText(date: Date, count: number): string {
  const dateStr = date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  })
  return `${dateStr}: ${count.toLocaleString()} proxies discovered`
}

function buildCountsFromProxies(proxies: Proxy[]): Record<string, number> {
  const counts: Record<string, number> = {}
  const now = new Date()
  const startDate = new Date(now)
  startDate.setDate(startDate.getDate() - 90)

  proxies.forEach((proxy) => {
    if (proxy.created_at) {
      const date = new Date(proxy.created_at)
      if (date >= startDate && date <= now) {
        const key = formatDate(date)
        counts[key] = (counts[key] || 0) + 1
      }
    }
  })

  return counts
}

export function HeatmapCalendar({ proxies = [], stats }: HeatmapCalendarProps) {
  const { data, maxCount, weeks, months, tableRows } = useMemo(() => {
    const precomputed = stats?.aggregations?.discovery_by_date
    const counts =
      precomputed && Object.keys(precomputed).length > 0
        ? { ...precomputed }
        : buildCountsFromProxies(proxies)

    const now = new Date()
    const startDate = new Date(now)
    startDate.setDate(startDate.getDate() - 90)

    const weeks: Array<Array<{ date: Date; count: number; key: string }>> = []
    let maxCount = 0

    const calendarStart = new Date(startDate)
    calendarStart.setDate(calendarStart.getDate() - calendarStart.getDay())

    const currentDate = new Date(calendarStart)
    let currentWeek: Array<{ date: Date; count: number; key: string }> = []

    while (currentDate <= now) {
      const key = formatDate(currentDate)
      const count = counts[key] || 0
      maxCount = Math.max(maxCount, count)

      currentWeek.push({
        date: new Date(currentDate),
        count,
        key,
      })

      if (currentWeek.length === 7) {
        weeks.push(currentWeek)
        currentWeek = []
      }

      currentDate.setDate(currentDate.getDate() + 1)
    }

    if (currentWeek.length > 0) {
      weeks.push(currentWeek)
    }

    const months: Array<{ name: string; weekIndex: number }> = []
    let lastMonth = -1
    weeks.forEach((week, weekIndex) => {
      const firstDayOfWeek = week[0]?.date
      if (firstDayOfWeek) {
        const month = firstDayOfWeek.getMonth()
        if (month !== lastMonth) {
          months.push({
            name: firstDayOfWeek.toLocaleDateString("en-US", { month: "short" }),
            weekIndex,
          })
          lastMonth = month
        }
      }
    })

    const tableRows = Object.entries(counts)
      .filter(([, count]) => count > 0)
      .sort(([a], [b]) => b.localeCompare(a))

    return { data: counts, maxCount, weeks, months, tableRows }
  }, [proxies, stats])

  const totalDiscovered = Object.values(data).reduce((sum, c) => sum + c, 0)

  return (
    <Card>
      <CardHeader>
        <CardTitle id="heatmap-calendar-title">Discovery Activity</CardTitle>
        <CardDescription id="heatmap-calendar-desc">
          {totalDiscovered.toLocaleString()} proxies discovered in the last 90 days
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div
          role="img"
          aria-labelledby="heatmap-calendar-title heatmap-calendar-desc"
          className="overflow-x-auto"
        >
          <div className="flex ml-8 mb-1">
            {months.map((month, i) => (
              <div
                key={i}
                className="text-xs text-muted-foreground"
                style={{
                  marginLeft:
                    i === 0
                      ? month.weekIndex * 14
                      : (month.weekIndex - months[i - 1].weekIndex - 1) * 14,
                  width: 14,
                }}
              >
                {month.name}
              </div>
            ))}
          </div>

          <div className="flex">
            <div className="flex flex-col justify-around mr-2 text-xs text-muted-foreground">
              <span>Mon</span>
              <span>Wed</span>
              <span>Fri</span>
            </div>

            <div className="flex gap-[2px]" aria-hidden="true">
              {weeks.map((week, weekIndex) => (
                <div key={weekIndex} className="flex flex-col gap-[2px]">
                  {week.map((day) => (
                    <div
                      key={day.key}
                      className="w-3 h-3 rounded-sm cursor-default"
                      style={{ backgroundColor: getHeatmapColor(day.count, maxCount) }}
                      title={getTooltipText(day.date, day.count)}
                    />
                  ))}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 mt-4 text-xs text-muted-foreground">
            <span>Less</span>
            <div className="flex gap-[2px]" aria-hidden="true">
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: CHART_COLORS.heatmapEmpty }} />
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: CHART_COLORS.heatmapLow }} />
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: CHART_COLORS.heatmapMidLow }} />
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: CHART_COLORS.heatmapMid }} />
              <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: CHART_COLORS.heatmapHigh }} />
            </div>
            <span>More</span>
          </div>
        </div>
        <table className="sr-only">
          <caption>Daily proxy discovery counts for the last 90 days</caption>
          <thead>
            <tr>
              <th scope="col">Date</th>
              <th scope="col">Proxies discovered</th>
            </tr>
          </thead>
          <tbody>
            {tableRows.map(([date, count]) => (
              <tr key={date}>
                <td>{date}</td>
                <td>{count.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  )
}