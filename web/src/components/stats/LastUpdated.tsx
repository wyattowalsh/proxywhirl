import { Clock } from "lucide-react"
import { formatRelativeTime } from "@/lib/utils"

interface LastUpdatedProps {
  timestamp: string
}

export function LastUpdated({ timestamp }: LastUpdatedProps) {
  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground">
      <Clock className="h-4 w-4" />
      <span>Last updated {formatRelativeTime(timestamp)}</span>
    </div>
  )
}
