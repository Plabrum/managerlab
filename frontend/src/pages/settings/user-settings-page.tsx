import { PageTopBar } from '@/components/page-topbar';
import { UserSettingsCard } from '@/components/settings/user-settings-card';
import { useUsersCurrentUserGetCurrentUserSuspense } from '@/openapi/users/users';

export function UserSettingsPage() {
  const { data: currentUser } = useUsersCurrentUserGetCurrentUserSuspense();

  return (
    <PageTopBar title="User Settings">
      <UserSettingsCard user={currentUser} />
    </PageTopBar>
  );
}
