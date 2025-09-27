import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { config } from '@/lib/config';
import { AuthProvider } from '@/components/providers/auth-provider';
import { Nav } from '@/components/nav';

interface User {
  name: string;
  email: string;
  email_verified?: boolean;
  created_at: string;
  updated_at: string;
  id: string;
}

export async function getCurrentUser(): Promise<User> {
  const cooks = await cookies();
  const session = cooks.get('session')?.value;

  // No cookie at all → nothing to expire; just go to login
  if (!session || session === 'null') {
    redirect('/auth');
  }

  const response = await fetch(`${config.api.baseUrl}/users/current-user`, {
    headers: {
      cookie: `session=${session}`,
      'Content-Type': 'application/json',
    },
    cache: 'no-store',
  });

  if (response.status === 401) {
    redirect('/auth/expire');
  }

  if (!response.ok) {
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
