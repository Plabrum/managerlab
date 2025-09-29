import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { config } from '@/lib/config';
import { AuthProvider } from '@/components/providers/auth-provider';
import { Nav } from '@/components/nav';
import { ErrorBoundary } from '@/components/error-boundary';
import { SuspenseWrapper } from '@/components/suspense-wrapper';
import { GetCurrentUserUserResponseBody } from '@/openapi/managerLab.schemas';
import { toast } from 'sonner';

export async function getCurrentUser(): Promise<GetCurrentUserUserResponseBody> {
  const cooks = await cookies();

  // Build cookie string from all cookies
  const cookieString = cooks
    .getAll()
    .map((cookie) => `${cookie.name}=${cookie.value}`)
    .join('; ');

  if (!cookieString) {
    redirect('/auth');
  }

  const response = await fetch(`${config.api.baseUrl}/users/current-user`, {
    headers: {
      Cookie: cookieString,
      'Content-Type': 'application/json',
    },
    cache: 'no-store',
  });

  if (response.status === 401) {
    redirect('/auth/expire');
  }

  if (!response.ok) {
    toast.error('Failed to fetch user data. Please log in again.');
    redirect('/auth');
  }

  const user = await response.json();
  return user;
}

export default async function AuthenticatedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();

  return (
    <AuthProvider user={user}>
      <Nav>
        <main className="flex-1 p-6">{children}</main>
      </Nav>
    </AuthProvider>
  );
}
