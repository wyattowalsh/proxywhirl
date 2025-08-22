import Link from 'next/link';
import Image from 'next/image';
import Icon from 'public/img/icon.svg';
import { AnimatedBackground } from '@/components/ui/animated-background';
import type { ReactNode } from 'react';
import { LuGauge, LuShieldCheck, LuDatabase } from 'react-icons/lu';

// Data variables
const TITLE = 'proxywhirl';
const SUBTITLE = 'Advanced Rotating Proxy System';

type Feature = {
  icon: ReactNode;
  title: string;
  description: string;
  gradient: string;
};

const FEATURES: Feature[] = [
  {
    icon: <LuGauge className="feature-icon" />,
    title: 'Async Rotation',
    description: 'Latency-aware rotation, retries, timeouts, and health scoring.',
    gradient: 'from-blue-500/10 via-indigo-500/10 to-purple-500/10',
  },
  {
    icon: <LuShieldCheck className="feature-icon" />,
    title: 'Strict Validation',
    description: 'Pydantic-first models: IP, port, scheme, and country checks.',
    gradient: 'from-green-500/10 via-emerald-500/10 to-teal-500/10',
  },
  {
    icon: <LuDatabase className="feature-icon" />,
    title: 'Multi-Backend Cache',
    description: 'Memory, JSON, or SQLite for warm starts and persistence.',
    gradient: 'from-amber-500/10 via-orange-500/10 to-rose-500/10',
  },
];

type Button = {
  href: string;
  label: string;
  ariaLabel: string;
  external?: boolean;
};

const BUTTONS: Button[] = [
  {
    href: '/docs',
    label: 'Get Started',
    ariaLabel: 'Get started with proxywhirl documentation',
  },
  {
    href: 'https://github.com/wyattowalsh/proxywhirl',
    label: 'View on GitHub',
    ariaLabel: 'View proxywhirl source code on GitHub (opens in new tab)',
    external: true,
  },
];

export default function HomePage() {
  return (
    <div className="landing-page-container">
      {/* Animated Background */}
      <AnimatedBackground />

      {/* Content */}
      <main className="relative z-10 flex flex-col justify-center items-center text-center px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto h-full">
        {/* Hero Section */}
        <div className="flex flex-col items-center space-y-8 sm:space-y-12">
          {/* Logo Section with Enhanced Effects */}
          <div className="relative group">
            {/* Multiple glow rings for depth */}
            <div className="absolute inset-0 w-28 h-28 bg-gradient-to-r from-blue-500 via-purple-500 to-cyan-500 rounded-full blur-xl opacity-20 group-hover:opacity-40 transition-opacity duration-700 animate-pulse-slow" />
            <div className="absolute inset-0 w-24 h-24 bg-gradient-to-r from-cyan-400 to-blue-400 rounded-full blur-lg opacity-30 group-hover:opacity-60 transition-opacity duration-500 animate-pulse" />
            <div className="relative transform group-hover:scale-110 transition-transform duration-500 ease-out">
              <Image
                src={Icon}
                alt="proxywhirl Logo — Python rotating proxies library"
                width={112}
                height={112}
                className="drop-shadow-2xl animate-bounce-subtle"
                priority
              />
            </div>
          </div>

          {/* Title with Enhanced Typography */}
          <div className="space-y-6">
            <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-black tracking-tight leading-none">
              <span className="pw bg-gradient-to-r from-blue-600 via-purple-600 via-cyan-600 to-teal-600 bg-clip-text text-transparent animate-gradient-x drop-shadow-sm">
                {TITLE}
              </span>
            </h1>

            {/* Enhanced tagline with better contrast and readability */}
            <p className="text-lg sm:text-xl lg:text-2xl xl:text-3xl text-fd-muted-foreground max-w-4xl leading-relaxed font-light tracking-wide">
              {SUBTITLE}
            </p>
          </div>
        </div>

        {/* Enhanced Feature Grid with Better Accessibility */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 w-full max-w-5xl mt-12 lg:mt-16">
          {FEATURES.map((feature, index) => (
            <div
              key={feature.title}
              className="group relative bg-white/70 dark:bg-black/30 backdrop-blur-xl border border-white/30 dark:border-white/10 rounded-3xl p-6 lg:p-8 hover:scale-105 hover:-translate-y-2 transition-all duration-500 ease-out shadow-lg hover:shadow-2xl hover:shadow-blue-500/10 focus-within:ring-2 focus-within:ring-blue-500/50"
              role="article"
              aria-labelledby={`feature-${index}-title`}
              tabIndex={0}
            >
              <div
                className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
              />
              <div className="relative z-10 space-y-4">
                <div
                  className="feature-icon-wrap transform group-hover:scale-110 group-hover:rotate-6 transition-all duration-500 ease-out"
                  role="img"
                  aria-label={`${feature.title} icon`}
                >
                  {feature.icon}
                </div>
                <h3
                  id={`feature-${index}-title`}
                  className="font-bold text-xl lg:text-2xl text-fd-foreground tracking-tight"
                >
                  {feature.title}
                </h3>
                <p className="text-fd-muted-foreground leading-relaxed text-base lg:text-lg">
                  {feature.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Enhanced CTA Section with Better Accessibility */}
        <div className="flex flex-col sm:flex-row gap-6 lg:gap-8 items-center mt-12 lg:mt-16">
          <Link
            href={BUTTONS[0].href}
            className="group relative inline-flex items-center justify-center px-8 lg:px-10 py-4 lg:py-5 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white font-bold text-lg lg:text-xl rounded-3xl overflow-hidden transform hover:scale-105 hover:-translate-y-1 transition-all duration-300 ease-out shadow-xl hover:shadow-2xl hover:shadow-blue-500/25 focus:outline-none focus:ring-4 focus:ring-blue-500/50 focus:ring-offset-2 focus:ring-offset-transparent"
            aria-label={BUTTONS[0].ariaLabel}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600 via-fuchsia-600 to-cyan-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            <span className="relative z-10 flex items-center font-semibold tracking-wide">
              {BUTTONS[0].label}
              <svg
                className="ml-3 w-5 h-5 lg:w-6 lg:h-6 transform group-hover:translate-x-2 transition-transform duration-300 ease-out"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
              </svg>
            </span>
          </Link>

          <Link
            href={BUTTONS[1].href}
            className="group relative inline-flex items-center justify-center px-8 lg:px-10 py-4 lg:py-5 bg-white/20 dark:bg-black/20 backdrop-blur-xl border border-white/40 dark:border-white/20 text-fd-foreground font-semibold text-lg lg:text-xl rounded-3xl hover:bg-white/30 dark:hover:bg-black/30 transition-all duration-300 ease-out transform hover:scale-105 hover:-translate-y-1 shadow-lg hover:shadow-xl focus:outline-none focus:ring-4 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-transparent"
            target={BUTTONS[1].external ? '_blank' : undefined}
            rel={BUTTONS[1].external ? 'noopener noreferrer' : undefined}
            aria-label={BUTTONS[1].ariaLabel}
          >
            <svg
              className="mr-3 w-5 h-5 lg:w-6 lg:h-6 transform group-hover:rotate-12 transition-transform duration-300 ease-out"
              fill="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            <span className="font-semibold tracking-wide">{BUTTONS[1].label}</span>
          </Link>
        </div>
      </main>
    </div>
  );
}
