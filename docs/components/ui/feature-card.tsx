'use client';

import { motion, useMotionValue, useSpring, useTransform } from 'motion/react';
import Link from 'next/link';
import type { ReactNode } from 'react';
import { LuSparkles, LuArrowRight, LuZap } from 'react-icons/lu';
import { useRef, useState } from 'react';

export interface Feature {
  icon: ReactNode;
  title: string;
  description: string;
  gradient: string;
  accentColor: string;
  href: string;
}

interface FeatureCardProps {
  feature: Feature;
  index: number;
}

export function FeatureCard({ feature, index }: FeatureCardProps) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [isHovered, setIsHovered] = useState(false);
  
  // Advanced physics-based motion values
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  // Spring physics for smooth, natural movement
  const springConfig = { damping: 25, stiffness: 300, mass: 0.5 };
  const rotateX = useSpring(useTransform(mouseY, [-300, 300], [15, -15]), springConfig);
  const rotateY = useSpring(useTransform(mouseX, [-300, 300], [-15, 15]), springConfig);
  const scale = useSpring(1, springConfig);
  
  // Advanced gradient position tracking
  const gradientX = useSpring(50, springConfig);
  const gradientY = useSpring(50, springConfig);
  
  // Sophisticated mouse tracking with magnetic effect
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    
    const rect = cardRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    mouseX.set(e.clientX - centerX);
    mouseY.set(e.clientY - centerY);
    
    // Magnetic gradient following
    const relativeX = ((e.clientX - rect.left) / rect.width) * 100;
    const relativeY = ((e.clientY - rect.top) / rect.height) * 100;
    gradientX.set(relativeX);
    gradientY.set(relativeY);
  };
  
  const handleMouseEnter = () => {
    setIsHovered(true);
    scale.set(1.03);
  };
  
  const handleMouseLeave = () => {
    setIsHovered(false);
    mouseX.set(0);
    mouseY.set(0);
    scale.set(1);
    gradientX.set(50);
    gradientY.set(50);
  };

  return (
    <Link href={feature.href} className="block group">
      <motion.article
        ref={cardRef}
        className="relative feature-card-enhanced overflow-hidden cursor-pointer will-change-transform"
        role="article"
        aria-labelledby={`feature-${index}-title`}
        tabIndex={0}
        initial={{ opacity: 0, y: 40, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ 
          duration: 0.7, 
          ease: [0.16, 1, 0.3, 1], 
          delay: 1.2 + index * 0.1 
        }}
        style={{
          perspective: 1000,
          transformStyle: 'preserve-3d',
          rotateX,
          rotateY,
          scale
        }}
        onMouseMove={handleMouseMove}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        whileTap={{ scale: 0.98 }}
      >
      {/* Multi-layer glassmorphism background system */}
      <div className="absolute inset-0 feature-card-backdrop rounded-3xl" />
      
      {/* Dynamic magnetic gradient overlay */}
      <motion.div
        className="absolute inset-0 rounded-3xl opacity-0"
        style={{
          background: `radial-gradient(circle at ${gradientX}% ${gradientY}%, ${
            feature.accentColor === 'green' 
              ? 'rgba(34, 197, 94, 0.15)' 
              : feature.accentColor === 'cyan'
              ? 'rgba(6, 182, 212, 0.15)'
              : feature.accentColor === 'red'
              ? 'rgba(239, 68, 68, 0.15)'
              : 'rgba(59, 130, 246, 0.15)' // fallback
          } 0%, transparent 70%)`
        }}
        animate={{ 
          opacity: isHovered ? 1 : 0,
        }}
        transition={{ duration: 0.3, ease: "easeOut" }}
      />
      
      {/* Advanced particle system overlay */}
      <div className="absolute inset-0 rounded-3xl overflow-hidden">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className={`absolute w-1 h-1 rounded-full opacity-0 ${
              feature.accentColor === 'green' 
                ? 'bg-green-400' 
                : feature.accentColor === 'cyan'
                ? 'bg-cyan-400'
                : feature.accentColor === 'red'
                ? 'bg-red-400'
                : 'bg-blue-400' // fallback
            }`}
            style={{
              left: `${20 + i * 12}%`,
              top: `${30 + Math.sin(i) * 20}%`,
            }}
            animate={isHovered ? {
              opacity: [0, 0.6, 0],
              scale: [0.5, 1.2, 0.5],
              y: [-20, -40, -20],
              transition: {
                duration: 2,
                repeat: Infinity,
                delay: i * 0.2,
                ease: "easeInOut"
              }
            } : {
              opacity: 0,
              scale: 0.5,
              y: -20
            }}
          />
        ))}
      </div>
      
      {/* Enhanced border glow with physics */}
      <motion.div 
        className="absolute inset-0 rounded-3xl border-2 border-transparent"
        style={{
          background: isHovered 
            ? `linear-gradient(135deg, ${
                feature.accentColor === 'green' 
                  ? 'rgba(34, 197, 94, 0.3)' 
                  : feature.accentColor === 'cyan'
                  ? 'rgba(6, 182, 212, 0.3)'
                  : feature.accentColor === 'red'
                  ? 'rgba(239, 68, 68, 0.3)'
                  : 'rgba(59, 130, 246, 0.3)' // fallback
              }, transparent 50%, ${
                feature.accentColor === 'green' 
                  ? 'rgba(34, 197, 94, 0.2)' 
                  : feature.accentColor === 'cyan'
                  ? 'rgba(6, 182, 212, 0.2)'
                  : feature.accentColor === 'red'
                  ? 'rgba(239, 68, 68, 0.2)'
                  : 'rgba(59, 130, 246, 0.2)' // fallback
              })` 
            : 'transparent'
        }}
        animate={{
          boxShadow: isHovered 
            ? `0 0 40px ${
                feature.accentColor === 'green' 
                  ? 'rgba(34, 197, 94, 0.25)' 
                  : feature.accentColor === 'cyan'
                  ? 'rgba(6, 182, 212, 0.25)'
                  : feature.accentColor === 'red'
                  ? 'rgba(239, 68, 68, 0.25)'
                  : 'rgba(59, 130, 246, 0.25)' // fallback
              }` 
            : '0 0 0 rgba(0, 0, 0, 0)'
        }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      />
      
      <div className="relative z-20 space-y-3 p-4 lg:p-5">
        {/* Revolutionary icon container with 3D transforms */}
        <motion.div 
          className="relative mx-auto w-12 h-12 lg:w-16 lg:h-16"
          animate={isHovered ? {
            rotateY: [0, 180, 360],
            scale: [1, 1.2, 1],
            transition: { duration: 1, ease: "easeInOut" }
          } : {}}
        >
          <motion.div 
            className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${
              feature.accentColor === 'green' 
                ? 'from-green-500/20 via-emerald-500/15 to-green-400/20' 
                : feature.accentColor === 'cyan'
                ? 'from-cyan-500/20 via-blue-500/15 to-cyan-400/20'
                : feature.accentColor === 'red'
                ? 'from-red-500/20 via-orange-500/15 to-red-400/20'
                : 'from-blue-500/20 via-indigo-500/15 to-purple-500/20' // fallback
            } backdrop-blur-sm border border-white/10`}
            animate={isHovered ? {
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0],
              transition: { duration: 0.8, ease: "easeInOut" }
            } : {}}
          />
          
          <motion.div 
            className="absolute inset-0 flex items-center justify-center text-2xl lg:text-3xl font-bold"
            animate={isHovered ? {
              scale: [1, 1.3, 1.1],
              transition: { duration: 0.6, ease: "backOut" }
            } : {}}
          >
            {feature.icon}
          </motion.div>
          
          {/* Icon glow effect */}
          <motion.div
            className={`absolute inset-0 rounded-2xl ${
              feature.accentColor === 'green' 
                ? 'bg-green-500' 
                : feature.accentColor === 'cyan'
                ? 'bg-cyan-500'
                : feature.accentColor === 'red'
                ? 'bg-red-500'
                : 'bg-blue-500' // fallback
            }`}
            animate={isHovered ? {
              opacity: [0, 0.3, 0],
              scale: [1, 1.4, 1.8],
              transition: { duration: 1.5, ease: "easeOut" }
            } : { opacity: 0 }}
          />
        </motion.div>
        
        <div className="space-y-2">
          <motion.div className="flex items-center justify-between">
            <motion.h3
              id={`feature-${index}-title`}
              className="font-black text-lg lg:text-xl text-fd-foreground tracking-tight leading-tight"
              animate={isHovered ? {
                scale: 1.05,
                letterSpacing: "0.02em",
                transition: { duration: 0.3, ease: "easeOut" }
              } : {
                scale: 1,
                letterSpacing: "normal"
              }}
            >
              {feature.title}
            </motion.h3>
            
            {/* Enhanced link indicator with physics */}
            <motion.div
              className="relative"
              animate={isHovered ? {
                x: [0, 8, 4],
                opacity: 1,
                transition: { duration: 0.4, ease: "easeOut" }
              } : {
                x: 0,
                opacity: 0.5
              }}
            >
              <motion.div
                animate={isHovered ? {
                  rotate: [0, 360],
                  transition: { duration: 1, ease: "easeInOut" }
                } : {}}
              >
                <LuArrowRight className="w-5 h-5 lg:w-6 lg:h-6 text-fd-muted-foreground" />
              </motion.div>
              
              {/* Arrow trail effect */}
              <motion.div
                className="absolute top-0 left-0"
                animate={isHovered ? {
                  x: [-20, 0],
                  opacity: [0, 0.5, 0],
                  transition: { duration: 0.6, ease: "easeOut" }
                } : { opacity: 0 }}
              >
                <LuArrowRight className="w-5 h-5 lg:w-6 lg:h-6 text-fd-muted-foreground" />
              </motion.div>
            </motion.div>
          </motion.div>
          
          <motion.p 
            className="text-fd-muted-foreground leading-relaxed text-sm lg:text-base font-medium"
            animate={isHovered ? {
              color: 'hsl(var(--foreground))',
              transition: { duration: 0.3 }
            } : {
              color: 'hsl(var(--muted-foreground))'
            }}
          >
            {feature.description}
          </motion.p>
        </div>
      </div>

      {/* Advanced floating sparkles constellation */}
      <div className="absolute top-4 right-4 w-6 h-6 z-30">
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute"
            style={{
              left: `${i * 8}px`,
              top: `${Math.sin(i) * 4}px`,
            }}
            animate={isHovered ? {
              scale: [0, 1.5, 0.8],
              rotate: [0, 180 + i * 60, 360],
              opacity: [0, 1, 0.7],
              transition: { 
                duration: 2, 
                delay: i * 0.2,
                repeat: Infinity,
                ease: "easeInOut"
              }
            } : { 
              scale: 0, 
              opacity: 0 
            }}
          >
            <LuSparkles className="w-3 h-3 text-fd-muted-foreground" />
          </motion.div>
        ))}
        
        {/* Main sparkle with electric effect */}
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
          animate={isHovered ? {
            scale: [1, 1.5, 1.2],
            rotate: [0, 360],
            transition: { duration: 1.5, ease: "easeInOut" }
          } : {}}
        >
          <LuZap className={`w-4 h-4 ${
            feature.accentColor === 'green' 
              ? 'text-green-400' 
              : feature.accentColor === 'cyan'
              ? 'text-cyan-400'
              : feature.accentColor === 'red'
              ? 'text-red-400'
              : 'text-blue-400' // fallback
          }`} />
        </motion.div>
      </div>
      
      {/* Sophisticated pattern overlay with depth */}
      <div className="absolute inset-0 rounded-3xl overflow-hidden z-10 pointer-events-none">
        <motion.div
          className="absolute inset-0 opacity-[0.02]"
          style={{
            backgroundImage: `radial-gradient(circle at 25% 25%, currentColor 2px, transparent 2px),
                             radial-gradient(circle at 75% 75%, currentColor 2px, transparent 2px)`,
            backgroundSize: '24px 24px'
          }}
          animate={isHovered ? {
            backgroundSize: '28px 28px',
            opacity: 0.04,
            transition: { duration: 0.4 }
          } : {
            backgroundSize: '24px 24px',
            opacity: 0.02
          }}
        />
      </div>
    </motion.article>
    </Link>
  );
}
