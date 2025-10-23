'use client';

import {
  GetUserUserResponseBody,
  ListTeamsResponse,
  TeamListItemSchema,
} from '@/openapi/managerLab.schemas';
import { createContext, useContext, useState, useCallback } from 'react';
import { config } from '@/lib/config';

interface AuthContextValue {
  user: GetUserUserResponseBody;
  teams: TeamListItemSchema[];
  currentTeamId: number | null;
  isCampaignScoped: boolean;
  switchTeam: (teamId: number) => Promise<void>;
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
  user: GetUserUserResponseBody;
  initialTeams: ListTeamsResponse;
  children: React.ReactNode;
}) {
  const [teamsData, setTeamsData] = useState<ListTeamsResponse>(initialTeams);

  const refetchTeams = useCallback(async () => {
    const res = await fetch(`${config.api.baseUrl}/users/teams`, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
    });

    if (res.ok) {
      const data: ListTeamsResponse = await res.json();
      setTeamsData(data);
    }
  }, []);

  const switchTeam = useCallback(async (teamId: number) => {
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
      // Reload the page to fetch fresh data with the new team context
      window.location.reload();
    } else {
      const error = await res.json();
      throw new Error(error.detail || 'Failed to switch team');
    }
  }, []);

  const contextValue: AuthContextValue = {
    user,
    teams: teamsData.teams,
    currentTeamId: teamsData.current_team_id ?? null,
    isCampaignScoped: teamsData.is_campaign_scoped,
    switchTeam,
    refetchTeams,
  };

  return <AuthCtx.Provider value={contextValue}>{children}</AuthCtx.Provider>;
}
