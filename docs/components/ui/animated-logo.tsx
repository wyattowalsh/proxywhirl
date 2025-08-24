'use client';

import { motion } from 'motion/react';
import Image from 'next/image';
import type { StaticImageData } from 'next/image';

interface AnimatedLogoProps {
  src: StaticImageData;
  alt: string;
  width: number;
  height: number;
}

export function AnimatedLogo({ src, alt, width, height }: AnimatedLogoProps) {
  return (
    <motion.div 
      className="relative group"
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
      whileHover={{ scale: 1.05 }}
    >
      {/* Enhanced Multiple glow rings for depth */}
      <motion.div 
        className="absolute inset-0 w-32 h-32 bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500 rounded-full blur-xl opacity-30 group-hover:opacity-60"
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
      />
      <motion.div 
        className="absolute inset-0 w-28 h-28 bg-gradient-to-r from-cyan-400 to-blue-400 rounded-full blur-lg opacity-40 group-hover:opacity-80"
        animate={{ rotate: -360 }}
        transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
      />
      <motion.div 
        className="absolute inset-0 w-24 h-24 bg-gradient-to-r from-purple-400 to-indigo-400 rounded-full blur-md opacity-50 group-hover:opacity-90"
        animate={{ rotate: 360 }}
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
      />
      <motion.div 
        className="relative transform group-hover:scale-110 transition-transform duration-500 ease-out"
        whileHover={{ rotate: [0, -5, 5, 0] }}
        transition={{ duration: 0.6, ease: "easeInOut" }}
      >
        <Image
          src={src}
          alt={alt}
          width={width}
          height={height}
          className="drop-shadow-2xl relative z-10"
          priority
        />
      </motion.div>
    </motion.div>
  );
}
