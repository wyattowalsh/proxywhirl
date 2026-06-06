import { Copy, Star, Terminal } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import type { Proxy, Protocol } from "@/types"

interface ProxyCardProps {
  proxy: Proxy
  onCopy: () => void
  onTest?: () => void
  isFavorite?: boolean
  onToggleFavorite?: () => void
}

export function ProxyCard({ proxy, onCopy, onTest, isFavorite, onToggleFavorite }: ProxyCardProps) {
  return (
    <div className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          {/* IP:Port and Protocol */}
          <div className="flex items-center gap-2 flex-wrap">
            <code className="text-sm font-mono truncate">
              {proxy.ip}:{proxy.port}
            </code>
            <Badge variant={proxy.protocol as Protocol}>
              {proxy.protocol.toUpperCase()}
            </Badge>
          </div>
          
          {/* Location and Response Time */}
          <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
            {proxy.country_code && (
              <span title={proxy.country || undefined}>
                {proxy.country_code}
                {proxy.city && <span className="text-xs ml-1 opacity-70">{proxy.city}</span>}
              </span>
            )}
            {proxy.response_time !== null && (
              <span className="font-mono">{proxy.response_time.toFixed(0)}ms</span>
            )}
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex gap-1 shrink-0">
          {onToggleFavorite && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={onToggleFavorite}
              aria-label={isFavorite ? "Remove proxy from favorites" : "Add proxy to favorites"}
            >
              <Star className={`h-4 w-4 ${isFavorite ? "fill-yellow-500 text-yellow-500" : ""}`} aria-hidden="true" />
            </Button>
          )}
          {onTest && (
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={onTest}
              title="Copy test command"
              aria-label="Copy test command"
            >
              <Terminal className="h-4 w-4" aria-hidden="true" />
            </Button>
          )}
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8"
            onClick={onCopy}
            aria-label="Copy proxy address"
          >
            <Copy className="h-4 w-4" aria-hidden="true" />
          </Button>
        </div>
      </div>
    </div>
  )
}
