'use client';

import {
  UserSchema,
  TeamListItemSchema,
  ScopeType,
} from '@/openapi/ariveAPI.schemas';
import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { config } from '@/lib/config';

interface AuthContextValue {
  user: UserSchema;
  teams: TeamListItemSchema[];
  currentTeamId: string | null;
  isCampaignScoped: boolean;
  switchTeam: (teamId: string) => Promise<void>;
  refetchTeams: () => Promise<void>;
}

// Create context that *can* be null internally
const AuthCtx = createContext<AuthContextValue | null>(null);

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthCtx);
  if (!ctx) {
    throw new Error(
      'useAuth must be used within an <AuthProvider>. ' +
        'Did you forget to wrap your layout?'
    );
  }
  return ctx;
}

export function AuthProvider({
  user,
  initialTeams,
  children,
}: {
  user: UserSchema;
  initialTeams: TeamListItemSchema[];
  children: React.ReactNode;
}) {
  const [teamsData, setTeamsData] =
    useState<TeamListItemSchema[]>(initialTeams);
  const [isSwitchingTeam, setIsSwitchingTeam] = useState(false);
  const queryClient = useQueryClient();

  const refetchTeams = useCallback(async () => {
    const res = await fetch(`${config.api.baseUrl}/users/teams`, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
    });

    if (res.ok) {
      const data: TeamListItemSchema[] = await res.json();
      setTeamsData(data);
    }
  }, []);

  const switchTeam = useCallback(
    async (teamId: string) => {
      const res = await fetch(`${config.api.baseUrl}/users/switch-team`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({ team_id: teamId }),
      });

      if (res.ok) {
        // Invalidate all queries since team context has changed
        await queryClient.invalidateQueries();
        // Refetch teams to update the selected team
        await refetchTeams();
        // Reload the page to ensure all server components are refreshed
        window.location.reload();
      } else {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to switch team');
      }
    },
    [queryClient, refetchTeams]
  );

  // Auto-switch to first team if no scope is set
  useEffect(() => {
    const selectedTeam = teamsData.find((t) => t.is_selected);
    const isCampaignScoped = teamsData.some(
      (t) => t.scope_type === ScopeType.campaign
    );

    if (
      !isSwitchingTeam &&
      !selectedTeam &&
      !isCampaignScoped &&
      teamsData.length > 0
    ) {
      setIsSwitchingTeam(true);
      // Switch to first team automatically
      fetch(`${config.api.baseUrl}/users/switch-team`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({ team_id: teamsData[0].id }),
      })
        .then((res) => {
          if (res.ok) {
            // Refresh teams data to get updated is_selected flags
            return refetchTeams();
          }
        })
        .finally(() => {
          setIsSwitchingTeam(false);
        });
    }
  }, [teamsData, isSwitchingTeam, refetchTeams]);

  const selectedTeam = teamsData.find((t) => t.is_selected);
  const isCampaignScoped = teamsData.some(
    (t) => t.scope_type === ScopeType.campaign
  );

  const contextValue: AuthContextValue = {
    user,
    teams: teamsData,
    currentTeamId: (selectedTeam?.id as string | null) ?? null,
    isCampaignScoped,
    switchTeam,
    refetchTeams,
  };

  return <AuthCtx.Provider value={contextValue}>{children}</AuthCtx.Provider>;
}
