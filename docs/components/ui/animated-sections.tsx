'use client';

import { motion } from 'motion/react';
import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

interface HeroSectionProps {
  children: ReactNode;
  className?: string;
}

export function HeroSection({ children, className }: HeroSectionProps) {
  return (
    <motion.div 
      className={cn("flex flex-col items-center space-y-4 sm:space-y-6 mb-8 md:mb-10", className)}
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

interface FeatureGridProps {
  children: ReactNode;
  className?: string;
}

export function FeatureGrid({ children, className }: FeatureGridProps) {
  return (
    <motion.div 
      className={cn("grid grid-cols-1 md:grid-cols-3 gap-3 lg:gap-4 w-full max-w-5xl mb-6 md:mb-8", className)}
      initial={{ opacity: 0, y: 60 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8, ease: "easeOut", delay: 1 }}
    >
      {children}
    </motion.div>
  );
}

interface CTASectionProps {
  children: ReactNode;
  className?: string;
}

export function CTASection({ children, className }: CTASectionProps) {
  return (
    <motion.div 
      className={cn("flex flex-col sm:flex-row gap-4 lg:gap-6 items-center pb-4 md:pb-6", className)}
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut", delay: 1.8 }}
    >
      {children}
    </motion.div>
  );
}
