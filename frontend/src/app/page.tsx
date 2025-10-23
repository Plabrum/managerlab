import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { LandingPage } from '@/components/landing-page';

async function checkValidSession(): Promise<boolean> {
  const cookieStore = await cookies();

  // Check for valid session cookie - treat 'null' as no session
  const sessionCookie = cookieStore.get('session');
  // No cookie, or empty value, or explicit 'null' value = not authenticated
  if (
    !sessionCookie ||
    !sessionCookie.value ||
    sessionCookie.value === 'null'
  ) {
    return false;
  }

  return true;
}

export default async function HomePage() {
  const hasValidSession = await checkValidSession();

  // If user has a valid session cookie, redirect to dashboard
  if (hasValidSession) {
    redirect('/dashboard');
  }

  // If no valid session, show the landing page (SSG-friendly)
  return <LandingPage />;
}
