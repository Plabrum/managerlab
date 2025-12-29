import { z } from 'zod';
import { PageTopBar } from '@/components/page-topbar';
import { UserSettingsCard } from '@/components/settings/user-settings-card';
import { useUsersCurrentUserGetCurrentUserSuspense } from '@/openapi/users/users';
import ErrorPage from '@/pages/error-page';

const searchSchema = z.object({
  edit: z.boolean().optional(),
});

export function UserSettingsPage() {
  const { data: currentUser } = useUsersCurrentUserGetCurrentUserSuspense();

  return (
    <PageTopBar title="User Settings">
      <UserSettingsCard user={currentUser} />
    </PageTopBar>
  );
}
