'use client';

import { useAuth } from '@/components/provers/auth-provider';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard,
  Megaphone,
  FileText,
  Building2,
  Users,
  Settings,
} from 'lucide-react';

const navigationItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'campaigns', label: 'Campaigns', icon: Megaphone },
  { id: 'invoices', label: 'Invoices', icon: FileText },
  { id: 'brands', label: 'Brands', icon: Building2 },
  { id: 'roster', label: 'Roster', icon: Users },
];

export default function HomePage() {
  const user = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">
              Dashboard Overview
            </h2>
          </div>
        );
      case 'campaigns':
        return (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Campaigns</h2>
          </div>
        );
      case 'invoices':
        return (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Invoices</h2>
          </div>
        );
      case 'brands':
        return (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Brands</h2>
          </div>
        );
      case 'roster':
        return (
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Roster</h2>
          </div>
        );
      default:
        return null;
    }
  };

  const getPageTitle = () => {
    const item = navigationItems.find((item) => item.id === activeTab);
    return item ? item.label : 'Dashboard';
  };

  return (
    <div className="flex min-h-screen bg-black">
      {/* Sidebar */}
      <div className="flex w-64 flex-col border-r border-gray-800 bg-gray-900">
        {/* Logo/Brand */}
        <div className="flex h-16 items-center border-b border-gray-800 px-6">
          <h1 className="text-xl font-bold text-white">Arive</h1>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-2 p-4">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex w-full items-center space-x-3 rounded-lg px-4 py-3 text-left transition-colors ${
                  isActive
                    ? 'bg-white text-black'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span className="font-medium">{item.label}</span>
              </button>
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
            <Button
              variant="ghost"
              size="sm"
              className="h-8 w-8 p-0 text-gray-300 hover:bg-gray-800 hover:text-white"
            >
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col">
        {/* Top Bar */}
        <header className="flex h-16 items-center border-b border-gray-800 bg-gray-900 px-6">
          <h1 className="text-2xl font-semibold text-white">
            {getPageTitle()}
          </h1>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6">{renderContent()}</main>
      </div>
    </div>
  );
}
