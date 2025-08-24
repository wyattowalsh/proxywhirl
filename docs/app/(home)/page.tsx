import Icon from 'public/img/icon.svg';
import { AnimatedBackground } from '@/components/ui/animated-background';
import { AnimatedLogo } from '@/components/ui/animated-logo';
import { AnimatedTitle } from '@/components/ui/animated-title';
import { FeatureCard } from '@/components/ui/feature-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { HeroSection, FeatureGrid, CTASection } from '@/components/ui/animated-sections';
import type { ReactNode } from 'react';
import { LuZap, LuShieldCheck, LuLayers, LuArrowRight, LuGithub, LuSparkles, LuTerminal, LuBrainCircuit, LuDatabase } from 'react-icons/lu';

// Enhanced data configuration with hacker-inspired approach
const BRAND_CONFIG = {
  name: 'proxywhirl',
  tagline: 'Data Extraction Arsenal',
  description: 'Elite-grade Python proxy rotation system engineered for high-stakes web data extraction, reconnaissance, and intelligence gathering operations.',
  version: '2.0',
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
    description: 'Command-line interface, Python API, and interactive terminal UI for seamless proxy management across all environments.',
    gradient: 'from-green-500/25 via-emerald-500/20 to-green-400/25',
    accentColor: 'green',
    href: '/docs/cli',
  },
  {
    icon: <LuBrainCircuit className="feature-icon" />,
    title: 'Smart Operations',
    description: 'Intelligent collection, comprehensive validation, and adaptive rotation with health scoring and circuit breaker protection.',
    gradient: 'from-cyan-500/25 via-blue-500/20 to-cyan-400/25',
    accentColor: 'cyan',
    href: '/docs/usage#validation',
  },
  {
    icon: <LuDatabase className="feature-icon" />,
    title: 'Data Management',
    description: 'Multiple cache backends, flexible list exports, and comprehensive health reports for production monitoring.',
    gradient: 'from-red-500/25 via-orange-500/20 to-red-400/25',
    accentColor: 'red',
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
    <div className="landing-page-container relative bg-black flex flex-col md:h-screen md:max-h-screen md:overflow-hidden">
      {/* Revolutionary Animated Background */}
      <AnimatedBackground />
      
      {/* Cyber-themed hacker background effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Matrix-style grid overlay */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,0,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,0,0.03)_1px,transparent_1px)] bg-[size:50px_50px] animate-pulse" />
        
        {/* Neon glow orbs with hacker colors */}
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-green-500/8 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-cyan-500/8 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}} />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-radial from-red-500/5 to-transparent rounded-full blur-2xl" />
        
        {/* Digital scanning lines */}
        <div className="absolute inset-0">
          <div className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-green-400/20 to-transparent animate-scan-line" />
          <div className="absolute w-full h-0.5 bg-gradient-to-r from-transparent via-cyan-400/15 to-transparent animate-scan-line-slow" style={{animationDelay: '2s'}} />
        </div>
        
        {/* Matrix rain effect */}
        <div className="absolute inset-0 overflow-hidden">
          {Array.from({length: 20}).map((_, i) => (
            <div
              key={i}
              className="absolute text-green-400/20 text-xs terminal-text animate-matrix-rain"
              style={{
                left: `${i * 5}%`,
                animationDelay: `${i * 0.5}s`,
                animationDuration: `${8 + i * 2}s`
              }}
            >
              {Array.from({length: 30}).map((_, j) => (
                <div key={j} className="h-4">
                  {Math.random() > 0.5 ? '1' : '0'}
                </div>
              ))}
            </div>
          ))}
        </div>
        
        {/* Corner brackets for terminal feel */}
        <div className="absolute top-4 left-4 w-12 h-12 border-l-2 border-t-2 border-green-400/30" />
        <div className="absolute top-4 right-4 w-12 h-12 border-r-2 border-t-2 border-green-400/30" />
        <div className="absolute bottom-4 left-4 w-12 h-12 border-l-2 border-b-2 border-green-400/30" />
        <div className="absolute bottom-4 right-4 w-12 h-12 border-r-2 border-b-2 border-green-400/30" />
      </div>

      {/* Enhanced Content with Sophisticated Layout */}
      <main className="relative z-10 flex flex-col justify-center items-center text-center px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto py-4 sm:py-6 md:py-8 md:min-h-0 md:flex-1 md:overflow-hidden">
        
        {/* Terminal-style header */}
        <div className="absolute top-4 left-4 text-green-400/60 text-xs terminal-text hidden md:block">
          <div className="flex items-center gap-2">
            <span className="text-green-400">root@proxywhirl:~#</span>
            <span className="animate-pulse">_</span>
          </div>
        </div>
        
        {/* Status indicator */}
        <div className="absolute top-4 right-20 md:right-24 text-green-400/60 text-xs terminal-text hidden md:flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span>SYSTEM ONLINE</span>
        </div>
        
        {/* Hero Section with Advanced Motion Typography */}
        <HeroSection>
          {/* Enhanced Logo with Sophisticated Effects */}
          <AnimatedLogo
            src={Icon}
            alt={`${BRAND_CONFIG.name} Logo — Python rotating proxies library v${BRAND_CONFIG.version}`}
            width={120}
            height={120}
          />

          {/* Revolutionary Title System with Advanced Typography */}
          <AnimatedTitle
            title={BRAND_CONFIG.name}
            subtitle={BRAND_CONFIG.tagline}
            description={BRAND_CONFIG.description}
          />
        </HeroSection>

        {/* Enhanced Feature Grid with Sophisticated Cards */}
        <FeatureGrid>
          {FEATURES.map((feature, index) => (
            <FeatureCard
              key={feature.title}
              feature={feature}
              index={index}
            />
          ))}
        </FeatureGrid>

        {/* Revolutionary CTA Section with Advanced Interactions */}
        <CTASection>
          {ACTION_BUTTONS.map((button, index) => (
            <AnimatedButton
              key={button.href}
              href={button.href}
              label={button.label}
              ariaLabel={button.ariaLabel}
              external={button.external}
              variant={button.variant}
              icon={button.icon}
              iconPosition={button.iconPosition}
            />
          ))}
        </CTASection>
      </main>
    </div>
  );
}
