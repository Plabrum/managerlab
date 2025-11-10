'use client';

import * as React from 'react';
import { ChevronsUpDown, Plus, Building2 } from 'lucide-react';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from '@/components/ui/sidebar';
import { useAuth } from '@/components/providers/auth-provider';
import { ActionsMenu } from '@/components/actions-menu';
import type { ActionDTO } from '@/openapi/ariveAPI.schemas';

export function TeamSwitcher({
  onAddTeamClick,
}: {
  onAddTeamClick?: () => void;
}) {
  const { isMobile } = useSidebar();
  const { teams, currentTeamId, isCampaignScoped, switchTeam, refetchTeams } =
    useAuth();
  const [isSwitching, setIsSwitching] = React.useState(false);

  const handleTeamSwitch = React.useCallback(
    async (teamId: number) => {
      if (isCampaignScoped || teamId === currentTeamId || isSwitching) {
        return;
      }

      setIsSwitching(true);
      try {
        await switchTeam(teamId);
        // Note: page will reload on success, so no need to reset state
      } catch (error) {
        console.error('Failed to switch team:', error);
        setIsSwitching(false);
      }
    },
    [isCampaignScoped, currentTeamId, isSwitching, switchTeam]
  );

  const activeTeam = teams.find((t) => t.team_id === currentTeamId) || teams[0];

  if (!activeTeam) {
    return null;
  }

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
              {teams.map((team) => (
                <TeamMenuItem
                  key={team.team_id}
                  team={team}
                  isActive={team.team_id === currentTeamId}
                  isSwitching={isSwitching}
                  onSwitch={handleTeamSwitch}
                  onActionComplete={refetchTeams}
                />
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

interface TeamMenuItemProps {
  team: {
    team_id: number;
    public_id: string;
    team_name: string;
    role_level: string;
    actions?: ActionDTO[];
  };
  isActive: boolean;
  isSwitching: boolean;
  onSwitch: (teamId: number) => void;
  onActionComplete: () => void;
}

function TeamMenuItem({
  team,
  isActive,
  isSwitching,
  onSwitch,
  onActionComplete,
}: TeamMenuItemProps) {
  // Use actions from team data (already fetched in teams list)
  const actions = team.actions || [];
  const hasActions = actions.length > 0;

  return (
    <DropdownMenuItem
      onClick={() => onSwitch(team.team_id)}
      disabled={isSwitching || isActive}
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
      {isActive && <span className="ml-auto text-xs">✓</span>}
      {hasActions && (
        <div onClick={(e) => e.stopPropagation()}>
          <ActionsMenu
            actions={actions}
            actionGroup="team_actions"
            objectId={team.public_id}
            onActionComplete={onActionComplete}
          />
        </div>
      )}
    </DropdownMenuItem>
  );
}
