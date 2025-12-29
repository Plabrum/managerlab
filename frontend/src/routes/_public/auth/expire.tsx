import { createFileRoute, redirect } from '@tanstack/react-router';

export const Route = createFileRoute('/_public/auth/expire')({
  beforeLoad: () => {
    // Clear session cookie on client side
    document.cookie =
      'session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax';
    throw redirect({ to: '/auth', replace: true });
  },
});
