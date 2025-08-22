import { type HomeLayoutProps, type DocsLayoutProps } from 'fumadocs-ui/layout';
import { type AppProps } from '@/components/layouts/page';
import { source } from './lib/source';

// shared configuration
export const layoutProps: HomeLayoutProps & DocsLayoutProps = {
  nav: {
    title: 'My App',
  },
  links: [
    {
      text: 'Documentation',
      url: '/docs',
      active: 'nested-url',
    },
  ],
};

// docs layout configuration
export const docsProps: AppProps = {
  tree: source.pageTree,
}; 