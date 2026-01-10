import { useEffect, useState } from "react"
import type { Stats } from "@/types"

const STATS_URL = import.meta.env.BASE_URL + "proxy-lists/stats.json"

export function useStats() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(STATS_URL)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch stats")
        return res.json()
      })
      .then((data: Stats) => {
        setStats(data)
        setError(null)
      })
      .catch((err) => {
        setError(err.message)
      })
      .finally(() => {
        setLoading(false)
      })
  }, [])

  return { stats, loading, error }
}
