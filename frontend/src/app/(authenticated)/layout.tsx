import { cookies } from 'next/headers';
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
import type { GetCurrentUserUserResponseBody } from '@/openapi/managerLab.schemas';

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

// Per-session cache only here (30s)
const getCurrentUserCached = (session: string) =>
  unstable_cache(() => fetchCurrentUser(session), ['me', session], {
    revalidate: 30,
  })();

export async function getCurrentUser() {
  const store = await cookies(); // async on canary; drop await on stable
  const session = store.get('session')?.value;
  if (!session) redirect('/auth');
  return getCurrentUserCached(session);
}

export default async function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();

  return (
    <AuthProvider user={user}>
      <BreadcrumbProvider>
        <SidebarProvider>
          <AppSidebar />
          <SidebarInset>
            <header className="group-has-data-[collapsible=icon]/sidebar-wrapper:h-12 flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear">
              <div className="flex items-center gap-2 px-4">
                <SidebarTrigger className="-ml-1" />
                <Separator
                  orientation="vertical"
                  className="mr-2 data-[orientation=vertical]:h-4"
                />
                <DynamicBreadcrumb />
              </div>
            </header>
            <main className="flex-1 p-6">
              <ErrorBoundary>
                <SuspenseWrapper>{children}</SuspenseWrapper>
              </ErrorBoundary>
            </main>
          </SidebarInset>
        </SidebarProvider>
      </BreadcrumbProvider>
    </AuthProvider>
  );
}
