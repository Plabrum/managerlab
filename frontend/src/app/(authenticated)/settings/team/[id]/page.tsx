'use client';

import { useUsersListUsersSuspense } from '@/openapi/users/users';
import { PageTopBar } from '@/components/page-topbar';
import { TeamMembersCard } from '@/components/settings/team-members-card';
import { ObjectActions } from '@/components/object-detail';
import { useAuth } from '@/components/providers/auth-provider';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';

export default function TeamSettingsPage() {
  const { data: users } = useUsersListUsersSuspense();
  const { teams, refetchTeams } = useAuth();

  const currentTeam = teams.find((t) => t.is_selected);

  if (!currentTeam) {
    return null;
  }

  return (
    <PageTopBar
      title="Team Settings"
      actions={
        <ObjectActions
          data={currentTeam}
          actionGroup={ActionGroupType.team_actions}
          onRefetch={refetchTeams}
        />
      }
    >
      <TeamMembersCard users={users} />
    </PageTopBar>
  );
}
