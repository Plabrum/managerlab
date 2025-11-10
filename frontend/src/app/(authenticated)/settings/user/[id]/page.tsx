'use client';

import { useUsersCurrentUserGetCurrentUserSuspense } from '@/openapi/users/users';
import { PageTopBar } from '@/components/page-topbar';
import { UserSettingsCard } from '@/components/settings/user-settings-card';

export default function UserSettingsPage() {
  const { data: currentUser } = useUsersCurrentUserGetCurrentUserSuspense();

  return (
    <PageTopBar title="User Settings">
      <UserSettingsCard user={currentUser} />
    </PageTopBar>
  );
}
