import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import {
  usersCurrentUserGetCurrentUser,
  type GetUserUserResponseBody,
} from '@/server-sdk';
import { AuthProvider } from '@/components/provers/auth-provider';
import { Nav } from '@/components/nav';

export async function getCurrentUser(): Promise<GetUserUserResponseBody> {
  const cooks = await cookies();
  const session = cooks.get('session')?.value;

  // No cookie at all → nothing to expire; just go to login
  if (!session || session === 'null') {
    redirect('/auth');
  }

  const { data: user, status } = await usersCurrentUserGetCurrentUser({
    headers: { cookie: `session=${session}` },
    cache: 'no-store',
  });

  console.log('Fetched current user:', user, status);

  if (Number(status) === 401) {
    redirect('/auth/expire');
  } else if (!user) {
    return redirect('/auth');
  } else return user;
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
