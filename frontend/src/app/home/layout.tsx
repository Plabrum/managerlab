import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import {
  usersCurrentUserGetCurrentUser,
  GetUserUserResponseBody,
} from '@/server-sdk';
import { AuthProvider } from '@/components/provers/auth-provider';

async function getCurrentUser(): Promise<GetUserUserResponseBody | null> {
  const cookieHeader = cookies().toString();
  const { data: user } = await usersCurrentUserGetCurrentUser({
    headers: { cookie: cookieHeader },
    cache: 'no-store',
  });
  return user ?? null;
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
