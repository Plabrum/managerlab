import { createFileRoute } from '@tanstack/react-router';
import { LandingPage } from '@/components/landing-page';

export const Route = createFileRoute('/_public/landing')({
  component: LandingPage,
});

function Landing() {
  return <LandingPage />;
}
