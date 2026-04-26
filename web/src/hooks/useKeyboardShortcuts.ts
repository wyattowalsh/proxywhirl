import { useEffect, useCallback } from "react"

interface ShortcutHandlers {
  onSearch?: () => void
  onClearFilters?: () => void
  onCopyAll?: () => void
  onToggleHelp?: () => void
  onToggleFilters?: () => void
}

export function useKeyboardShortcuts({
  onSearch,
  onClearFilters,
  onCopyAll,
  onToggleHelp,
  onToggleFilters,
}: ShortcutHandlers) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Don't trigger if user is typing in an input
    const target = e.target as HTMLElement
    if (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable) {
      // Allow Escape to work even in inputs
      if (e.key === "Escape") {
        (target as HTMLInputElement).blur()
        onClearFilters?.()
      }
      return
    }

    // Don't trigger with modifier keys (except for some)
    if (e.metaKey || e.ctrlKey || e.altKey) {
      return
    }

    switch (e.key) {
      case "/":
        e.preventDefault()
        onSearch?.()
        break
      case "Escape":
        onClearFilters?.()
        break
      case "c":
        onCopyAll?.()
        break
      case "?":
        e.preventDefault()
        onToggleHelp?.()
        break
      case "f":
        e.preventDefault()
        onToggleFilters?.()
        break
    }
  }, [onSearch, onClearFilters, onCopyAll, onToggleHelp, onToggleFilters])

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [handleKeyDown])
}

export const SHORTCUTS = [
  { key: "/", description: "Focus search" },
  { key: "f", description: "Toggle filters" },
  { key: "c", description: "Copy all filtered proxies" },
  { key: "Esc", description: "Clear search / close modals" },
  { key: "?", description: "Show keyboard shortcuts" },
] as const
