'use client';

import * as React from 'react';
import {
  LayoutDashboard,
  Megaphone,
  FileText,
  Building2,
  Users,
  Settings2,
  GalleryVerticalEnd,
  Image,
  Newspaper,
} from 'lucide-react';

import { NavMain } from '@/components/nav-main';
import { NavUser } from '@/components/nav-user';
import { TeamSwitcher } from '@/components/team-switcher';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from '@/components/ui/sidebar';
import { useAuth } from '@/components/providers/auth-provider';

const teams = [
  {
    name: 'Arive',
    logo: GalleryVerticalEnd,
    plan: 'Enterprise',
  },
];

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const user = useAuth();

  const navMain = [
    {
      title: 'Dashboard',
      url: '/dashboard',
      icon: LayoutDashboard,
    },
    {
      title: 'Campaigns',
      url: '/campaigns',
      icon: Megaphone,
    },
    {
      title: 'Brands',
      url: '/brands',
      icon: Building2,
    },
    {
      title: 'Roster',
      url: '/roster',
      icon: Users,
    },
    {
      title: 'Posts',
      url: '/posts',
      icon: Newspaper,
    },
    {
      title: 'Media',
      url: '/media',
      icon: Image,
    },
    {
      title: 'Invoices',
      url: '/invoices',
      icon: FileText,
    },
    {
      title: 'Settings',
      url: '/settings',
      icon: Settings2,
    },
  ];

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navMain} />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={{ name: user.name, email: user.email, avatar: '' }} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
