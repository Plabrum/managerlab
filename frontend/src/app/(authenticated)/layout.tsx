'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { AuthProvider } from '@/components/providers/auth-provider';
import { ErrorBoundary } from '@/components/error-boundary';
import { SuspenseWrapper } from '@/components/suspense-wrapper';
import { AppSidebar } from '@/components/app-sidebar';
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import { DynamicBreadcrumb } from '@/components/dynamic-breadcrumb';
import { BreadcrumbProvider } from '@/components/breadcrumb-provider';
import { DynamicPageHeader } from '@/components/dynamic-page-header';
import { HeaderProvider } from '@/components/header-provider';
import { DynamicPageActions } from '@/components/dynamic-page-actions';
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
      retry: false,
      staleTime: 30000, // 30s cache
    },
  });

  const {
    data: teams,
    isLoading: teamsLoading,
    error: teamsError,
  } = useUsersTeamsListTeams({
    query: {
      retry: false,
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

  console.log('Rendering AuthenticatedLayout for user:', user.email);
  // Normal layout with sidebar for users with teams
  return (
    <AuthProvider user={user} initialTeams={teams}>
      <BreadcrumbProvider>
        <HeaderProvider>
          <SidebarProvider>
            <AppSidebar />
            <SidebarInset>
              <header className="group-has-data-[collapsible=icon]/sidebar-wrapper:h-12 flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear">
                <div className="grid w-full grid-cols-3 items-center px-4">
                  <div className="flex items-center justify-start gap-2">
                    <SidebarTrigger className="-ml-1" />
                    <Separator
                      orientation="vertical"
                      className="mr-2 data-[orientation=vertical]:h-4"
                    />
                    <DynamicBreadcrumb />
                  </div>

                  <div className="flex justify-center">
                    <DynamicPageHeader />
                  </div>

                  <div className="flex justify-end">
                    <DynamicPageActions />
                  </div>
                </div>
              </header>
              <main className="flex-1 p-6">
                <ErrorBoundary>
                  <SuspenseWrapper>{children}</SuspenseWrapper>
                </ErrorBoundary>
              </main>
            </SidebarInset>
          </SidebarProvider>
        </HeaderProvider>
      </BreadcrumbProvider>
    </AuthProvider>
  );
}
