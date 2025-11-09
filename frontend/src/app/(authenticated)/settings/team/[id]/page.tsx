'use client';

import { use } from 'react';
import { useUsersListUsers } from '@/openapi/users/users';
import { PageTopBar } from '@/components/page-topbar';
import { TeamMembersCard } from '@/components/settings/team-members-card';
import { Button } from '@/components/ui/button';
import { UserPlus } from 'lucide-react';
import { useAuth } from '@/components/providers/auth-provider';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function TeamSettingsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { teams, currentTeamId } = useAuth();

  const { data: users, isLoading } = useUsersListUsers();

  // Find the current team to verify the ID matches
  const currentTeam = teams.find((t) => t.team_id === currentTeamId);

  // Redirect if the ID in the URL doesn't match the current team's public_id
  useEffect(() => {
    if (currentTeam && currentTeam.public_id !== id) {
      router.push(`/settings/team/${currentTeam.public_id}`);
    }
  }, [currentTeam, id, router]);

  if (isLoading || !users) {
    return null;
  }

  const handleInviteUser = () => {
    // TODO: Implement user invitation flow
    console.log('Invite user clicked');
  };

  return (
    <PageTopBar
      title="Team Settings"
      actions={
        <Button onClick={handleInviteUser} size="sm">
          <UserPlus className="mr-2 h-4 w-4" />
          Invite User
        </Button>
      }
    >
      <TeamMembersCard users={users} />
    </PageTopBar>
  );
}
