// lib/theme.ts - Comprehensive theme configuration

// Theme token definitions
export const lightTheme = {
  // Base colors
  background: 'hsl(0 0% 100%)',
  foreground: 'hsl(222.2 84% 4.9%)',
  
  // Card colors
  card: 'hsl(0 0% 100%)',
  'card-foreground': 'hsl(222.2 84% 4.9%)',
  
  // Popover colors
  popover: 'hsl(0 0% 100%)',
  'popover-foreground': 'hsl(222.2 84% 4.9%)',
  
  // Primary colors
  primary: 'hsl(221.2 83.2% 53.3%)',
  'primary-foreground': 'hsl(210 40% 98%)',
  
  // Secondary colors
  secondary: 'hsl(210 40% 96%)',
  'secondary-foreground': 'hsl(222.2 84% 4.9%)',
  
  // Muted colors
  muted: 'hsl(210 40% 96%)',
  'muted-foreground': 'hsl(215.4 16.3% 46.9%)',
  
  // Accent colors
  accent: 'hsl(210 40% 96%)',
  'accent-foreground': 'hsl(222.2 84% 4.9%)',
  
  // Destructive colors
  destructive: 'hsl(0 84.2% 60.2%)',
  'destructive-foreground': 'hsl(210 40% 98%)',
  
  // Border colors
  border: 'hsl(214.3 31.8% 91.4%)',
  input: 'hsl(214.3 31.8% 91.4%)',
  ring: 'hsl(221.2 83.2% 53.3%)',
  
  // Custom ProxyWhirl colors
  'proxy-active': 'hsl(142.1 76.2% 36.3%)',
  'proxy-inactive': 'hsl(0 72.2% 50.6%)',
  'proxy-validating': 'hsl(47.9 95.8% 53.1%)',
  'proxy-unknown': 'hsl(215.4 16.3% 46.9%)',
  
  // Chart colors
  'chart-1': 'hsl(221.2 83.2% 53.3%)',
  'chart-2': 'hsl(142.1 76.2% 36.3%)',
  'chart-3': 'hsl(47.9 95.8% 53.1%)',
  'chart-4': 'hsl(280.0 100% 70.0%)',
  'chart-5': 'hsl(9.0 100% 64.0%)',
  
  // Status colors
  success: 'hsl(142.1 76.2% 36.3%)',
  warning: 'hsl(47.9 95.8% 53.1%)',
  error: 'hsl(0 84.2% 60.2%)',
  info: 'hsl(221.2 83.2% 53.3%)',
  
  // Sidebar colors
  'sidebar-primary': 'hsl(222.2 84% 4.9%)',
  'sidebar-primary-foreground': 'hsl(210 40% 98%)',
  'sidebar-accent': 'hsl(210 40% 96%)',
  'sidebar-accent-foreground': 'hsl(222.2 84% 4.9%)',
  'sidebar-border': 'hsl(214.3 31.8% 91.4%)',
  'sidebar-ring': 'hsl(221.2 83.2% 53.3%)'
} as const

export const darkTheme = {
  // Base colors
  background: 'hsl(222.2 84% 4.9%)',
  foreground: 'hsl(210 40% 98%)',
  
  // Card colors
  card: 'hsl(222.2 84% 4.9%)',
  'card-foreground': 'hsl(210 40% 98%)',
  
  // Popover colors
  popover: 'hsl(222.2 84% 4.9%)',
  'popover-foreground': 'hsl(210 40% 98%)',
  
  // Primary colors
  primary: 'hsl(217.2 91.2% 59.8%)',
  'primary-foreground': 'hsl(222.2 84% 4.9%)',
  
  // Secondary colors
  secondary: 'hsl(217.2 32.6% 17.5%)',
  'secondary-foreground': 'hsl(210 40% 98%)',
  
  // Muted colors
  muted: 'hsl(217.2 32.6% 17.5%)',
  'muted-foreground': 'hsl(215 20.2% 65.1%)',
  
  // Accent colors
  accent: 'hsl(217.2 32.6% 17.5%)',
  'accent-foreground': 'hsl(210 40% 98%)',
  
  // Destructive colors
  destructive: 'hsl(0 72.2% 50.6%)',
  'destructive-foreground': 'hsl(210 40% 98%)',
  
  // Border colors
  border: 'hsl(217.2 32.6% 17.5%)',
  input: 'hsl(217.2 32.6% 17.5%)',
  ring: 'hsl(217.2 91.2% 59.8%)',
  
  // Custom ProxyWhirl colors
  'proxy-active': 'hsl(142.1 70.6% 45.3%)',
  'proxy-inactive': 'hsl(0 72.2% 50.6%)',
  'proxy-validating': 'hsl(47.9 95.8% 53.1%)',
  'proxy-unknown': 'hsl(215 20.2% 65.1%)',
  
  // Chart colors
  'chart-1': 'hsl(217.2 91.2% 59.8%)',
  'chart-2': 'hsl(142.1 70.6% 45.3%)',
  'chart-3': 'hsl(47.9 95.8% 53.1%)',
  'chart-4': 'hsl(280.0 100% 70.0%)',
  'chart-5': 'hsl(9.0 100% 64.0%)',
  
  // Status colors
  success: 'hsl(142.1 70.6% 45.3%)',
  warning: 'hsl(47.9 95.8% 53.1%)',
  error: 'hsl(0 72.2% 50.6%)',
  info: 'hsl(217.2 91.2% 59.8%)',
  
  // Sidebar colors
  'sidebar-primary': 'hsl(210 40% 98%)',
  'sidebar-primary-foreground': 'hsl(222.2 84% 4.9%)',
  'sidebar-accent': 'hsl(217.2 32.6% 17.5%)',
  'sidebar-accent-foreground': 'hsl(210 40% 98%)',
  'sidebar-border': 'hsl(217.2 32.6% 17.5%)',
  'sidebar-ring': 'hsl(217.2 91.2% 59.8%)'
} as const

// Theme configuration type
type ThemeColors = Record<string, string>

export interface ThemeConfig {
  name: string
  colors: ThemeColors
  cssVars: Record<string, string>
}

// Generate CSS variables from theme object
function generateCSSVars(theme: ThemeColors): Record<string, string> {
  const cssVars: Record<string, string> = {}
  
  Object.entries(theme).forEach(([key, value]) => {
    cssVars[`--${key}`] = value
  })
  
  return cssVars
}

// Theme configurations
export const themes: Record<string, ThemeConfig> = {
  light: {
    name: 'Light',
    colors: lightTheme,
    cssVars: generateCSSVars(lightTheme)
  },
  dark: {
    name: 'Dark', 
    colors: darkTheme,
    cssVars: generateCSSVars(darkTheme)
  }
}

// Helper function to apply theme
export function applyTheme(themeName: string) {
  const theme = themes[themeName]
  if (!theme) return
  
  const root = document.documentElement
  
  // Remove all existing theme variables
  Object.keys(themes).forEach(name => {
    Object.keys(themes[name].cssVars).forEach(cssVar => {
      root.style.removeProperty(cssVar)
    })
  })
  
  // Apply new theme variables
  Object.entries(theme.cssVars).forEach(([cssVar, value]) => {
    root.style.setProperty(cssVar, value)
  })
  
  // Update data attributes
  root.setAttribute('data-theme', themeName)
  document.body.className = document.body.className.replace(/theme-\w+/g, '') + ` theme-${themeName}`
}

// Theme detection utility
export function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

// Theme persistence
export function getStoredTheme(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('proxywhirl-theme')
}

export function setStoredTheme(theme: string) {
  if (typeof window === 'undefined') return
  localStorage.setItem('proxywhirl-theme', theme)
}

// Initialize theme on app start
export function initializeTheme() {
  const stored = getStoredTheme()
  const system = getSystemTheme()
  const theme = stored || system
  
  applyTheme(theme)
  return theme
}
