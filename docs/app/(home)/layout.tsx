import type { ReactNode } from 'react';
import { HomeLayout } from 'fumadocs-ui/layouts/home';
import { baseOptions } from '@/app/layout.config';
import { 
  RiBookOpenLine,
  RiCodeSSlashLine,
  RiGitPullRequestLine,
  RiFileCodeLine,
  RiSparklingLine
} from 'react-icons/ri';
import { Button } from "@/components/ui/button";
import Link from 'fumadocs-core/link';

// Enhanced navigation configuration with modern approach
const NAVIGATION_ITEMS = [
  {
    href: '/docs',
    icon: RiBookOpenLine,
    label: 'Docs',
    description: 'Complete guides and API reference',
    accent: 'blue',
  },
  {
    href: '/usage',
    icon: RiFileCodeLine,
    label: 'Usage',
    description: 'How to use ProxyWhirl effectively',
    accent: 'orange',
  },
  {
    href: '/reference',
    icon: RiCodeSSlashLine,
    label: 'API Reference',
    description: 'Detailed API documentation',
    accent: 'emerald', 
  },
  {
    href: '/contributing',
    icon: RiGitPullRequestLine,
    label: 'Contributing',
    description: 'Join our community',
    accent: 'purple',
  }
] as const;

// Enhanced navigation button component
function NavButton({ item }: { item: typeof NAVIGATION_ITEMS[number] }) {
  const Icon = item.icon;
  
  return (
    <Button variant="ghost" size="sm" className="group relative nav-link-enhanced overflow-hidden">
      <Link href={item.href} className="flex items-center gap-2 font-semibold relative z-10">
        <div className={`relative p-1 rounded-md transition-all duration-300 group-hover:scale-110 ${
          item.accent === 'blue' 
            ? 'group-hover:bg-blue-500/10 group-hover:text-blue-400' 
            : item.accent === 'emerald'
            ? 'group-hover:bg-emerald-500/10 group-hover:text-emerald-400'
            : item.accent === 'purple'
            ? 'group-hover:bg-purple-500/10 group-hover:text-purple-400'
            : 'group-hover:bg-orange-500/10 group-hover:text-orange-400'
        }`}>
          <Icon className="w-4 h-4 transition-all duration-300" />
          
          {/* Icon glow effect */}
          <div className={`absolute inset-0 rounded-md opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${
            item.accent === 'blue' 
              ? 'bg-blue-400' 
              : item.accent === 'emerald'
              ? 'bg-emerald-400'
              : item.accent === 'purple'
              ? 'bg-purple-400'
              : 'bg-orange-400'
          } blur-md scale-150 -z-10`} />
        </div>
        <span className="transition-all duration-300 group-hover:translate-x-0.5">
          {item.label}
        </span>
      </Link>
      
      {/* Enhanced hover background effect */}
      <div className={`absolute inset-0 rounded-md opacity-0 group-hover:opacity-100 transition-all duration-300 -z-10 ${
        item.accent === 'blue' 
          ? 'bg-gradient-to-r from-blue-500/5 to-indigo-500/5' 
          : item.accent === 'emerald'
          ? 'bg-gradient-to-r from-emerald-500/5 to-teal-500/5'
          : item.accent === 'purple'
          ? 'bg-gradient-to-r from-purple-500/5 to-pink-500/5'
          : 'bg-gradient-to-r from-orange-500/5 to-amber-500/5'
      }`} />
      
      {/* Subtle border glow */}
      <div className={`absolute inset-0 rounded-md border opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${
        item.accent === 'blue' 
          ? 'border-blue-500/20' 
          : item.accent === 'emerald'
          ? 'border-emerald-500/20'
          : item.accent === 'purple'
          ? 'border-purple-500/20'
          : 'border-orange-500/20'
      }`} />
    </Button>
  );
}

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <HomeLayout 
      {...baseOptions}
      links={NAVIGATION_ITEMS.map((item) => ({
        type: 'custom',
        children: <NavButton key={item.href} item={item} />
      }))}
    >
      {children}
    </HomeLayout>
  );
}
