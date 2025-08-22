'use client';

import { useEffect, useState, useCallback, useMemo } from 'react';

interface ParticleProps {
  id: number;
  size: 'sm' | 'md' | 'lg';
  color: 'blue' | 'purple' | 'cyan' | 'indigo';
}

function FloatingParticle({ id, size, color }: ParticleProps) {
  const [style, setStyle] = useState<React.CSSProperties>({});

  const sizeClasses = {
    sm: 'w-1 h-1',
    md: 'w-2 h-2', 
    lg: 'w-3 h-3'
  };

  const colorClasses = {
    blue: 'bg-blue-400/20 dark:bg-blue-400/10',
    purple: 'bg-purple-400/20 dark:bg-purple-400/10',
    cyan: 'bg-cyan-400/20 dark:bg-cyan-400/10',
    indigo: 'bg-indigo-400/20 dark:bg-indigo-400/10'
  };

  useEffect(() => {
    setStyle({
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      animationDelay: `${Math.random() * 10}s`,
      animationDuration: `${6 + Math.random() * 8}s`
    });
  }, []);

  return (
    <div
      className={`absolute rounded-full animate-float blur-sm ${sizeClasses[size]} ${colorClasses[color]}`}
      style={style}
    />
  );
}

function GradientOrb({ 
  className, 
  size, 
  colors, 
  animation,
  blur = 'blur-3xl' 
}: {
  className: string;
  size: string;
  colors: string;
  animation: string;
  blur?: string;
}) {
  return (
    <div 
      className={`absolute ${size} bg-gradient-to-r ${colors} rounded-full ${blur} ${animation} ${className}`}
    />
  );
}

export function AnimatedBackground() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Generate particles with variety
  const particles = useMemo(() => {
    const particleConfigs: ParticleProps[] = [];
    const sizes: ParticleProps['size'][] = ['sm', 'md', 'lg'];
    const colors: ParticleProps['color'][] = ['blue', 'purple', 'cyan', 'indigo'];
    
    for (let i = 0; i < 30; i++) {
      particleConfigs.push({
        id: i,
        size: sizes[Math.floor(Math.random() * sizes.length)],
        color: colors[Math.floor(Math.random() * colors.length)]
      });
    }
    
    return particleConfigs;
  }, []);

  if (!mounted) {
    return (
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-cyan-50 dark:from-blue-950/20 dark:via-purple-950/20 dark:to-cyan-950/20" />
    );
  }

  return (
    <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-cyan-50 dark:from-blue-950/20 dark:via-purple-950/20 dark:to-cyan-950/20">
      {/* Floating Particles */}
      <div className="absolute inset-0 overflow-hidden">
        {particles.map((particle) => (
          <FloatingParticle 
            key={particle.id} 
            id={particle.id}
            size={particle.size}
            color={particle.color}
          />
        ))}
      </div>
      
      {/* Primary Gradient Orbs */}
      <GradientOrb
        className="top-1/4 left-1/4"
        size="w-72 h-72 lg:w-96 lg:h-96"
        colors="from-blue-500/15 via-indigo-500/10 to-purple-500/15"
        animation="animate-pulse-slow"
        blur="blur-3xl"
      />
      
      <GradientOrb
        className="bottom-1/4 right-1/4"
        size="w-80 h-80 lg:w-[28rem] lg:h-[28rem]"
        colors="from-cyan-400/15 via-teal-400/10 to-blue-500/15"
        animation="animate-pulse-slow-delayed"
        blur="blur-3xl"
      />
      
      {/* Central Rotating Orb */}
      <GradientOrb
        className="top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
        size="w-[32rem] h-[32rem] lg:w-[40rem] lg:h-[40rem]"
        colors="from-purple-400/8 via-fuchsia-400/5 to-cyan-400/8"
        animation="animate-spin-slow"
        blur="blur-3xl"
      />
      
      {/* Secondary Accent Orbs */}
      <GradientOrb
        className="top-0 right-0"
        size="w-64 h-64"
        colors="from-violet-400/10 to-purple-500/10"
        animation="animate-pulse-slow animate-delay-100"
        blur="blur-2xl"
      />
      
      <GradientOrb
        className="bottom-0 left-0"
        size="w-56 h-56"
        colors="from-indigo-400/10 to-cyan-500/10"
        animation="animate-pulse-slow animate-delay-300"
        blur="blur-2xl"
      />
      
      {/* Mesh Gradient Overlay for Depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-transparent dark:via-black/5 pointer-events-none" />
      
      {/* Noise Texture for Visual Interest */}
      <div 
        className="absolute inset-0 opacity-[0.015] dark:opacity-[0.02] pointer-events-none"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`,
        }}
      />
    </div>
  );
} 