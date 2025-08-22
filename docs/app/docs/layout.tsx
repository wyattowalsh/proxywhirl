import { DocsLayout } from '@/components/layouts/docs';
import type { ReactNode } from 'react';
import { baseOptions } from '@/app/layout.config';
import { source } from '@/lib/source';
import { GithubInfo } from 'fumadocs-ui/components/github-info';


const docsOptions: DocsLayoutProps = {
  ...baseOptions,
  tree: source.pageTree,
  footer: (
        <GithubInfo owner="wyattowalsh" repo="proxywhirl" className="lg:-mx-2" />
      ),
};


export default function Layout({ children }: { children: ReactNode }) {
  return <DocsLayout {...docsOptions}>{children}</DocsLayout>;
}
