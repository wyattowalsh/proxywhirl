import type { Variants } from 'motion/react'

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
}

export const slideUp: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
}

export const slideDown: Variants = {
  hidden: { opacity: 0, y: -20 },
  visible: { opacity: 1, y: 0 },
}

export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: { opacity: 1, scale: 1 },
}

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
}

export const staggerFast: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
    },
  },
}

// Transition presets
export const transitions = {
  spring: { type: 'spring', stiffness: 300, damping: 25 },
  smooth: { duration: 0.3, ease: 'easeOut' },
  fast: { duration: 0.15, ease: 'easeOut' },
  slow: { duration: 0.5, ease: 'easeInOut' },
} as const

// Button interaction presets
export const buttonInteraction = {
  whileHover: { scale: 1.02 },
  whileTap: { scale: 0.98 },
  transition: transitions.fast,
}

export const cardInteraction = {
  whileHover: { scale: 1.02, y: -2 },
  transition: transitions.smooth,
}
