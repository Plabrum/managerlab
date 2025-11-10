'use client';

import { use, useEffect, type ReactNode } from 'react';
import { useAuth } from '@/components/providers/auth-provider';
import { useRouter } from 'next/navigation';

export default function TeamSettingsLayout({
  params,
  children,
}: {
  params: Promise<{ id: string }>;
  children: ReactNode;
}) {
  const { id } = use(params);
  const router = useRouter();
  const { teams } = useAuth();

  // Find the current team to verify the ID matches
  const currentTeam = teams.find((t) => t.is_selected);

  // Redirect if the ID in the URL doesn't match the current team's id
  useEffect(() => {
    if (currentTeam && currentTeam.id !== id) {
      router.push(`/settings/team/${currentTeam.id}`);
    }
  }, [currentTeam, id, router]);

  return <>{children}</>;
}
