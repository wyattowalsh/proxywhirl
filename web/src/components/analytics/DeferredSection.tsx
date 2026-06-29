"use client"

import { useEffect, useRef, useState, type ReactNode } from "react"

interface DeferredSectionProps {
  children: ReactNode
  fallback: ReactNode
  /** IntersectionObserver rootMargin — load slightly before entering viewport */
  rootMargin?: string
  className?: string
}

/**
 * Defers rendering children until the section enters (or nears) the viewport.
 * Disconnects the observer after first intersection to avoid repeat work.
 */
export function DeferredSection({
  children,
  fallback,
  rootMargin = "200px 0px",
  className,
}: DeferredSectionProps) {
  const ref = useRef<HTMLElement>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el || visible) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry?.isIntersecting) {
          setVisible(true)
          observer.disconnect()
        }
      },
      { rootMargin },
    )

    observer.observe(el)
    return () => observer.disconnect()
  }, [rootMargin, visible])

  return (
    <section ref={ref} className={className}>
      {visible ? children : fallback}
    </section>
  )
}