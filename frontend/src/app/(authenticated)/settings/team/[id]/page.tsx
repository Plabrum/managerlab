'use client';

import { use } from 'react';
import { useUsersListUsersSuspense } from '@/openapi/users/users';
import { useTeamsIdGetTeamSuspense } from '@/openapi/teams/teams';
import { PageTopBar } from '@/components/page-topbar';
import { TeamMembersCard } from '@/components/settings/team-members-card';
import { ObjectActions } from '@/components/object-detail';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';

export default function TeamSettingsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: users } = useUsersListUsersSuspense();
  const { data: team, refetch } = useTeamsIdGetTeamSuspense(id);

  return (
    <PageTopBar
      title={team.name}
      actions={
        <ObjectActions
          data={team}
          actionGroup={ActionGroupType.team_actions}
          onRefetch={refetch}
        />
      }
    >
      <TeamMembersCard users={users} />
    </PageTopBar>
  );
}
