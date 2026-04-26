import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { LucideIcon } from "lucide-react"

interface StatsCardProps {
  title: string
  value: string | number
  description?: string
  icon?: LucideIcon
  className?: string
  color?: string
}

export function StatsCard({
  title,
  value,
  description,
  icon: Icon,
  className,
  color,
}: StatsCardProps) {
  return (
    <Card className={cn("", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {Icon && (
          <Icon
            className="h-4 w-4 text-muted-foreground"
            style={color ? { color } : undefined}
          />
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold" style={color ? { color } : undefined}>
          {value}
        </div>
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  )
}
