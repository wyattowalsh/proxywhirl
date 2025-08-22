import { source } from '@/lib/source';
import {
  DocsPage,
  DocsBody,
} from '@/components/layouts/page';
import { notFound } from 'next/navigation';
import { createRelativeLink } from "fumadocs-ui/mdx";
import { getMDXComponents } from "@/mdx-components";
import type { Metadata } from 'next';
import { createElement } from 'react';
import Link from 'next/link';
import { icons as lucideIcons } from 'lucide-react';
import * as Ai from 'react-icons/ai';
import * as Bi from 'react-icons/bi';
import * as Bs from 'react-icons/bs';
import * as Cg from 'react-icons/cg';
import * as Ci from 'react-icons/ci';
import * as Di from 'react-icons/di';
import * as Fa from 'react-icons/fa';
import * as Fa6 from 'react-icons/fa6';
import * as Fc from 'react-icons/fc';
import * as Fi from 'react-icons/fi';
import * as Gi from 'react-icons/gi';
import * as Go from 'react-icons/go';
import * as Gr from 'react-icons/gr';
import * as Hi from 'react-icons/hi';
import * as Hi2 from 'react-icons/hi2';
import * as Im from 'react-icons/im';
import * as Io from 'react-icons/io';
import * as Io5 from 'react-icons/io5';
import * as Lia from 'react-icons/lia';
import * as Lu from 'react-icons/lu';
import * as Md from 'react-icons/md';
import * as Pi from 'react-icons/pi';
import * as Ri from 'react-icons/ri';
import * as Si from 'react-icons/si';
import * as Sl from 'react-icons/sl';
import * as Tb from 'react-icons/tb';
import * as Tfi from 'react-icons/tfi';
import * as Ti from 'react-icons/ti';
import * as Vsc from 'react-icons/vsc';
import * as Wi from 'react-icons/wi';

// Icon sets mapping (same as source.ts)
const iconSets = {
  ai: Ai,
  bi: Bi,
  bs: Bs,
  cg: Cg,
  ci: Ci,
  di: Di,
  fa: Fa,
  fa6: Fa6,
  fc: Fc,
  fi: Fi,
  gi: Gi,
  go: Go,
  gr: Gr,
  hi: Hi,
  hi2: Hi2,
  im: Im,
  io: Io,
  io5: Io5,
  lia: Lia,
  lu: Lu,
  md: Md,
  pi: Pi,
  ri: Ri,
  si: Si,
  sl: Sl,
  tb: Tb,
  tfi: Tfi,
  ti: Ti,
  vsc: Vsc,
  wi: Wi,
};

// Icon resolver function that matches your source.ts logic exactly
function resolveIcon(iconString: string): React.ReactElement | null {
  if (!iconString) return null;

  // Support for lucide icons (direct name)
  if (iconString in lucideIcons) {
    return createElement(lucideIcons[iconString as keyof typeof lucideIcons]);
  }

  // Support for react-icons (prefix/name format)
  if (iconString.includes('/')) {
    const [prefix, iconName] = iconString.split('/');
    
    if (!prefix || !iconName) return null;

    const iconSet = iconSets[prefix as keyof typeof iconSets];
    if (!iconSet) return null;

    const IconComponent = iconSet[iconName as keyof typeof iconSet] as React.ComponentType;
    if (IconComponent) {
      return createElement(IconComponent);
    }
  }

  return null;
}

export default async function Page(props: {
  params: Promise<{ slug?: string[] }>;
}) {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();

  const MDXContent = page.data.body;
  // Access icon from page's frontmatter - the schema includes icon as ZodOptional<ZodString>
  const pageData = page.data as typeof page.data & { icon?: string };
  const pageIcon = pageData.icon ? resolveIcon(pageData.icon) : null;

  return (
    <DocsPage toc={page.data.toc} full={page.data.full}>
      {pageData.icon && pageIcon ? (
        <div className="relative mb-4 p-4 rounded-2xl bg-gradient-to-br from-blue-50/50 via-purple-50/30 to-pink-50/50 dark:from-blue-950/20 dark:via-purple-950/10 dark:to-pink-950/20 border border-blue-200/50 dark:border-blue-800/30 overflow-hidden">
          {/* Enhanced background decoration */}
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/5 to-pink-500/10" />
          <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-blue-400/30 via-purple-400/50 to-pink-400/30" />
          <div className="absolute -top-4 -right-4 w-32 h-32 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-2xl" />
          <div className="absolute -bottom-4 -left-4 w-24 h-24 bg-gradient-to-br from-purple-400/15 to-pink-400/15 rounded-full blur-xl" />
          
          <Link 
            href={`/docs/${params.slug?.join('/') || ''}`}
            className="group/header block"
          >
            <div className="relative flex items-center gap-6 transition-all duration-300 hover:scale-[1.02]">
              <div className="group relative flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-blue-500/20 via-purple-500/15 to-pink-500/10 border border-blue-400/30 shadow-lg shadow-blue-500/20 group-hover/header:shadow-xl group-hover/header:shadow-purple-500/25 transition-all duration-300 group-hover/header:scale-105 flex-shrink-0">
                <div className="text-blue-600 dark:text-blue-400 group-hover/header:text-purple-600 dark:group-hover/header:text-purple-400 group-hover/header:scale-110 transition-all duration-300 text-6xl">
                  {pageIcon}
                </div>
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/30 via-blue-100/20 to-purple-100/20 dark:from-white/10 dark:via-blue-400/10 dark:to-purple-400/10 opacity-0 group-hover/header:opacity-100 transition-opacity duration-300" />
              </div>
              
              <div className="flex-1 space-y-2 min-w-0">
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 dark:from-blue-400 dark:via-purple-400 dark:to-pink-400 bg-clip-text text-transparent leading-tight group-hover/header:from-purple-600 group-hover/header:via-pink-600 group-hover/header:to-blue-600 dark:group-hover/header:from-purple-400 dark:group-hover/header:via-pink-400 dark:group-hover/header:to-blue-400 transition-all duration-300">
                  {page.data.title}
                </h1>
                
                {page.data.description && (
                  <p className="text-lg text-slate-600 dark:text-slate-400 leading-relaxed max-w-2xl group-hover/header:text-slate-500 dark:group-hover/header:text-slate-300 transition-colors duration-300">
                    {page.data.description}
                  </p>
                )}
              </div>
            </div>
          </Link>
        </div>
      ) : (
        <div className="relative mb-12 space-y-8">
          {/* Enhanced background decoration for title-only */}
          <div className="absolute -top-8 -left-8 w-32 h-32 bg-gradient-to-br from-blue-500/15 via-purple-500/10 to-pink-500/15 rounded-full blur-2xl" />
          <div className="absolute -top-4 -right-8 w-24 h-24 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-full blur-xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 bg-gradient-to-br from-blue-400/5 via-purple-400/5 to-pink-400/5 rounded-full blur-3xl" />
          
          <Link 
            href={`/docs/${params.slug?.join('/') || ''}`}
            className="group/header block"
          >
            <div className="relative space-y-6 transition-all duration-300 hover:scale-[1.01]">
              <div className="space-y-4">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 dark:from-blue-400 dark:via-purple-400 dark:to-pink-400 bg-clip-text text-transparent leading-tight tracking-tight group-hover/header:from-purple-600 group-hover/header:via-pink-600 group-hover/header:to-blue-600 dark:group-hover/header:from-purple-400 dark:group-hover/header:via-pink-400 dark:group-hover/header:to-blue-400 transition-all duration-300">
                  {page.data.title}
                </h1>
              
                {page.data.description && (
                  <p className="text-xl text-slate-600 dark:text-slate-400 leading-relaxed max-w-3xl group-hover/header:text-slate-500 dark:group-hover/header:text-slate-300 transition-colors duration-300">
                    {page.data.description}
                  </p>
                )}
              </div>
              
              {/* Colorful separator */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full h-px bg-gradient-to-r from-blue-200 via-purple-200 to-pink-200 dark:from-blue-800 dark:via-purple-800 dark:to-pink-800" />
                </div>
                <div className="relative flex justify-center">
                  <div className="px-4 bg-background">
                    <div className="w-2 h-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500" />
                  </div>
                </div>
              </div>
            </div>
          </Link>
        </div>
      )}

      <DocsBody>
        <MDXContent
          components={getMDXComponents({
            relative: (url) => createRelativeLink(url, page),
          })}
        />
      </DocsBody>
    </DocsPage>
  );
}

export async function generateStaticParams(): Promise<Array<{ slug?: string[] }>> {
  return source.generateParams();
}

export async function generateMetadata(props: {
  params: Promise<{ slug?: string[] }>;
}): Promise<Metadata> {
  const params = await props.params;
  const page = source.getPage(params.slug);
  if (!page) notFound();

  return {
    title: page.data.title,
    description: page.data.description,
  };
}
