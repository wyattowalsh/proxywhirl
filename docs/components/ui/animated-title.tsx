'use client';

import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

interface AnimatedTitleProps {
  title: string;
  subtitle: string;
  className?: string;
}

export function AnimatedTitle({ title, subtitle, className }: AnimatedTitleProps) {
  return (
    <motion.div 
      className={cn("space-y-6", className)}
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut", delay: 0.4 }}
    >
      <motion.h1 
        className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-black tracking-tight leading-none"
        whileHover={{ scale: 1.02 }}
        transition={{ type: "spring", stiffness: 400, damping: 10 }}
      >
        <motion.span 
          className="brand-text"
          style={{
            // Fallback gradient in case CSS custom properties don't load
            background: `linear-gradient(135deg, 
              rgb(34, 197, 94) 0%,
              rgb(6, 182, 212) 35%,
              rgb(59, 130, 246) 70%,
              rgb(147, 51, 234) 100%
            )`,
            backgroundSize: '200% 100%',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            color: 'transparent'
          }}
          animate={{ 
            backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
        >
          {title}
        </motion.span>
      </motion.h1>

      {/* Enhanced tagline with better typography */}
      <motion.p 
        className="text-md sm:text-lg lg:text-xl xl:text-2xl text-fd-muted-foreground max-w-4xl leading-relaxed font-light tracking-wide"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.6 }}
      >
        {subtitle}
      </motion.p>
    </motion.div>
  );
}
