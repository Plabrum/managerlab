import type { ReactNode } from 'react';

interface NavbarProps {
  children: ReactNode;
  brand?: ReactNode;
  actions?: ReactNode;
}

export function Navbar({ children, brand, actions }: NavbarProps) {
  return (
    <nav className="w-full bg-black">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="relative flex h-16 items-center justify-center">
          {brand && <div className="absolute left-0">{brand}</div>}
          <div className="hidden md:block">
            <div className="flex items-baseline space-x-4">{children}</div>
          </div>
          {actions && (
            <div className="absolute right-0 flex items-center space-x-4">
              {actions}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
