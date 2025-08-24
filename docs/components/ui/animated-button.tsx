'use client';

import { motion } from 'motion/react';
import Link from 'next/link';
import type { ReactNode } from 'react';

interface AnimatedButtonProps {
  href: string;
  label: string;
  ariaLabel: string;
  external?: boolean;
  variant?: 'primary' | 'secondary';
  icon?: ReactNode;
  iconPosition?: 'left' | 'right';
}

export function AnimatedButton({ 
  href, 
  label, 
  ariaLabel, 
  external, 
  variant = 'primary',
  icon,
  iconPosition = 'right'
}: AnimatedButtonProps) {
  const isPrimary = variant === 'primary';
  
  const primaryClasses = "group relative inline-flex items-center justify-center px-10 lg:px-12 py-5 lg:py-6 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white font-bold text-lg lg:text-xl rounded-3xl overflow-hidden shadow-xl hover:shadow-2xl hover:shadow-blue-500/30 focus:outline-none focus:ring-4 focus:ring-blue-500/50 focus:ring-offset-2 focus:ring-offset-transparent transition-all duration-300";
  
  const secondaryClasses = "group relative inline-flex items-center justify-center px-10 lg:px-12 py-5 lg:py-6 bg-white/20 dark:bg-black/20 backdrop-blur-xl border border-white/40 dark:border-white/20 text-fd-foreground font-semibold text-lg lg:text-xl rounded-3xl hover:bg-white/30 dark:hover:bg-black/30 shadow-lg hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-transparent transition-all duration-300";

  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -2 }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
    >
      <Link
        href={href}
        className={isPrimary ? primaryClasses : secondaryClasses}
        target={external ? '_blank' : undefined}
        rel={external ? 'noopener noreferrer' : undefined}
        aria-label={ariaLabel}
      >
        {isPrimary && (
          <motion.div 
            className="absolute inset-0 bg-gradient-to-r from-purple-600 via-fuchsia-600 to-cyan-600 opacity-0 group-hover:opacity-100"
            initial={false}
            whileHover={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          />
        )}
        
        <span className="relative z-10 flex items-center font-semibold tracking-wide">
          {icon && iconPosition === 'left' && (
            <motion.div
              className="mr-3"
              whileHover={{ 
                rotate: isPrimary ? 0 : 12, 
                scale: 1.1,
                x: isPrimary ? 4 : 0 
              }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              {icon}
            </motion.div>
          )}
          
          {label}
          
          {icon && iconPosition === 'right' && (
            <motion.div
              className="ml-3"
              whileHover={{ 
                x: isPrimary ? 4 : 0,
                rotate: isPrimary ? 0 : 12,
                scale: 1.1 
              }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              {icon}
            </motion.div>
          )}
        </span>
        
        {isPrimary ? (
          // Enhanced glow effect for primary
          <motion.div
            className="absolute inset-0 rounded-3xl"
            style={{
              background: 'radial-gradient(circle at center, rgba(255,255,255,0.1) 0%, transparent 70%)'
            }}
            initial={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.3 }}
          />
        ) : (
          // Glass morphism enhancement for secondary
          <motion.div
            className="absolute inset-0 rounded-3xl bg-gradient-to-r from-white/10 to-white/5 dark:from-white/5 dark:to-white/10 opacity-0 group-hover:opacity-100"
            initial={false}
            whileHover={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          />
        )}
      </Link>
    </motion.div>
  );
}
