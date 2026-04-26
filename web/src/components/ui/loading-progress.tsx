import { useEffect, useState } from "react"
import { motion, AnimatePresence } from "motion/react"
import { cn } from "@/lib/utils"

interface LoadingProgressProps {
  loading: boolean
  progress?: number // 0-100, undefined = indeterminate
  className?: string
}

export function LoadingProgress({ loading, progress, className }: LoadingProgressProps) {
  const [styles, setStyles] = useState({ width: "0%" });

  useEffect(() => {
    if (loading) {
      if (progress !== undefined) {
        setStyles({ width: `${Math.max(5, Math.min(100, progress))}%` });
      } else {
        // Indeterminate animation handled by CSS class
        setStyles({ width: "100%" });
      }
    } else {
      setStyles({ width: "100%" });
    }
  }, [loading, progress]);

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
        >
          <div
            className={cn(
              "h-full bg-primary transition-all duration-300 ease-out",
              progress === undefined && "animate-progress-indeterminate origin-left"
            )}
            style={progress !== undefined ? styles : undefined}
          />
        </motion.div>
      )}
    </AnimatePresence>
  )
}
