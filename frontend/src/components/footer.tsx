import type { ReactNode } from 'react';

interface FooterProps {
  children: ReactNode;
  brand?: ReactNode;
  copyright?: string;
}

export function Footer({ children, brand, copyright }: FooterProps) {
  return (
    <footer className="border-t border-gray-800 bg-black">
      <div className="container mx-auto px-4 py-12 sm:px-6 lg:px-8">
        <div className="grid gap-8 md:grid-cols-4">
          {brand && <div className="space-y-4">{brand}</div>}
          {children}
        </div>
        {copyright && (
          <div className="text-muted-foreground mt-12 border-t border-gray-800 pt-8 text-center text-sm">
            <p>{copyright}</p>
          </div>
        )}
      </div>
    </footer>
  );
}
