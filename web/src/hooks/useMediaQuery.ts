import { useState, useEffect } from "react"

export function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window !== "undefined") {
      return window.matchMedia(query).matches
    }
    return false
  })

  useEffect(() => {
    const mediaQuery = window.matchMedia(query)
    const handler = (event: MediaQueryListEvent) => setMatches(event.matches)
    
    // Set initial value
    setMatches(mediaQuery.matches)
    
    // Listen for changes
    mediaQuery.addEventListener("change", handler)
    return () => mediaQuery.removeEventListener("change", handler)
  }, [query])

  return matches
}

// Convenience hooks for common breakpoints (matching Tailwind defaults)
export function useIsMobile(): boolean {
  return !useMediaQuery("(min-width: 768px)")
}

export function useIsTablet(): boolean {
  return useMediaQuery("(min-width: 768px)") && !useMediaQuery("(min-width: 1024px)")
}

export function useIsDesktop(): boolean {
  return useMediaQuery("(min-width: 1024px)")
}
