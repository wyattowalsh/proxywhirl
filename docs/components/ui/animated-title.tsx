'use client';

import { motion } from 'motion/react';

interface AnimatedTitleProps {
  title: string;
  subtitle: string;
}

export function AnimatedTitle({ title, subtitle }: AnimatedTitleProps) {
  return (
    <motion.div 
      className="space-y-6"
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
          className="pw bg-gradient-to-r from-blue-600 via-purple-600 to-teal-600 bg-clip-text text-transparent drop-shadow-sm"
          animate={{ 
            backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          style={{ backgroundSize: "200% 100%" }}
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
