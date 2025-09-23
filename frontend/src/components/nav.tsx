'use client';

import type React from 'react';

import { useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { useIsMobile } from '@/hooks/use-mobile';
import {
  LayoutDashboard,
  Megaphone,
  FileText,
  Building2,
  Users,
  Settings,
  Menu,
  ChevronLeft,
  ChevronsRight,
} from 'lucide-react';

import { useAuth } from '@/components/providers/auth-provider';

const availablePages = {
  dashboard: {
    label: 'Dashboard',
    icon: LayoutDashboard,
    href: '/dashboard',
  },
  campaigns: { label: 'Campaigns', icon: Megaphone, href: '/campaigns' },
  invoices: { label: 'Invoices', icon: FileText, href: '/invoices' },
  brands: { label: 'Brands', icon: Building2, href: '/brands' },
  roster: { label: 'Roster', icon: Users, href: '/roster' },
};

const navigationItems = Object.values(availablePages);

function NavigationContent({
  isCollapsed = false,
  onItemClick,
}: {
  isCollapsed?: boolean;
  onItemClick?: () => void;
}) {
  const user = useAuth();
  const pathname = usePathname();

  return (
    <>
      {/* Navigation */}
      <nav className="flex-1 space-y-2 p-4">
        {navigationItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={index}
              href={item.href}
              onClick={onItemClick}
              className={`flex w-full items-center rounded-lg py-3 transition-colors ${
                isCollapsed
                  ? `justify-center px-2 ${isActive ? '' : 'text-gray-300 hover:text-white'}`
                  : `space-x-3 px-4 ${isActive ? 'bg-white text-black' : 'text-gray-300 hover:bg-gray-800 hover:text-white'}`
              }`}
            >
              <div
                className={`flex items-center justify-center ${
                  isCollapsed && isActive
                    ? 'rounded-lg bg-white p-2 text-black'
                    : isCollapsed
                      ? 'rounded-lg p-2 hover:bg-gray-800 hover:text-white'
                      : ''
                }`}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
              </div>
              {!isCollapsed && (
                <span className="font-medium">{item.label}</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="border-t border-gray-800 px-4 py-4">
        <div
          className={`flex items-center ${isCollapsed ? 'justify-center' : 'space-x-3'}`}
        >
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-white font-semibold text-black">
            {user.name.charAt(0).toUpperCase()}
          </div>
          {!isCollapsed && (
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-white">
                {user.name}
              </p>
              <p className="truncate text-xs text-gray-400">{user.email}</p>
            </div>
          )}
          {!isCollapsed && (
            <Link href="/settings">
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 text-gray-300 hover:bg-gray-800 hover:text-white"
              >
                <Settings className="h-4 w-4" />
              </Button>
            </Link>
          )}
        </div>
        {isCollapsed && (
          <div className="mt-2 flex justify-center">
            <Link href="/settings">
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0 text-gray-300 hover:bg-gray-800 hover:text-white"
              >
                <Settings className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        )}
      </div>
    </>
  );
}

export function Nav({ children }: { children?: React.ReactNode }) {
  const pathname = usePathname();
  const isMobile = useIsMobile();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  const getPageTitle = () => {
    if (pathname === '/settings') return 'Settings';
    const item = navigationItems.find((item) => item.href === pathname);
    return item ? item.label : 'Dashboard';
  };

  if (isMobile) {
    return (
      <div className="flex min-h-screen bg-black">
        <div className="flex flex-1 flex-col">
          {/* Mobile Top Bar */}
          <header className="flex h-16 items-center border-b border-gray-800 bg-gray-900 px-4">
            <Sheet open={isMobileOpen} onOpenChange={setIsMobileOpen}>
              <SheetTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="mr-4 h-8 w-8 p-0 text-gray-300 hover:bg-gray-800 hover:text-white"
                >
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent
                side="left"
                className="w-64 border-gray-800 bg-gray-900 p-0 [&>button]:text-white [&>button]:hover:text-gray-300"
              >
                <SheetHeader className="border-b border-gray-800 p-6">
                  <SheetTitle className="text-left text-xl font-bold text-white">
                    Arive
                  </SheetTitle>
                </SheetHeader>
                <div className="flex h-full flex-col">
                  <NavigationContent
                    onItemClick={() => setIsMobileOpen(false)}
                  />
                </div>
              </SheetContent>
            </Sheet>
            <h1 className="text-2xl font-semibold text-white">
              {getPageTitle()}
            </h1>
          </header>
          {children}
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-black">
      {/* Desktop Sidebar Navigation */}
      <div
        className={`flex flex-col border-r border-gray-800 bg-gray-900 transition-all duration-300 ${
          isCollapsed ? 'w-16' : 'w-64'
        }`}
      >
        {/* Logo/Brand with collapse toggle */}
        <div className="flex h-16 items-center border-b border-gray-800 px-4">
          {isCollapsed ? (
            <div className="flex w-full justify-center">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsCollapsed(false)}
                className="h-8 w-8 p-0 text-white hover:bg-gray-800"
              >
                <ChevronsRight className="h-5 w-5" />
              </Button>
            </div>
          ) : (
            <div className="flex w-full items-center justify-between">
              <h1 className="text-xl font-bold text-white">Arive</h1>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsCollapsed(true)}
                className="h-8 w-8 p-0 text-white hover:bg-gray-800"
              >
                <ChevronLeft className="h-5 w-5" />
              </Button>
            </div>
          )}
        </div>

        <NavigationContent isCollapsed={isCollapsed} />
      </div>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col">
        {/* Top Bar */}
        <header className="flex h-16 items-center border-b border-gray-800 bg-gray-900 px-6">
          <h1 className="text-2xl font-semibold text-white">
            {getPageTitle()}
          </h1>
        </header>
        {children}
      </div>
    </div>
  );
}
