'use client';

import * as React from 'react';
import { ChevronsUpDown, Plus, Building2 } from 'lucide-react';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';
import { useAuth } from '@/components/providers/auth-provider';

export function TeamSwitcher({
  onAddTeamClick,
}: {
  onAddTeamClick?: () => void;
}) {
  const { isMobile } = useSidebar();
  const { teams, currentTeamId, isCampaignScoped, switchTeam } = useAuth();
  const [isSwitching, setIsSwitching] = React.useState(false);

  const activeTeam = teams.find((t) => t.team_id === currentTeamId) || teams[0];

  if (!activeTeam) {
    return null;
  }

  const handleTeamSwitch = async (teamId: number) => {
    if (isCampaignScoped || teamId === currentTeamId || isSwitching) {
      return;
    }

    setIsSwitching(true);
    try {
      await switchTeam(teamId);
    } catch (error) {
      console.error('Failed to switch team:', error);
      setIsSwitching(false);
    }
  };

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <SidebarMenuButton
              size="lg"
              className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
              disabled={isSwitching}
            >
              <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                <Building2 className="size-4" />
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-medium">
                  {activeTeam.team_name}
                </span>
                <span className="truncate text-xs">
                  {isCampaignScoped
                    ? 'Campaign Guest'
                    : activeTeam.role_level.charAt(0).toUpperCase() +
                      activeTeam.role_level.slice(1).toLowerCase()}
                </span>
              </div>
              {!isCampaignScoped && <ChevronsUpDown className="ml-auto" />}
            </SidebarMenuButton>
          </DropdownMenuTrigger>
          {!isCampaignScoped && (
            <DropdownMenuContent
              className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
              align="start"
              side={isMobile ? 'bottom' : 'right'}
              sideOffset={4}
            >
              <DropdownMenuLabel className="text-muted-foreground text-xs">
                Teams
              </DropdownMenuLabel>
              {teams.map((team, index) => (
                <DropdownMenuItem
                  key={team.team_id}
                  onClick={() => handleTeamSwitch(team.team_id)}
                  disabled={isSwitching || team.team_id === currentTeamId}
                  className="gap-2 p-2"
                >
                  <div className="flex size-6 items-center justify-center rounded-md border">
                    <Building2 className="size-3.5 shrink-0" />
                  </div>
                  <div className="flex flex-1 flex-col">
                    <span className="font-medium">{team.team_name}</span>
                    <span className="text-muted-foreground text-xs">
                      {team.role_level.charAt(0).toUpperCase() +
                        team.role_level.slice(1).toLowerCase()}
                    </span>
                  </div>
                  {team.team_id === currentTeamId && (
                    <span className="ml-auto text-xs">✓</span>
                  )}
                  {index < 9 && (
                    <DropdownMenuShortcut>⌘{index + 1}</DropdownMenuShortcut>
                  )}
                </DropdownMenuItem>
              ))}
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="gap-2 p-2"
                onClick={onAddTeamClick}
                disabled={isSwitching}
              >
                <div className="flex size-6 items-center justify-center rounded-md border bg-transparent">
                  <Plus className="size-4" />
                </div>
                <div className="text-muted-foreground font-medium">
                  Add team
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          )}
        </DropdownMenu>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
