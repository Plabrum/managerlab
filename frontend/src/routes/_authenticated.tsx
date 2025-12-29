import { useEffect } from 'react';
import {
  createFileRoute,
  Outlet,
  redirect,
  useLocation,
  useNavigate,
} from '@tanstack/react-router';
import { AppSidebar } from '@/components/app-sidebar';
import { ErrorBoundary } from '@/components/error-boundary';
import { AuthProvider } from '@/components/providers/auth-provider';
import { SuspenseWrapper } from '@/components/suspense-wrapper';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import { useTeamsListTeams } from '@/openapi/teams/teams';
import { useUsersCurrentUserGetCurrentUser } from '@/openapi/users/users';

export const Route = createFileRoute('/_authenticated')({
  component: AuthenticatedLayoutComponent,
  errorComponent: ({ error }) => {
    // Handle authentication errors
    if (error && typeof error === 'object' && 'status' in error) {
      const status = (error as { status: number }).status;
      if (status === 401) {
        document.cookie =
          'session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax';
        throw redirect({ to: '/auth', replace: true });
      }
    }
    throw redirect({ to: '/error', replace: true });
  },
});

function AuthenticatedLayoutComponent() {
  const navigate = useNavigate();
  const location = useLocation();
  const isOnboardingPage = location.pathname.includes('/onboarding');

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
        // Clear session and redirect to auth
        document.cookie =
          'session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax';
        navigate({ to: '/auth', replace: true });
      } else {
        navigate({ to: '/error', replace: true });
      }
    }
  }, [userError, teamsError, navigate]);

  // Redirect to onboarding if user has no teams and not already on onboarding page
  useEffect(() => {
    if (teams && teams.length === 0 && !isOnboardingPage) {
      navigate({ to: '/onboarding', replace: true });
    }
  }, [teams, isOnboardingPage, navigate]);

  // Show loading state while fetching initial data
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

  // Explicit check for TypeScript
  if (!user || !teams) {
    return null;
  }

  // If on onboarding page, render without sidebar
  if (isOnboardingPage) {
    return (
      <AuthProvider user={user} initialTeams={teams}>
        <ErrorBoundary>
          <SuspenseWrapper>
            <Outlet />
          </SuspenseWrapper>
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
              <SuspenseWrapper>
                <Outlet />
              </SuspenseWrapper>
            </ErrorBoundary>
          </main>
        </SidebarInset>
      </SidebarProvider>
    </AuthProvider>
  );
}
