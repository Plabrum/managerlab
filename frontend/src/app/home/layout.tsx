import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import {
  usersCurrentUserGetCurrentUser,
  GetUserUserResponseBody,
} from '@/server-sdk';
import { AuthProvider } from '@/components/provers/auth-provider';

async function getCurrentUser(): Promise<GetUserUserResponseBody | null> {
  const cookieStore = await cookies();
  const cookieHeader = cookieStore.toString();

  try {
    const { data: user } = await usersCurrentUserGetCurrentUser({
      headers: { cookie: cookieHeader },
      cache: 'no-store',
    });
    return user ?? null;
  } catch (error) {
    console.error('Failed to fetch current user:', error);
    return null;
  }
}

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getCurrentUser();
  if (!user) redirect('/login');
  return <AuthProvider user={user}>{children}</AuthProvider>;
}
