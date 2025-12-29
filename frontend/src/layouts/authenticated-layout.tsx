import { Outlet, useLocation } from '@tanstack/react-router';
import { AppSidebar } from '@/components/app-sidebar';
import { ErrorBoundary } from '@/components/error-boundary';
import { AuthProvider } from '@/components/providers/auth-provider';
import { SuspenseWrapper } from '@/components/suspense-wrapper';
import { SidebarInset, SidebarProvider } from '@/components/ui/sidebar';
import type {
  UserSchema,
  TeamListItemSchema,
} from '@/openapi/ariveAPI.schemas';

interface AuthenticatedLayoutProps {
  user: UserSchema;
  teams: TeamListItemSchema[];
}

export function AuthenticatedLayout({ user, teams }: AuthenticatedLayoutProps) {
  const location = useLocation();
  const isOnboardingPage = location.pathname.includes('/onboarding');

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
