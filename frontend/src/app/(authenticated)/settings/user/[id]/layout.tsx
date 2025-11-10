'use client';

import { use, useEffect, type ReactNode } from 'react';
import { useUsersCurrentUserGetCurrentUser } from '@/openapi/users/users';
import { useRouter } from 'next/navigation';

export default function UserSettingsLayout({
  params,
  children,
}: {
  params: Promise<{ id: string }>;
  children: ReactNode;
}) {
  const { id } = use(params);
  const router = useRouter();

  const { data: currentUser } = useUsersCurrentUserGetCurrentUser();

  // Redirect if the ID in the URL doesn't match the current user
  useEffect(() => {
    if (currentUser && String(currentUser.id) !== id) {
      router.push(`/settings/user/${currentUser.id}`);
    }
  }, [currentUser, id, router]);

  return <>{children}</>;
}
