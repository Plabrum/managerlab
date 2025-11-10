'use client';

import { use } from 'react';
import { useUsersCurrentUserGetCurrentUser } from '@/openapi/users/users';
import { PageTopBar } from '@/components/page-topbar';
import { UserSettingsCard } from '@/components/settings/user-settings-card';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function UserSettingsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();

  const { data: currentUser, isLoading } = useUsersCurrentUserGetCurrentUser();

  // Redirect if the ID in the URL doesn't match the current user
  useEffect(() => {
    if (currentUser && String(currentUser.id) !== id) {
      router.push(`/settings/user/${currentUser.id}`);
    }
  }, [currentUser, id, router]);

  if (isLoading || !currentUser) {
    return null;
  }

  return (
    <PageTopBar title="User Settings">
      <UserSettingsCard user={currentUser} />
    </PageTopBar>
  );
}
