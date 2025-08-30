import './global.css';
import { RootProvider } from 'fumadocs-ui/provider';
import { Inter } from 'next/font/google';
import type { ReactNode } from 'react';
import type { Metadata } from 'next';

const inter = Inter({
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: {
    default: 'proxywhirl rotating proxy system',
    template: '%s | proxywhirl rotating proxy system'
  },
  description: 'Python proxy server for seamless web requests',
  keywords: [
    'proxy',
    'python',
    'web scraping',
    'requests',
    'proxy server',
    'proxy rotation',
    'web automation'
  ],
  authors: [{ name: 'Wyatt Walsh' }],
  creator: 'Wyatt Walsh',
  publisher: 'proxywhirl',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  icons: {
    icon: [
      { url: '/img/favicon/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/img/favicon/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
      { url: '/img/favicon/favicon.ico', sizes: 'any' }
    ],
    apple: [
      { url: '/img/favicon/apple-touch-icon.png', sizes: '180x180', type: 'image/png' }
    ],
    other: [
      {
        rel: 'mask-icon',
        url: '/img/icon.svg',
        color: '#3b82f6'
      }
    ]
  },
  manifest: '/img/favicon/site.webmanifest',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0f172a' }
  ],
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    siteName: 'proxywhirl',
    title: 'proxywhirl',
    description: 'Elegant Python proxy server for seamless web requests',
    url: 'https://proxywhirl.com',
    images: [
      {
        url: '/img/icon.png',
        width: 1200,
        height: 630,
        alt: 'proxywhirl - Elegant Python Proxy Server'
      }
    ]
  },
  twitter: {
    card: 'summary_large_image',
    title: 'proxywhirl',
    description: 'Elegant Python proxy server for seamless web requests',
    images: ['/img/icon.png'],
  },
  alternates: {
    canonical: 'https://proxywhirl.com',
  }
};

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen">
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  );
}
