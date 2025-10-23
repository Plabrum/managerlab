'use client';

import * as React from 'react';
import { ChevronsUpDown, Plus, Building2, MoreHorizontal } from 'lucide-react';

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
import { Button } from '@/components/ui/button';
import { useAuth } from '@/components/providers/auth-provider';
import { useActionsActionGroupObjectIdListObjectActions } from '@/openapi/actions/actions';
import { useActionExecutor } from '@/hooks/use-action-executor';
import { ActionConfirmationDialog } from '@/components/actions/action-confirmation-dialog';
import type { ActionDTO } from '@/openapi/managerLab.schemas';

export function TeamSwitcher({
  onAddTeamClick,
}: {
  onAddTeamClick?: () => void;
}) {
  const { isMobile } = useSidebar();
  const { teams, currentTeamId, isCampaignScoped, switchTeam, refetchTeams } =
    useAuth();
  const [isSwitching, setIsSwitching] = React.useState(false);
  const [actionsMenuTeamId, setActionsMenuTeamId] = React.useState<
    string | null
  >(null);

  // Action executor for team actions (must be before early return)
  const teamActionExecutor = useActionExecutor({
    actionGroup: 'team_actions',
    objectId: actionsMenuTeamId || undefined,
    onSuccess: async () => {
      // Refetch teams after successful action
      await refetchTeams();
      setActionsMenuTeamId(null);
    },
  });

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

  const handleTeamActionClick = (
    e: React.MouseEvent,
    publicId: string,
    action: ActionDTO
  ) => {
    e.stopPropagation();
    setActionsMenuTeamId(publicId);
    teamActionExecutor.initiateAction(action);
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
                <TeamMenuItem
                  key={team.team_id}
                  team={team}
                  index={index}
                  isActive={team.team_id === currentTeamId}
                  isSwitching={isSwitching}
                  onSwitch={handleTeamSwitch}
                  onActionClick={handleTeamActionClick}
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

      <ActionConfirmationDialog
        open={teamActionExecutor.showConfirmation}
        action={teamActionExecutor.pendingAction}
        isExecuting={teamActionExecutor.isExecuting}
        onConfirm={teamActionExecutor.confirmAction}
        onCancel={teamActionExecutor.cancelAction}
      />
    </SidebarMenu>
  );
}

interface TeamMenuItemProps {
  team: {
    team_id: number;
    public_id: string;
    team_name: string;
    role_level: string;
  };
  index: number;
  isActive: boolean;
  isSwitching: boolean;
  onSwitch: (teamId: number) => void;
  onActionClick: (
    e: React.MouseEvent,
    publicId: string,
    action: ActionDTO
  ) => void;
}

function TeamMenuItem({
  team,
  index,
  isActive,
  isSwitching,
  onSwitch,
  onActionClick,
}: TeamMenuItemProps) {
  const [showActionsMenu, setShowActionsMenu] = React.useState(false);

  // Fetch team actions for this team
  const { data: actionsData } = useActionsActionGroupObjectIdListObjectActions(
    'team_actions',
    team.public_id,
    {
      query: {
        enabled: showActionsMenu,
      },
    }
  );

  const actions = actionsData?.actions || [];
  const hasActions = actions.length > 0;

  return (
    <DropdownMenuItem
      onClick={() => onSwitch(team.team_id)}
      disabled={isSwitching || isActive}
      className="gap-2 p-2"
      onMouseEnter={() => setShowActionsMenu(true)}
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
        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              <MoreHorizontal className="h-4 w-4" />
              <span className="sr-only">Team actions</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" onClick={(e) => e.stopPropagation()}>
            {actions.map((action) => (
              <DropdownMenuItem
                key={action.action}
                onClick={(e) => onActionClick(e, team.public_id, action)}
                className="cursor-pointer"
              >
                {action.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      )}
      {!hasActions && index < 9 && (
        <DropdownMenuShortcut>⌘{index + 1}</DropdownMenuShortcut>
      )}
    </DropdownMenuItem>
  );
}
