import Icon from 'public/img/icon.svg';
import { AnimatedBackground } from '@/components/ui/animated-background';
import { AnimatedLogo } from '@/components/ui/animated-logo';
import { AnimatedTitle } from '@/components/ui/animated-title';
import { FeatureCard } from '@/components/ui/feature-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { HeroSection, FeatureGrid, CTASection } from '@/components/ui/animated-sections';
import type { ReactNode } from 'react';
import { LuZap, LuShieldCheck, LuLayers, LuArrowRight, LuGithub, LuSparkles, LuTerminal, LuBrainCircuit, LuDatabase } from 'react-icons/lu';

// Enhanced data configuration with elite hacker approach
const BRAND_CONFIG = {
  name: 'proxywhirl',
  tagline: 'collect, validate, and rotate proxies',
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
    <div className="landing-page-container relative bg-black flex flex-col md:h-screen md:max-h-screen md:overflow-hidden">
      {/* Revolutionary Animated Background */}
      <AnimatedBackground />
      
      {/* Cyber-themed hacker background effects */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {/* Enhanced cyber-themed data extraction background effects */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,255,65,0.04)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,65,0.04)_1px,transparent_1px)] bg-[size:40px_40px] animate-pulse" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,210,239,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,210,239,0.02)_1px,transparent_1px)] bg-[size:80px_80px] animate-pulse" style={{animationDelay: '1s'}} />
        
        {/* Proxy network visualization orbs */}
        <div className="absolute top-1/6 left-1/5 w-80 h-80 bg-[hsl(var(--pw-proxy-healthy)_/_6%)] rounded-full blur-3xl animate-proxy-pulse" />
        <div className="absolute bottom-1/6 right-1/5 w-80 h-80 bg-[hsl(var(--pw-console-cyan)_/_6%)] rounded-full blur-3xl animate-proxy-pulse" style={{animationDelay: '1.5s'}} />
        <div className="absolute top-1/3 right-1/6 w-64 h-64 bg-[hsl(var(--pw-proxy-elite)_/_8%)] rounded-full blur-3xl animate-elite-glow" />
        <div className="absolute bottom-1/3 left-1/6 w-96 h-96 bg-[hsl(var(--pw-proxy-error)_/_4%)] rounded-full blur-3xl animate-proxy-pulse" style={{animationDelay: '2.5s'}} />
        
        {/* Data extraction scanning lines with proxy status colors */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-[hsl(var(--pw-proxy-healthy)_/_25%)] to-transparent animate-scan-line" />
          <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-[hsl(var(--pw-console-cyan)_/_20%)] to-transparent animate-scan-line-slow top-1/3" style={{animationDelay: '1s'}} />
          <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-[hsl(var(--pw-proxy-elite)_/_30%)] to-transparent animate-scan-line-elite top-2/3" style={{animationDelay: '3s'}} />
        </div>
        
        {/* Enhanced matrix rain with proxy data simulation */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {Array.from({length: 16}).map((_, i) => (
            <div
              key={i}
              className="absolute text-[hsl(var(--pw-console-green)_/_20%)] text-xs terminal-text animate-matrix-rain"
              style={{
                left: `${i * 6.25}%`,
                animationDelay: `${i * 0.7}s`,
                animationDuration: `${10 + i * 1.5}s`
              }}
            >
              {Array.from({length: 25}).map((_, j) => (
                <div key={j} className="h-4">
                  {j % 4 === 0 ? 'ELITE' : j % 4 === 1 ? '200' : j % 4 === 2 ? 'OK' : Math.random() > 0.7 ? '1' : '0'}
                </div>
              ))}
            </div>
          ))}
        </div>
        
        {/* Terminal status indicators */}
        <div className="absolute top-4 left-4 w-12 h-12 border-l-2 border-t-2 border-[hsl(var(--pw-proxy-healthy)_/_40%)] animate-proxy-pulse" />
        <div className="absolute top-4 right-4 w-12 h-12 border-r-2 border-t-2 border-[hsl(var(--pw-console-cyan)_/_40%)] animate-proxy-pulse" style={{animationDelay: '0.5s'}} />
        <div className="absolute bottom-4 left-4 w-12 h-12 border-l-2 border-b-2 border-[hsl(var(--pw-proxy-elite)_/_40%)] animate-elite-glow" />
        <div className="absolute bottom-4 right-4 w-12 h-12 border-r-2 border-b-2 border-[hsl(var(--pw-proxy-healthy)_/_40%)] animate-proxy-pulse" style={{animationDelay: '1.5s'}} />
      </div>

      {/* Enhanced Content with Sophisticated Layout */}
      <main className="relative z-10 flex flex-col justify-center items-center text-center px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto py-4 sm:py-6 md:py-8 md:min-h-0 md:flex-1 md:overflow-hidden">
        
        {/* Enhanced terminal-style header with proxy status */}
        <div className="absolute top-4 left-4 text-[hsl(var(--pw-console-green))] text-xs terminal-text hidden md:block">
          <div className="flex items-center gap-2">
            <span className="text-[hsl(var(--pw-console-green))]">root@proxywhirl:~#</span>
            <span className="animate-pulse">_</span>
          </div>
        </div>
        
        {/* Enhanced proxy status indicator */}
        <div className="absolute top-4 right-20 md:right-24 text-[hsl(var(--pw-console-green)_/_80%)] text-xs terminal-text hidden md:flex items-center gap-2">
          <div className="w-2 h-2 bg-[hsl(var(--pw-proxy-healthy))] rounded-full animate-proxy-pulse"></div>
          <span>PROXIES ONLINE</span>
          <div className="w-2 h-2 bg-[hsl(var(--pw-proxy-elite))] rounded-full animate-elite-glow ml-2"></div>
          <span>ELITE</span>
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
