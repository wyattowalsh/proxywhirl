// components/theme-provider.tsx - Theme context and provider
import React, { createContext, useContext, useEffect, useState } from 'react'
import { applyTheme, getSystemTheme, getStoredTheme, setStoredTheme, themes, type ThemeConfig } from '@/lib/theme'

interface ThemeContextType {
  theme: string
  setTheme: (theme: string) => void
  themes: Record<string, ThemeConfig>
  systemTheme: 'light' | 'dark'
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

interface ThemeProviderProps {
  children: React.ReactNode
  defaultTheme?: string
  storageKey?: string
}

export function ThemeProvider({ 
  children, 
  defaultTheme = 'system',
  storageKey = 'proxywhirl-theme'
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<string>(() => {
    if (typeof window === 'undefined') return defaultTheme
    const stored = localStorage.getItem(storageKey)
    return stored || defaultTheme
  })
  
  const [systemTheme, setSystemTheme] = useState<'light' | 'dark'>(() => {
    if (typeof window === 'undefined') return 'light'
    return getSystemTheme()
  })

  // Apply theme on mount and when theme changes
  useEffect(() => {
    const root = document.documentElement
    root.classList.remove('light', 'dark')

    const themeToApply = theme === 'system' ? systemTheme : theme
    
    if (themeToApply === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.add('light')
    }

    applyTheme(themeToApply)
  }, [theme, systemTheme])

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const handleChange = (e: MediaQueryListEvent) => {
      setSystemTheme(e.matches ? 'dark' : 'light')
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  const setTheme = (newTheme: string) => {
    setStoredTheme(newTheme)
    setThemeState(newTheme)
  }

  const value = {
    theme,
    setTheme,
    themes,
    systemTheme
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

// Theme toggle component
export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  const toggleTheme = () => {
    if (theme === 'light') {
      setTheme('dark')
    } else if (theme === 'dark') {
      setTheme('system')
    } else {
      setTheme('light')
    }
  }

  return (
    <button
      onClick={toggleTheme}
      className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 w-10"
      aria-label="Toggle theme"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0"
      >
        <circle cx="12" cy="12" r="5" />
        <path d="M12 1v2" />
        <path d="M12 21v2" />
        <path d="m4.22 4.22 1.42 1.42" />
        <path d="m18.36 18.36 1.42 1.42" />
        <path d="M1 12h2" />
        <path d="M21 12h2" />
        <path d="m4.22 19.78 1.42-1.42" />
        <path d="m18.36 5.64 1.42-1.42" />
      </svg>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="absolute rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100"
      >
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
      </svg>
    </button>
  )
}

// Theme selector dropdown
export function ThemeSelector() {
  const { theme, setTheme, themes } = useTheme()

  return (
    <select
      value={theme}
      onChange={(e) => setTheme(e.target.value)}
      className="flex h-9 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    >
      <option value="system">System</option>
      {Object.entries(themes).map(([key, config]) => (
        <option key={key} value={key}>
          {config.name}
        </option>
      ))}
    </select>
  )
}
