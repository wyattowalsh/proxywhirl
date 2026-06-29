/** Semantic chart color tokens for consistent theming across chart components */

export const CHART_COLORS = {
  success: "#22c55e",
  warning: "#eab308",
  danger: "#ef4444",
  info: "#3b82f6",
  muted: "#6b7280",
  neutral: "#8884d8",

  fast: "#22c55e",
  medium: "#eab308",
  slow: "#ef4444",

  elite: "#22c55e",
  reliable: "#3b82f6",
  moderate: "#f59e0b",
  marginal: "#f97316",

  heatmapEmpty: "hsl(var(--muted))",
  heatmapLow: "#dcfce7",
  heatmapMidLow: "#86efac",
  heatmapMid: "#22c55e",
  heatmapHigh: "#15803d",

  atmosphere: "#3b82f6",
} as const

export const CHART_SERIES_COLORS = [
  "#3b82f6",
  "#22c55e",
  "#f59e0b",
  "#8b5cf6",
  "#ec4899",
  "#14b8a6",
  "#6366f1",
  "#f97316",
  "#84cc16",
  "#06b6d4",
  "#a855f7",
  "#10b981",
  "#f43f5e",
  "#0ea5e9",
  "#d946ef",
] as const

export const RESPONSE_TIME_BIN_COLORS = [
  "#22c55e",
  "#84cc16",
  "#eab308",
  "#f97316",
  "#ef4444",
  "#dc2626",
] as const

export const PORT_COLORS: Record<number, string> = {
  80: "#3b82f6",
  8080: "#22c55e",
  3128: "#f59e0b",
  1080: "#8b5cf6",
  8888: "#ec4899",
  8000: "#14b8a6",
  443: "#6366f1",
  3129: "#f97316",
  0: CHART_COLORS.muted,
}

export const RELIABILITY_TIER_COLORS = {
  Elite: CHART_COLORS.elite,
  Reliable: CHART_COLORS.reliable,
  Moderate: CHART_COLORS.moderate,
  Marginal: CHART_COLORS.marginal,
} as const

export function getSeriesColor(index: number): string {
  return CHART_SERIES_COLORS[index % CHART_SERIES_COLORS.length]
}

export function getSpeedColor(ms: number): string {
  if (ms <= 500) return CHART_COLORS.fast
  if (ms <= 1500) return CHART_COLORS.medium
  return CHART_COLORS.slow
}

export function getConfidenceColor(score: number): string {
  if (score >= 70) return CHART_COLORS.success
  if (score >= 40) return CHART_COLORS.warning
  return CHART_COLORS.danger
}

export function getHeatmapColor(count: number, max: number): string {
  if (count === 0) return CHART_COLORS.heatmapEmpty
  const intensity = Math.min(count / max, 1)
  if (intensity < 0.25) return CHART_COLORS.heatmapLow
  if (intensity < 0.5) return CHART_COLORS.heatmapMidLow
  if (intensity < 0.75) return CHART_COLORS.heatmapMid
  return CHART_COLORS.heatmapHigh
}