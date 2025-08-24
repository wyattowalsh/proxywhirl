'use client';

import { motion } from 'motion/react';
import type { ReactNode } from 'react';

interface HeroSectionProps {
  children: ReactNode;
}

export function HeroSection({ children }: HeroSectionProps) {
  return (
    <motion.div 
      className="flex flex-col items-center space-y-4 sm:space-y-6 mb-8 md:mb-10"
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
}

export function FeatureGrid({ children }: FeatureGridProps) {
  return (
    <motion.div 
      className="grid grid-cols-1 md:grid-cols-3 gap-3 lg:gap-4 w-full max-w-5xl mb-6 md:mb-8"
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
}

export function CTASection({ children }: CTASectionProps) {
  return (
    <motion.div 
      className="flex flex-col sm:flex-row gap-4 lg:gap-6 items-center pb-4 md:pb-6"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut", delay: 1.8 }}
    >
      {children}
    </motion.div>
  );
}
