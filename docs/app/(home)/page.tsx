import Icon from 'public/img/icon.svg';
import { AnimatedBackground } from '@/components/ui/animated-background';
import { AnimatedLogo } from '@/components/ui/animated-logo';
import { AnimatedTitle } from '@/components/ui/animated-title';
import { FeatureCard } from '@/components/ui/feature-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { HeroSection, FeatureGrid, CTASection } from '@/components/ui/animated-sections';
import type { ReactNode } from 'react';
import { LuZap, LuShieldCheck, LuLayers, LuArrowRight, LuGithub, LuSparkles, LuTerminal, LuBrainCircuit, LuDatabase, LuActivity } from 'react-icons/lu';
import { cn } from '@/lib/utils';
import styles from './styles.module.css';

// Enhanced data configuration with elite hacker approach
const BRAND_CONFIG = {
  name: 'proxywhirl',
  tagline: 'rotating proxy system',
} as const;

type Feature = {
  icon: ReactNode;
  title: string;
  description: string;
  gradient: string;
  accentColor: string;
  href: string;
};

const FEATURES: Feature[] = [
  {
    icon: <LuTerminal className="feature-icon" />,
    title: 'Multiple Interfaces',
    description: 'Use it from the command line, import it in Python, or fire up the interactive TUI. Whatever floats your boat.',
    gradient: 'from-green-500/25 via-emerald-500/20 to-green-400/25',
    accentColor: 'green',
    href: '/docs/cli',
  },
  {
    icon: <LuBrainCircuit className="feature-icon" />,
    title: 'Smart Collection, Validation, Rotation',
    description: 'Finds proxies, checks if they actually work, and rotates them when they inevitably break. Like a responsible adult.',
    gradient: 'from-cyan-500/25 via-blue-500/20 to-cyan-400/25',
    accentColor: 'cyan',
    href: '/docs/usage#validation',
  },
  {
    icon: <LuDatabase className="feature-icon" />,
    title: 'Multiple Caches, List Exports, Health Reports',
    description: 'Save your proxies to memory, files, or SQLite. Export them however you want. Get reports on which ones are actually worth using.',
    gradient: 'from-purple-500/25 via-violet-500/20 to-purple-400/25',
    accentColor: 'purple',
    href: '/docs/usage#caching',
  },
];

type ActionButton = {
  href: string;
  label: string;
  ariaLabel: string;
  external?: boolean;
  variant: 'primary' | 'secondary';
  icon: ReactNode;
  iconPosition?: 'left' | 'right';
};

const ACTION_BUTTONS: ActionButton[] = [
  {
    href: '/docs',
    label: 'Get Started',
    ariaLabel: 'Get started with proxywhirl documentation',
    variant: 'primary',
    icon: <LuArrowRight className="w-5 h-5 lg:w-6 lg:h-6" />,
  },
  {
    href: 'https://github.com/wyattowalsh/proxywhirl',
    label: 'View on GitHub',
    ariaLabel: 'View proxywhirl source code on GitHub (opens in new tab)',
    external: true,
    variant: 'secondary',
    icon: <LuGithub className="w-5 h-5 lg:w-6 lg:h-6" />,
    iconPosition: 'left',
  },
];

export default function HomePage() {
  return (
    <div className={cn(
      styles.landingPageContainer,
      'landing-page-container relative min-h-screen overflow-hidden',
      // Enhanced background with sophisticated gradients
      'bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900',
      'dark:from-black dark:via-gray-950 dark:to-black',
      // Glass morphism base layer
      'backdrop-blur-3xl',
      // Responsive layout
      'flex flex-col lg:min-h-screen'
    )}>
      
      {/* Revolutionary Multi-Layer Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Primary animated background component */}
        <AnimatedBackground />
        
        {/* Enhanced grid overlay with brand colors */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.03)_1px,transparent_1px)] bg-[size:60px_60px] [mask-image:radial-gradient(ellipse_at_center,black_50%,transparent_80%)]" />
        
        {/* Cyber-themed hacker background effects with enhanced animations */}
        <div className="absolute inset-0">
          {/* Enhanced cyber-themed data extraction background effects */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,65,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,65,0.02)_1px,transparent_1px)] bg-[size:40px_40px] animate-pulse opacity-40" />
          <div className="absolute inset-0 bg-[linear-gradient(rgba(0,210,239,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(0,210,239,0.015)_1px,transparent_1px)] bg-[size:80px_80px] animate-pulse opacity-30" style={{animationDelay: '1s'}} />
          
          {/* Enhanced proxy network visualization orbs with better responsivity */}
          <div className="absolute top-[10%] left-[10%] sm:top-[15%] sm:left-[15%] lg:top-1/6 lg:left-1/5 w-48 h-48 sm:w-64 sm:h-64 lg:w-80 lg:h-80 bg-gradient-to-br from-blue-500/5 via-blue-400/3 to-transparent rounded-full blur-3xl animate-float" />
          <div className="absolute bottom-[10%] right-[10%] sm:bottom-[15%] sm:right-[15%] lg:bottom-1/6 lg:right-1/5 w-48 h-48 sm:w-64 sm:h-64 lg:w-80 lg:h-80 bg-gradient-to-br from-cyan-500/5 via-cyan-400/3 to-transparent rounded-full blur-3xl animate-float" style={{animationDelay: '1.5s'}} />
          <div className="absolute top-[25%] right-[15%] sm:top-1/3 sm:right-1/6 lg:top-1/3 lg:right-1/6 w-32 h-32 sm:w-48 sm:h-48 lg:w-64 lg:h-64 bg-gradient-to-br from-purple-500/6 via-purple-400/4 to-transparent rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-[25%] left-[15%] sm:bottom-1/3 sm:left-1/6 lg:bottom-1/3 lg:left-1/6 w-56 h-56 sm:w-72 sm:h-72 lg:w-96 lg:h-96 bg-gradient-to-br from-indigo-500/3 via-indigo-400/2 to-transparent rounded-full blur-3xl animate-pulse-slow" style={{animationDelay: '2.5s'}} />
          
          {/* Data extraction scanning lines with proxy status colors - responsive */}
          <div className="absolute inset-0 overflow-hidden opacity-20">
            <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-green-400/30 to-transparent animate-scan-line" />
            <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-cyan-400/25 to-transparent animate-scan-line-slow top-1/3" style={{animationDelay: '1s'}} />
            <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-purple-400/35 to-transparent top-2/3" style={{animationDelay: '3s', animation: 'scan-line-elite 8s linear infinite'}} />
          </div>
        </div>

        {/* Enhanced terminal status indicators - responsive positioning */}
        <div className="hidden md:block">
          <div className="absolute top-4 left-4 w-8 h-8 lg:w-12 lg:h-12 border-l-2 border-t-2 border-green-400/40 animate-pulse" />
          <div className="absolute top-4 right-4 w-8 h-8 lg:w-12 lg:h-12 border-r-2 border-t-2 border-cyan-400/40 animate-pulse" style={{animationDelay: '0.5s'}} />
          <div className="absolute bottom-4 left-4 w-8 h-8 lg:w-12 lg:h-12 border-l-2 border-b-2 border-purple-400/40 animate-glow-pulse" />
          <div className="absolute bottom-4 right-4 w-8 h-8 lg:w-12 lg:h-12 border-r-2 border-b-2 border-green-400/40 animate-pulse" style={{animationDelay: '1.5s'}} />
        </div>

        {/* Enhanced matrix rain effect - mobile optimized */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-10">
          {Array.from({length: 8}).map((_, i) => (
            <div
              key={i}
              className={cn(
                'absolute text-green-400/30 text-xs font-mono leading-4',
                'hidden sm:block', // Hide on mobile for performance
                'animate-matrix-rain'
              )}
              style={{
                left: `${i * 12.5}%`,
                animationDelay: `${i * 0.7}s`,
                animationDuration: `${10 + i * 1.5}s`
              }}
            >
              {Array.from({length: 20}).map((_, j) => (
                <div key={j} className="h-4">
                  {j % 4 === 0 ? 'ELITE' : j % 4 === 1 ? '200' : j % 4 === 2 ? 'OK' : Math.random() > 0.7 ? '1' : '0'}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Enhanced Content with Sophisticated Layout and Container Queries */}
      <main className={cn(
        'relative z-10 flex flex-col justify-center items-center text-center',
        'px-4 sm:px-6 lg:px-8 xl:px-12',
        'max-w-7xl mx-auto w-full',
        'py-8 sm:py-12 md:py-16 lg:py-20',
        'gap-12 sm:gap-16 lg:gap-20',
        // Responsive height management
        'min-h-[calc(100vh-4rem)] lg:min-h-screen lg:justify-center'
      )}>
        
        {/* Enhanced terminal-style header with proxy status - better responsive behavior */}
        <div className="absolute top-4 left-4 text-green-400/80 text-xs font-mono hidden lg:block">
          <div className="flex items-center gap-2 glass-effect px-3 py-2 rounded-lg border border-green-400/20">
            <LuTerminal className="w-3 h-3" />
            <span className="text-green-400">root@proxywhirl:~#</span>
            <span className="animate-pulse text-green-300">_</span>
          </div>
        </div>
        
        {/* Enhanced proxy status indicator with better mobile layout */}
        <div className="absolute top-4 right-4 hidden lg:flex items-center gap-3 glass-effect px-3 py-2 rounded-lg border border-cyan-400/20">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-sm shadow-green-400/50"></div>
            <span className="text-green-400/90 text-xs font-mono">PROXIES ONLINE</span>
          </div>
          <div className="w-px h-4 bg-gray-600/30"></div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-glow-pulse shadow-sm shadow-purple-400/50"></div>
            <span className="text-purple-400/90 text-xs font-mono">ELITE</span>
          </div>
          <LuActivity className="w-3 h-3 text-cyan-400/70" />
        </div>
        
        {/* Hero Section with Advanced Motion Typography and Container Queries */}
        <HeroSection className="space-y-8 sm:space-y-12 lg:space-y-16">
          {/* Enhanced Logo with Sophisticated Effects and Responsive Sizing */}
          <div className="relative group">
            <AnimatedLogo
              src={Icon}
              alt={`${BRAND_CONFIG.name} Logo — Python rotating proxies library`}
              width={80}
              height={80}
              className="w-16 h-16 sm:w-20 sm:h-20 md:w-24 md:h-24 lg:w-28 lg:h-28 xl:w-32 xl:h-32"
            />
            {/* Logo glow effect */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-cyan-500/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          </div>

          {/* Revolutionary Title System with Advanced Typography and Responsive Scaling */}
          <AnimatedTitle
            title={BRAND_CONFIG.name}
            subtitle={BRAND_CONFIG.tagline}
            className="space-y-3 sm:space-y-4"
          />
        </HeroSection>

        {/* Enhanced Feature Grid with Sophisticated Cards and Container Queries */}
        <FeatureGrid className={cn(
          'w-full max-w-6xl',
          'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8',
          // Container queries for advanced responsive design
          '@container',
        )}>
          {FEATURES.map((feature, index) => (
            <div
              key={feature.title}
              className="@[400px]:col-span-1"
              style={{ 
                animationDelay: `${index * 0.15}s`,
                animation: 'fadeInUp 0.8s ease-out forwards'
              }}
            >
              <FeatureCard
                feature={{
                  ...feature,
                  // Enhanced gradients with better contrast
                  gradient: index === 0 
                    ? 'from-green-500/10 via-emerald-500/5 to-green-400/10' 
                    : index === 1 
                    ? 'from-cyan-500/10 via-blue-500/5 to-cyan-400/10'
                    : 'from-purple-500/10 via-violet-500/5 to-purple-400/10'
                }}
                index={index}
                className={cn(
                  'h-full group relative overflow-hidden',
                  'glass-effect border border-white/10',
                  'hover:border-white/20 hover:shadow-2xl',
                  'transition-all duration-500 ease-out',
                  'hover:scale-[1.02] hover:-translate-y-1'
                )}
              />
            </div>
          ))}
        </FeatureGrid>

        {/* Revolutionary CTA Section with Advanced Interactions and Better Mobile UX */}
        <CTASection className={cn(
          'w-full max-w-2xl space-y-8 sm:space-y-10',
          'pt-8 sm:pt-12'
        )}>
          <div className={cn(
            'flex flex-col sm:flex-row items-center justify-center',
            'gap-4 sm:gap-6 w-full'
          )}>
            {ACTION_BUTTONS.map((button, index) => (
              <div
                key={button.href}
                style={{ 
                  animationDelay: `${0.5 + index * 0.1}s`,
                  animation: 'fadeInUp 0.8s ease-out forwards'
                }}
                className="w-full sm:w-auto"
              >
                <AnimatedButton
                  href={button.href}
                  label={button.label}
                  ariaLabel={button.ariaLabel}
                  external={button.external}
                  variant={button.variant}
                  icon={button.icon}
                  iconPosition={button.iconPosition}
                  className={cn(
                    'w-full sm:w-auto min-w-[200px]',
                    'px-6 py-3 sm:px-8 sm:py-4',
                    'text-sm sm:text-base font-semibold',
                    'transition-all duration-300',
                    button.variant === 'primary' 
                      ? cn(
                          'bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600',
                          'hover:from-blue-500 hover:via-purple-500 hover:to-cyan-500',
                          'text-white border-transparent',
                          'shadow-lg hover:shadow-2xl',
                          'hover:shadow-blue-500/25'
                        )
                      : cn(
                          'glass-effect border border-white/20',
                          'hover:border-white/40 text-white',
                          'hover:bg-white/5'
                        )
                  )}
                />
              </div>
            ))}
          </div>
        </CTASection>
      </main>
    </div>
  );
}
