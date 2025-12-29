import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import ErrorPage from '@/routes/_public/error';
import { PageTopBar } from '@/components/page-topbar';
import { UserSettingsCard } from '@/components/settings/user-settings-card';
import { useUsersCurrentUserGetCurrentUserSuspense } from '@/openapi/users/users';

const searchSchema = z.object({
  edit: z.boolean().optional(),
});

export const Route = createFileRoute('/_authenticated/settings/user/$id')({
  component: UserSettingsPage,
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

function UserSettingsPage() {
  const { data: currentUser } = useUsersCurrentUserGetCurrentUserSuspense();

  return (
    <PageTopBar title="User Settings">
      <UserSettingsCard user={currentUser} />
    </PageTopBar>
  );
}
