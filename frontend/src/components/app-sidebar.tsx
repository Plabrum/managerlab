'use client';

import * as React from 'react';
import { LayoutDashboard, FolderKanban } from 'lucide-react';

import { NavMain } from '@/components/nav-main';
import { NavUser } from '@/components/nav-user';
import { TeamSwitcher } from '@/components/team-switcher';
import { CreateTeamModal } from '@/components/create-team-modal';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from '@/components/ui/sidebar';
import { useAuth } from '@/components/providers/auth-provider';
import { dashboardsListDashboards } from '@/openapi/dashboards/dashboards';
import type { ListDashboardsDashboardResponseBody } from '@/openapi/managerLab.schemas';

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { user } = useAuth();
  const [isTeamModalOpen, setIsTeamModalOpen] = React.useState(false);
  const [dashboards, setDashboards] = React.useState<
    ListDashboardsDashboardResponseBody[]
  >([]);

  React.useEffect(() => {
    const fetchDashboards = async () => {
      try {
        const data = await dashboardsListDashboards();
        setDashboards(data);
      } catch (error) {
        console.error('Failed to fetch dashboards:', error);
      }
    };

    fetchDashboards();
  }, []);

  const dashboardItems =
    dashboards.length > 0
      ? dashboards.map((dashboard) => ({
          title: dashboard.name,
          url: `/dashboard/${dashboard.id}`,
        }))
      : undefined;

  const navMain = [
    {
      title: 'Dashboard',
      url: '/dashboard',
      icon: LayoutDashboard,
      items: dashboardItems,
    },
    {
      title: 'Management',
      url: '#',
      icon: FolderKanban,
      items: [
        {
          title: 'Campaigns',
          url: '/campaigns',
        },
        {
          title: 'Brands',
          url: '/brands',
        },
        {
          title: 'Roster',
          url: '/roster',
        },
        {
          title: 'Posts',
          url: '/posts',
        },
        {
          title: 'Media',
          url: '/media',
        },
        {
          title: 'Invoices',
          url: '/invoices',
        },
      ],
    },
  ];

  return (
    <>
      <Sidebar collapsible="icon" {...props}>
        <SidebarHeader>
          <TeamSwitcher onAddTeamClick={() => setIsTeamModalOpen(true)} />
        </SidebarHeader>
        <SidebarContent>
          <NavMain items={navMain} />
        </SidebarContent>
        <SidebarFooter>
          <NavUser user={{ name: user.name, email: user.email, avatar: '' }} />
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>
      <CreateTeamModal
        open={isTeamModalOpen}
        onOpenChange={setIsTeamModalOpen}
      />
    </>
  );
}
