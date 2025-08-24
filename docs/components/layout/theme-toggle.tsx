'use client';
import { cva } from 'class-variance-authority';
import { Moon, Sun, Airplay, ChevronDown } from 'lucide-react';
import { useTheme } from 'next-themes';
import { type HTMLAttributes, useLayoutEffect, useState } from 'react';
import { cn } from '../../lib/cn';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';

const triggerVariants = cva(
  'group relative inline-flex items-center justify-center gap-2 rounded-full border border-fd-border/60 bg-gradient-to-br from-fd-background/95 via-fd-background/90 to-fd-background/85 backdrop-blur-lg p-1.5 shadow-lg transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] hover:shadow-2xl hover:shadow-fd-primary/10 hover:bg-gradient-to-tr hover:from-fd-accent/5 hover:via-fd-background/95 hover:to-fd-primary/5 hover:border-fd-primary/20 hover:-translate-y-0.5 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-fd-primary/50 focus:ring-offset-2 focus:ring-offset-fd-background active:scale-95 active:transition-transform active:duration-150 data-[state=open]:bg-gradient-to-br data-[state=open]:from-fd-accent/10 data-[state=open]:to-fd-primary/10 data-[state=open]:text-fd-accent-foreground data-[state=open]:shadow-2xl data-[state=open]:shadow-fd-primary/20 data-[state=open]:border-fd-primary/30 data-[state=open]:-translate-y-0.5 data-[state=open]:scale-105 animate-float-subtle overflow-hidden',
  {
    variants: {
      size: {
        sm: 'min-w-8 h-8 p-1',
        md: 'min-w-11 h-11 p-1.5',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  },
);

const iconVariants = cva(
  'relative transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)] group-hover:rotate-12 group-hover:scale-110 group-active:scale-95 drop-shadow-sm group-hover:drop-shadow-lg filter-gpu',
  {
    variants: {
      size: {
        sm: 'size-4',
        md: 'size-5',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  },
);

const dropdownItemVariants = cva(
  'group flex items-center gap-3 w-full rounded-xl p-3 text-sm transition-all duration-300 ease-[cubic-bezier(0.23,1,0.32,1)] hover:bg-gradient-to-r hover:from-fd-accent/80 hover:to-fd-accent/60 hover:text-fd-accent-foreground hover:shadow-md hover:shadow-fd-accent/20 hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-fd-primary/50 focus:ring-offset-1 focus:ring-offset-fd-background cursor-pointer active:scale-[0.98] active:transition-transform active:duration-100 relative overflow-hidden',
  {
    variants: {
      active: {
        true: 'bg-gradient-to-r from-fd-primary/15 to-fd-primary/10 text-fd-primary font-semibold shadow-md shadow-fd-primary/10 ring-1 ring-fd-primary/20',
        false: 'text-fd-muted-foreground hover:text-fd-foreground',
      },
    },
  },
);

const themeOptions = [
  {
    key: 'light',
    icon: Sun,
    label: 'Light theme',
    description: 'Light appearance',
  },
  {
    key: 'dark', 
    icon: Moon,
    label: 'Dark theme',
    description: 'Dark appearance',
  },
  {
    key: 'system',
    icon: Airplay,
    label: 'System theme',
    description: 'Follow system preference',
  },
] as const;

export function ThemeToggle({
  className,
  mode = 'light-dark-system',
  size = 'md',
  ...props
}: HTMLAttributes<HTMLElement> & {
  mode?: 'light-dark' | 'light-dark-system';
  size?: 'sm' | 'md';
}) {
  const { setTheme, theme, resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [open, setOpen] = useState(false);

  useLayoutEffect(() => {
    setMounted(true);
  }, []);

  // Enhanced loading state with skeleton
  if (!mounted) {
    return (
      <div
        className={cn(triggerVariants({ size }), className)}
        aria-label="Theme toggle loading"
        {...props}
      >
        <div className={cn(iconVariants({ size }), "rounded-full bg-fd-muted/50 animate-pulse")} />
      </div>
    );
  }

  // Get available options based on mode
  const availableOptions = mode === 'light-dark' 
    ? themeOptions.slice(0, 2)
    : themeOptions;

  // Find current theme option
  const currentTheme = theme || 'system';
  const currentOption = availableOptions.find(option => option.key === currentTheme) || availableOptions[0];

  // Always show opposite theme based on resolvedTheme (actual computed theme)
  // In light mode -> show Moon (to switch TO dark)
  // In dark mode -> show Sun (to switch TO light)
  // Use resolvedTheme which gives us 'light' or 'dark' regardless of theme setting
  const displayOption = resolvedTheme === 'dark' 
    ? themeOptions.find(option => option.key === 'light') || themeOptions[0] // Show sun when in dark mode
    : themeOptions.find(option => option.key === 'dark') || themeOptions[1]; // Show moon when in light mode

  const handleThemeChange = (newTheme: string) => {
    setTheme(newTheme);
    setOpen(false);
  };

  // Handle direct toggle - always toggle between light and dark
  const handleDirectToggle = () => {
    const newTheme = resolvedTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  };

  return (
    <Popover open={false} onOpenChange={undefined}>
      <PopoverTrigger
        className={cn(triggerVariants({ size }), className)}
        aria-label={`Switch to ${displayOption.label.toLowerCase()}`}
        data-theme-toggle=""
        onClick={handleDirectToggle}
        {...props}
      >
        {/* Animated background gradient */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-fd-primary/20 via-transparent to-fd-accent/20 opacity-0 group-hover:opacity-100 group-data-[state=open]:opacity-100 transition-opacity duration-500 animate-pulse-slow" />
        
        {/* Main icon container */}
        <div className="relative z-10 flex items-center justify-center">
          <displayOption.icon
            className={cn(iconVariants({ size }), "relative z-10")}
            fill="currentColor"
            strokeWidth={1.5}
          />
          
          {/* Glow effect behind icon */}
          <div className="absolute inset-0 rounded-full bg-current opacity-0 blur-lg scale-150 group-hover:opacity-20 group-data-[state=open]:opacity-30 transition-all duration-500" />
        </div>

        {/* Ripple effect */}
        <div className="absolute inset-0 rounded-full bg-fd-primary/30 scale-0 group-active:scale-100 group-active:opacity-20 opacity-0 transition-all duration-300" />
      </PopoverTrigger>

      <PopoverContent 
        className="w-64 p-3 overflow-hidden border-fd-border/60 bg-gradient-to-br from-fd-background/95 via-fd-background/90 to-fd-background/85 backdrop-blur-xl shadow-2xl shadow-fd-primary/5 animate-in fade-in-0 zoom-in-95 slide-in-from-top-2 duration-300"
        side="bottom"
        align="end"
        sideOffset={12}
      >
        <div className="space-y-2">
          <div className="px-3 py-2 text-xs font-bold text-fd-muted-foreground uppercase tracking-widest border-b border-fd-border/50 mb-3 bg-gradient-to-r from-fd-primary/10 to-fd-accent/10 rounded-lg backdrop-blur-sm">
            ✨ Theme Selection
          </div>
          
          {availableOptions.map((option) => {
            const isActive = currentTheme === option.key;
            
            return (
              <button
                key={option.key}
                onClick={() => handleThemeChange(option.key)}
                className={cn(dropdownItemVariants({ active: isActive }))}
                role="menuitem"
                aria-checked={isActive}
              >
                {/* Shimmer effect overlay */}
                <div className="absolute inset-0 translate-x-[-100%] group-hover:translate-x-[100%] bg-gradient-to-r from-transparent via-white/10 to-transparent transition-transform duration-700 ease-out" />
                
                <div className={cn(
                  "relative flex items-center justify-center size-10 rounded-xl border-2 transition-all duration-300 group-hover:scale-110 group-hover:rotate-3",
                  isActive 
                    ? "bg-gradient-to-br from-fd-primary/20 to-fd-primary/10 border-fd-primary/40 text-fd-primary shadow-lg shadow-fd-primary/20" 
                    : "bg-gradient-to-br from-fd-muted/30 to-fd-muted/20 border-fd-border text-fd-muted-foreground group-hover:from-fd-accent/20 group-hover:to-fd-accent/10 group-hover:border-fd-accent/50 group-hover:text-fd-accent-foreground group-hover:shadow-md group-hover:shadow-fd-accent/10"
                )}>
                  <option.icon 
                    className="size-5 transition-all duration-300 group-hover:scale-110 group-hover:rotate-12 drop-shadow-sm filter-gpu" 
                    fill="currentColor"
                    strokeWidth={1.5}
                  />
                  
                  {/* Icon glow effect */}
                  <div className="absolute inset-0 rounded-xl bg-current opacity-0 blur-md scale-110 group-hover:opacity-10 transition-all duration-300" />
                </div>
                
                <div className="flex-1 text-left relative z-10">
                  <div className="font-semibold text-base group-hover:text-fd-accent-foreground transition-colors duration-200">
                    {option.label}
                  </div>
                  <div className="text-xs text-fd-muted-foreground group-hover:text-fd-muted-foreground/90 transition-colors duration-200 mt-0.5">
                    {option.description}
                  </div>
                </div>
                
                {isActive && (
                  <div className="relative">
                    <div className="size-3 rounded-full bg-fd-primary animate-pulse shadow-lg shadow-fd-primary/50" />
                    <div className="absolute inset-0 size-3 rounded-full bg-fd-primary opacity-30 animate-ping" />
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </PopoverContent>
    </Popover>
  );
}
