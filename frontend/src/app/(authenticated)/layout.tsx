'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { AuthProvider } from '@/components/providers/auth-provider';
import { ErrorBoundary } from '@/components/error-boundary';
import { SuspenseWrapper } from '@/components/suspense-wrapper';
import { AppSidebar } from '@/components/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import {
  useUsersCurrentUserGetCurrentUser,
  useUsersTeamsListTeams,
} from '@/openapi/users/users';

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();

  // Fetch user and teams data client-side
  const {
    data: user,
    isLoading: userLoading,
    error: userError,
  } = useUsersCurrentUserGetCurrentUser({
    query: {
      staleTime: 30000, // 30s cache
    },
  });

  const {
    data: teams,
    isLoading: teamsLoading,
    error: teamsError,
  } = useUsersTeamsListTeams({
    query: {
      staleTime: 0, // No cache for teams to ensure immediate updates after onboarding
    },
  });

  // Handle authentication errors
  useEffect(() => {
    if (userError || teamsError) {
      const errorResponse = userError || teamsError;
      if (
        errorResponse &&
        typeof errorResponse === 'object' &&
        'status' in errorResponse &&
        errorResponse.status === 401
      ) {
        router.push('/auth/expire');
      } else {
        router.push('/auth');
      }
    }
  }, [userError, teamsError, router]);

  // Handle onboarding redirect
  useEffect(() => {
    if (!teamsLoading && teams && !userLoading && user) {
      const hasNoTeams = teams.teams.length === 0;
      const isOnboardingPage = pathname.includes('/onboarding');

      if (hasNoTeams && !isOnboardingPage) {
        router.push('/onboarding');
      }
    }
  }, [teams, teamsLoading, user, userLoading, pathname, router]);

  // Show loading state while fetching initial data
  if (userLoading || teamsLoading || !user || !teams) {
    return null; // Or a loading spinner
  }

  const isOnboardingPage = pathname.includes('/onboarding');

  // If on onboarding page, render without sidebar
  if (isOnboardingPage) {
    return (
      <AuthProvider user={user} initialTeams={teams}>
        <ErrorBoundary>
          <SuspenseWrapper>{children}</SuspenseWrapper>
        </ErrorBoundary>
      </AuthProvider>
    );
  }

  // Normal layout with sidebar for users with teams
  return (
    <AuthProvider user={user} initialTeams={teams}>
      <SidebarProvider defaultOpen={false}>
        <AppSidebar />
        <SidebarInset>
          <main className="flex flex-1 flex-col">
            <ErrorBoundary>
              <SuspenseWrapper>{children}</SuspenseWrapper>
            </ErrorBoundary>
          </main>
        </SidebarInset>
      </SidebarProvider>
    </AuthProvider>
  );
}
