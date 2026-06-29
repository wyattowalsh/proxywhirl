import { Clock } from "lucide-react"
import { formatRelativeTime } from "@/lib/utils"
import type { Stats } from "@/types"

interface LastUpdatedProps {
  timestamp: string
  /** Prefer metadata.json generated_at when bundled in stats */
  metadataGeneratedAt?: string | null
  stats?: Stats | null
}

export function LastUpdated({
  timestamp,
  metadataGeneratedAt,
  stats,
}: LastUpdatedProps) {
  const displayTimestamp =
    metadataGeneratedAt ?? stats?.metadata_generated_at ?? timestamp

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <Clock className="h-4 w-4" aria-hidden="true" />
      <span>Last updated {formatRelativeTime(displayTimestamp)}</span>
    </div>
  )
}