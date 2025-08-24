'use client';

import { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { motion, useMotionValue, useSpring } from 'motion/react';

interface ParticleProps {
  id: number;
  size: 'sm' | 'md' | 'lg' | 'xl';
  color: 'blue' | 'purple' | 'cyan' | 'indigo' | 'emerald' | 'rose';
  variant?: 'glow' | 'solid' | 'gradient';
}

interface CursorPosition {
  x: number;
  y: number;
}

function FloatingParticle({ id, size, color, variant = 'glow' }: ParticleProps) {
  const [style, setStyle] = useState<React.CSSProperties>({});
  const [magneticOffset, setMagneticOffset] = useState({ x: 0, y: 0 });

  const sizeClasses = {
    sm: 'w-1 h-1',
    md: 'w-2 h-2', 
    lg: 'w-3 h-3',
    xl: 'w-4 h-4'
  };

  const colorClasses = {
    blue: 'bg-blue-400/30 dark:bg-blue-400/20',
    purple: 'bg-purple-400/30 dark:bg-purple-400/20',
    cyan: 'bg-cyan-400/30 dark:bg-cyan-400/20',
    indigo: 'bg-indigo-400/30 dark:bg-indigo-400/20',
    emerald: 'bg-emerald-400/30 dark:bg-emerald-400/20',
    rose: 'bg-rose-400/30 dark:bg-rose-400/20'
  };

  const glowClasses = {
    blue: 'shadow-lg shadow-blue-400/50 dark:shadow-blue-400/30',
    purple: 'shadow-lg shadow-purple-400/50 dark:shadow-purple-400/30',
    cyan: 'shadow-lg shadow-cyan-400/50 dark:shadow-cyan-400/30',
    indigo: 'shadow-lg shadow-indigo-400/50 dark:shadow-indigo-400/30',
    emerald: 'shadow-lg shadow-emerald-400/50 dark:shadow-emerald-400/30',
    rose: 'shadow-lg shadow-rose-400/50 dark:shadow-rose-400/30'
  };

  useEffect(() => {
    const initialX = Math.random() * 100;
    const initialY = Math.random() * 100;
    const duration = 8 + Math.random() * 12;
    const delay = Math.random() * 10;

    setStyle({
      left: `${initialX}%`,
      top: `${initialY}%`,
      animationDelay: `${delay}s`,
      animationDuration: `${duration}s`,
      transform: `translate(${magneticOffset.x}px, ${magneticOffset.y}px)`
    });
  }, [magneticOffset]);

  const baseClasses = `absolute rounded-full transition-all duration-300 ease-out ${sizeClasses[size]} ${colorClasses[color]}`;
  const variantClasses = variant === 'glow' ? `${glowClasses[color]} blur-sm` : 'blur-sm';
  const animationClasses = 'animate-float hover:animate-pulse';

  return (
    <motion.div
      className={`${baseClasses} ${variantClasses} ${animationClasses}`}
      style={style}
      whileHover={{ scale: 1.5, opacity: 0.8 }}
      transition={{ type: "spring", stiffness: 400, damping: 10 }}
    />
  );
}

function GradientOrb({ 
  className, 
  size, 
  colors, 
  animation,
  blur = 'blur-3xl',
  opacity = 'opacity-100' 
}: {
  className: string;
  size: string;
  colors: string;
  animation: string;
  blur?: string;
  opacity?: string;
}) {
  return (
    <motion.div 
      className={`absolute ${size} bg-gradient-to-r ${colors} rounded-full ${blur} ${animation} ${className} ${opacity} transition-all duration-700`}
      whileHover={{ scale: 1.1, opacity: 0.8 }}
      transition={{ type: "spring", stiffness: 100, damping: 15 }}
    />
  );
}

function MagneticOrb({ 
  position,
  size = 'w-32 h-32',
  colors = 'from-blue-500/20 to-purple-500/20',
  blur = 'blur-2xl'
}: {
  position: { x: string; y: string };
  size?: string;
  colors?: string;
  blur?: string;
}) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  
  const springX = useSpring(x, { stiffness: 150, damping: 15 });
  const springY = useSpring(y, { stiffness: 150, damping: 15 });

  return (
    <motion.div
      className={`absolute ${size} bg-gradient-to-r ${colors} rounded-full ${blur} pointer-events-none`}
      style={{
        left: position.x,
        top: position.y,
        x: springX,
        y: springY,
      }}
      whileHover={{ scale: 1.2 }}
    />
  );
}

export function AnimatedBackground() {
  const [mounted, setMounted] = useState(false);
  const [cursorPosition, setCursorPosition] = useState<CursorPosition>({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Enhanced cursor tracking for magnetic effects
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setCursorPosition({
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
        });
      }
    };

    if (mounted) {
      window.addEventListener('mousemove', handleMouseMove);
      return () => window.removeEventListener('mousemove', handleMouseMove);
    }
  }, [mounted]);

  // Enhanced particles with more variety
  const particles = useMemo(() => {
    const particleConfigs: ParticleProps[] = [];
    const sizes: ParticleProps['size'][] = ['sm', 'md', 'lg', 'xl'];
    const colors: ParticleProps['color'][] = ['blue', 'purple', 'cyan', 'indigo', 'emerald', 'rose'];
    const variants: ParticleProps['variant'][] = ['glow', 'solid', 'gradient'];
    
    for (let i = 0; i < 45; i++) {
      particleConfigs.push({
        id: i,
        size: sizes[Math.floor(Math.random() * sizes.length)],
        color: colors[Math.floor(Math.random() * colors.length)],
        variant: variants[Math.floor(Math.random() * variants.length)]
      });
    }
    
    return particleConfigs;
  }, []);

  if (!mounted) {
    return (
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-purple-50/50 to-cyan-50/50 dark:from-blue-950/30 dark:via-purple-950/30 dark:to-cyan-950/30" />
    );
  }

  return (
    <div 
      ref={containerRef}
      className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-purple-50/50 to-cyan-50/50 dark:from-blue-950/30 dark:via-purple-950/30 dark:to-cyan-950/30 overflow-hidden"
    >
      {/* Enhanced Floating Particles with Motion */}
      <div className="absolute inset-0 overflow-hidden">
        {particles.map((particle) => (
          <FloatingParticle 
            key={particle.id} 
            id={particle.id}
            size={particle.size}
            color={particle.color}
            variant={particle.variant}
          />
        ))}
      </div>
      
      {/* Enhanced Primary Gradient Orbs with Motion */}
      <GradientOrb
        className="top-1/4 left-1/4"
        size="w-80 h-80 lg:w-[28rem] lg:h-[28rem]"
        colors="from-blue-500/20 via-indigo-500/15 to-purple-500/20"
        animation="animate-pulse-slow"
        blur="blur-3xl"
        opacity="opacity-90"
      />
      
      <GradientOrb
        className="bottom-1/4 right-1/4"
        size="w-96 h-96 lg:w-[32rem] lg:h-[32rem]"
        colors="from-cyan-400/20 via-teal-400/15 to-blue-500/20"
        animation="animate-pulse-slow-delayed"
        blur="blur-3xl"
        opacity="opacity-85"
      />
      
      {/* Enhanced Central Rotating Orb */}
      <motion.div
        className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[36rem] h-[36rem] lg:w-[48rem] lg:h-[48rem]"
        animate={{ rotate: 360 }}
        transition={{ duration: 50, repeat: Infinity, ease: "linear" }}
      >
        <div className="w-full h-full bg-gradient-to-r from-purple-400/12 via-fuchsia-400/8 to-cyan-400/12 rounded-full blur-3xl opacity-80" />
      </motion.div>
      
      {/* Dynamic Magnetic Orbs */}
      <MagneticOrb
        position={{ x: '10%', y: '20%' }}
        size="w-24 h-24 lg:w-32 lg:h-32"
        colors="from-violet-400/15 to-purple-500/15"
        blur="blur-2xl"
      />
      
      <MagneticOrb
        position={{ x: '85%', y: '75%' }}
        size="w-28 h-28 lg:w-36 lg:h-36"
        colors="from-indigo-400/15 to-cyan-500/15"
        blur="blur-2xl"
      />
      
      <MagneticOrb
        position={{ x: '70%', y: '15%' }}
        size="w-20 h-20 lg:w-28 lg:h-28"
        colors="from-emerald-400/15 to-teal-500/15"
        blur="blur-2xl"
      />
      
      {/* Enhanced Mesh Gradient Overlays */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/8 to-transparent dark:via-black/8 pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-tl from-blue-500/5 via-transparent to-purple-500/5 dark:from-blue-500/10 dark:to-purple-500/10 pointer-events-none" />
      
      {/* Enhanced Noise Texture with Animation */}
      <motion.div 
        className="absolute inset-0 opacity-[0.02] dark:opacity-[0.04] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='6' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
        animate={{ opacity: [0.02, 0.05, 0.02] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      
      {/* Glass Morphism Overlay */}
      <div className="absolute inset-0 backdrop-blur-[0.5px] pointer-events-none" />
    </div>
  );
} 