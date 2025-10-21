import { cookies, headers } from 'next/headers';
import { redirect } from 'next/navigation';
import { unstable_cache } from 'next/cache';
import { config } from '@/lib/config';
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
import type {
  GetCurrentUserUserResponseBody,
  ListTeamsResponse,
} from '@/openapi/managerLab.schemas';
import { DynamicPageActions } from '@/components/dynamic-page-actions';

async function fetchCurrentUser(
  session: string
): Promise<GetCurrentUserUserResponseBody> {
  const res = await fetch(`${config.api.baseUrl}/users/current_user`, {
    headers: {
      Cookie: `session=${session}`,
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    cache: 'no-store',
  });

  if (res.status === 401) redirect('/auth/expire');
  if (!res.ok) redirect('/auth');
  return res.json();
}

async function fetchTeams(session: string): Promise<ListTeamsResponse> {
  const res = await fetch(`${config.api.baseUrl}/users/teams`, {
    headers: {
      Cookie: `session=${session}`,
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    cache: 'no-store',
  });

  if (res.status === 401) redirect('/auth/expire');
  if (!res.ok) redirect('/auth');
  return res.json();
}

// Per-session cache only here (30s)
const getCurrentUserCached = (session: string) =>
  unstable_cache(() => fetchCurrentUser(session), ['me', session], {
    revalidate: 30,
  })();

const getTeamsCached = (session: string) =>
  unstable_cache(() => fetchTeams(session), ['teams', session], {
    revalidate: 30,
  })();

export default async function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const store = await cookies();
  const session = store.get('session')?.value;
  if (!session) redirect('/auth');

  const [user, teams] = await Promise.all([
    getCurrentUserCached(session),
    getTeamsCached(session),
  ]);

  // Get current pathname to check if we're on onboarding
  const headersList = await headers();
  const pathname = headersList.get('x-pathname') || '';

  // If user has no teams and not on onboarding page, redirect to onboarding
  const hasNoTeams = teams.teams.length === 0;
  const isOnboardingPage = pathname.includes('/onboarding');

  if (hasNoTeams && !isOnboardingPage) {
    redirect('/onboarding');
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
