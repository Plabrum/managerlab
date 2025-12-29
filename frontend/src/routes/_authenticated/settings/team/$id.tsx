import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import ErrorPage from '@/routes/_public/error';
import { ObjectActions } from '@/components/object-detail';
import { PageTopBar } from '@/components/page-topbar';
import { TeamMembersCard } from '@/components/settings/team-members-card';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';
import { useTeamsIdGetTeamSuspense } from '@/openapi/teams/teams';
import { useUsersListUsersSuspense } from '@/openapi/users/users';

const searchSchema = z.object({
  edit: z.boolean().optional(),
});

export const Route = createFileRoute('/_authenticated/settings/team/$id')({
  component: TeamSettingsPage,
  validateSearch: searchSchema,
  errorComponent: ({ error }) => {
    if (
      error &&
      typeof error === 'object' &&
      'status' in error &&
      error.status === 404
    ) {
      return <ErrorPage />;
    }
    throw error;
  },
});

function TeamSettingsPage() {
  const { id } = Route.useParams();
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
