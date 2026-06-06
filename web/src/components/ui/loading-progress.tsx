import { motion, AnimatePresence } from "motion/react"
import { cn } from "@/lib/utils"

interface LoadingProgressProps {
  loading: boolean
  progress?: number // 0-100, undefined = indeterminate
  className?: string
}

export function LoadingProgress({ loading, progress, className }: LoadingProgressProps) {
  const clampedProgress =
    progress === undefined ? undefined : Math.max(5, Math.min(100, progress))
  const progressStyle =
    clampedProgress === undefined
      ? undefined
      : {
          transform: `scaleX(${clampedProgress / 100})`,
          transformOrigin: "left",
        }

  return (
    <AnimatePresence>
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className={cn(
            "fixed top-0 left-0 right-0 z-50 h-1 overflow-hidden bg-muted/20",
            className
          )}
          role="progressbar"
          aria-label="Loading proxy data"
          aria-valuemin={progress === undefined ? undefined : 0}
          aria-valuemax={progress === undefined ? undefined : 100}
          aria-valuenow={clampedProgress}
        >
          <div
            className={cn(
              "h-full bg-primary transition-transform duration-300 ease-out",
              progress === undefined && "animate-progress-indeterminate origin-left"
            )}
            style={progressStyle}
          />
        </motion.div>
      )}
    </AnimatePresence>
  )
}
