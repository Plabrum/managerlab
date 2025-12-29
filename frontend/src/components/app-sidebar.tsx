import { LayoutDashboard, FolderKanban } from 'lucide-react';
import * as React from 'react';
import { CreateTeamModal } from '@/components/create-team-modal';
import { NavMain } from '@/components/nav-main';
import { NavUser } from '@/components/nav-user';
import { useAuth } from '@/components/providers/auth-provider';
import { TeamSwitcher } from '@/components/team-switcher';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from '@/components/ui/sidebar';

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { user } = useAuth();
  const [isTeamModalOpen, setIsTeamModalOpen] = React.useState(false);

  const navMain = [
    {
      title: 'Dashboard',
      url: '/dashboard',
      icon: LayoutDashboard,
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
          title: 'Deliverables',
          url: '/deliverables',
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
