import type { Metadata, Viewport } from 'next';
import { ClerkProvider } from '@clerk/nextjs';
import { Inter } from 'next/font/google';
import './globals.css';
import { Toaster } from '@/components/ui/toaster';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Options Portfolio Monitor',
  description: 'Track your options portfolio and get alerts when positions go in-the-money',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Options Monitor',
  },
  formatDetection: {
    telephone: false,
  },
  openGraph: {
    type: 'website',
    siteName: 'Options Portfolio Monitor',
    title: 'Options Portfolio Monitor',
    description: 'Track your options portfolio and get ITM alerts',
  },
};

export const viewport: Viewport = {
  themeColor: '#1f2937',
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en" suppressHydrationWarning>
        <head>
          <link rel="apple-touch-icon" href="/icons/icon-192.png" />
          <meta name="apple-mobile-web-app-capable" content="yes" />
          <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        </head>
        <body className={inter.className}>
          <div className="min-h-screen bg-background">
            {children}
          </div>
          <Toaster />
        </body>
      </html>
    </ClerkProvider>
  );
}
