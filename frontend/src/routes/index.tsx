import { createFileRoute, redirect } from '@tanstack/react-router';
import { LandingPage } from '@/components/landing-page';

export const Route = createFileRoute('/')({
  component: HomePage,
  beforeLoad: () => {
    // Check for session cookie
    const hasSession =
      document.cookie.includes('session=') &&
      !document.cookie.includes('session=null') &&
      !document.cookie.includes('session=;');

    if (hasSession) {
      throw redirect({ to: '/dashboard', replace: true });
    }
  },
});

function HomePage() {
  return <LandingPage />;
}
