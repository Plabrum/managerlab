'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard,
  Megaphone,
  FileText,
  Building2,
  Users,
  Settings,
} from 'lucide-react';

import { useAuth } from '@/components/provers/auth-provider';
const availablePages = {
  dashboard: {
    label: 'Dashboard',
    icon: LayoutDashboard,
    href: '/',
  },
  campaigns: { label: 'Campaigns', icon: Megaphone, href: '/campaigns' },
  invoices: { label: 'Invoices', icon: FileText, href: '/invoices' },
  brands: { label: 'Brands', icon: Building2, href: '/brands' },
  roster: { label: 'Roster', icon: Users, href: '/roster' },
};

const navigationItems = Object.values(availablePages);

export function HomeNavigation() {
  const user = useAuth();
  const pathname = usePathname();

  return (
    <div className="flex w-64 flex-col border-r border-gray-800 bg-gray-900">
      {/* Logo/Brand */}
      <div className="flex h-16 items-center border-b border-gray-800 px-6">
        <h1 className="text-xl font-bold text-white">Arive</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-2 p-4">
        {navigationItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;

          return (
            <Link
              key={index}
              href={item.href}
              className={`flex w-full items-center space-x-3 rounded-lg px-4 py-3 transition-colors ${
                isActive
                  ? 'bg-white text-black'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon className="h-5 w-5" />
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="border-t border-gray-800 px-4 py-4">
        <div className="flex items-center space-x-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white font-semibold text-black">
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-white">
              {user.name}
            </p>
            <p className="truncate text-xs text-gray-400">{user.email}</p>
          </div>
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
      </div>
    </div>
  );
}

export function HomeTopBar() {
  const pathname = usePathname();

  const getPageTitle = () => {
    if (pathname === '/settings') return 'Settings';
    if (pathname === '/') return 'Dashboard';
    const item = navigationItems.find((item) => item.href === pathname);
    return item ? item.label : 'Dashboard';
  };

  return (
    <header className="flex h-16 items-center border-b border-gray-800 bg-gray-900 px-6">
      <h1 className="text-2xl font-semibold text-white">{getPageTitle()}</h1>
    </header>
  );
}
