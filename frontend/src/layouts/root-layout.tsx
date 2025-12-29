import { useEffect } from 'react';
import { Outlet } from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import { ThemeProvider } from '@/components/theme-provider';
import { Toaster } from '@/components/ui/sonner';
import { TanstackQueryProvider } from '@/lib/tanstack-query-provider';

export function RootLayout() {
  // Set document title and meta on mount
  useEffect(() => {
    document.title = 'Arive - Next Generation Talent Management';
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute(
        'content',
        'Streamline your talent management operations with Arive'
      );
    } else {
      const meta = document.createElement('meta');
      meta.name = 'description';
      meta.content = 'Streamline your talent management operations with Arive';
      document.head.appendChild(meta);
    }
  }, []);

  return (
    <div className="font-sans antialiased">
      <TanstackQueryProvider>
        <ThemeProvider>
          <Outlet />
        </ThemeProvider>
      </TanstackQueryProvider>
      <Toaster />
      {import.meta.env.DEV && (
        <TanStackRouterDevtools position="bottom-right" />
      )}
    </div>
  );
}
