import type React from 'react';
import type { Metadata } from 'next';
import { GeistSans } from 'geist/font/sans';
import { GeistMono } from 'geist/font/mono';
import { TanstackQueryProvider } from '@/lib/tanstack-query-provider';
import { Toaster } from '@/components/ui/sonner';
import './globals.css';
import { ThemeProvider } from '@/components/theme-provider';
import '@/openapi/interceptors';

export const metadata: Metadata = {
  title: 'Arive - Next Generation Talent Management',
  description: 'Streamline your talent management operations with Arive',
  other: {
    'color-scheme': 'light dark',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${GeistSans.variable} ${GeistMono.variable}`}
      suppressHydrationWarning
    >
      <body className="font-sans antialiased">
        <TanstackQueryProvider>
          <ThemeProvider>{children}</ThemeProvider>
        </TanstackQueryProvider>
        <Toaster />
      </body>
    </html>
  );
}
