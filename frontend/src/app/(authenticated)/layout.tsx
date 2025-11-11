'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { AuthProvider } from '@/components/providers/auth-provider';
import { ErrorBoundary } from '@/components/error-boundary';
import { SuspenseWrapper } from '@/components/suspense-wrapper';
import { AppSidebar } from '@/components/app-sidebar';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import { useUsersCurrentUserGetCurrentUser } from '@/openapi/users/users';
import { useTeamsListTeams } from '@/openapi/teams/teams';

export default function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const isOnboardingPage = pathname.includes('/onboarding');

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
  } = useTeamsListTeams({
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
        router.push('/error');
      }
    }
  }, [userError, teamsError, router]);

  // Redirect to onboarding if user has no teams and not already on onboarding page
  useEffect(() => {
    if (teams && teams.length === 0 && !isOnboardingPage) {
      router.push('/onboarding');
    }
  }, [teams, isOnboardingPage, router]);

  // Show loading state while fetching initial data
  // Don't show loading if there's an error (redirect will happen)
  if (
    (userLoading || teamsLoading || !user || !teams) &&
    !userError &&
    !teamsError
  ) {
    return null; // Or a loading spinner
  }

  // If there's an error, show nothing while redirecting
  if (userError || teamsError) {
    return null;
  }

  // At this point, TypeScript knows user and teams are defined
  // but we need to help it with an explicit check
  if (!user || !teams) {
    return null;
  }

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
