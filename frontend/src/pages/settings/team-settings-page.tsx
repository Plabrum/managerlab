import { useParams } from '@tanstack/react-router';
import { ObjectActions } from '@/components/object-detail';
import { PageTopBar } from '@/components/page-topbar';
import { TeamMembersCard } from '@/components/settings/team-members-card';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { useTeamsIdGetTeamSuspense } from '@/openapi/teams/teams';
import { useUsersListUsersSuspense } from '@/openapi/users/users';

export function TeamSettingsPage() {
  const { id } = useParams({ from: '/_authenticated/settings/team/$id' });
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
