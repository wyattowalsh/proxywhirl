import { useSearchParams } from "react-router-dom"
import { useCallback, useMemo } from "react"
import type { Protocol } from "@/types"
import type { ProxyFilters, SortField, SortDirection } from "./useProxies"

const VALID_PROTOCOLS: Protocol[] = ["http", "socks4", "socks5"]

interface UrlFilterState {
  filters: ProxyFilters
  sortField: SortField
  sortDirection: SortDirection
  setFilters: (filters: ProxyFilters) => void
  setSort: (field: SortField, direction: SortDirection) => void
  clearAll: () => void
}

export function useUrlFilters(): UrlFilterState {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters = useMemo<ProxyFilters>(() => {
    const q = searchParams.get("q") || ""
    const protocolsParam = searchParams.get("protocols")?.split(",") || []
    const protocols = protocolsParam.filter((p): p is Protocol => VALID_PROTOCOLS.includes(p as Protocol))
    const countries = searchParams.get("countries")?.split(",").filter(Boolean) || []

    return {
      search: q,
      protocols,
      statuses: [],
      countries,
    }
  }, [searchParams])

  const sortField = useMemo<SortField>(() => {
    const sort = searchParams.get("sort")
    if (sort && ["ip", "port", "protocol", "status", "response_time", "source", "created_at"].includes(sort)) {
      return sort as SortField
    }
    return "response_time"
  }, [searchParams])

  const sortDirection = useMemo<SortDirection>(() => {
    const dir = searchParams.get("dir")
    return dir === "desc" ? "desc" : "asc"
  }, [searchParams])

  const setFilters = useCallback((newFilters: ProxyFilters) => {
    setSearchParams(prev => {
      const params = new URLSearchParams(prev)
      
      // Search
      if (newFilters.search) {
        params.set("q", newFilters.search)
      } else {
        params.delete("q")
      }
      
      // Protocols
      if (newFilters.protocols.length > 0) {
        params.set("protocols", newFilters.protocols.join(","))
      } else {
        params.delete("protocols")
      }
      
      // Countries
      if (newFilters.countries.length > 0) {
        params.set("countries", newFilters.countries.join(","))
      } else {
        params.delete("countries")
      }
      
      return params
    }, { replace: true })
  }, [setSearchParams])

  const setSort = useCallback((field: SortField, direction: SortDirection) => {
    setSearchParams(prev => {
      const params = new URLSearchParams(prev)
      
      if (field !== "response_time") {
        params.set("sort", field)
      } else {
        params.delete("sort")
      }
      
      if (direction !== "asc") {
        params.set("dir", direction)
      } else {
        params.delete("dir")
      }
      
      return params
    }, { replace: true })
  }, [setSearchParams])

  const clearAll = useCallback(() => {
    setSearchParams({}, { replace: true })
  }, [setSearchParams])

  return {
    filters,
    sortField,
    sortDirection,
    setFilters,
    setSort,
    clearAll,
  }
}
