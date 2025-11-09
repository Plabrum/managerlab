'use client';

import { Button } from '@/components/ui/button';
import { useAuthLogoutLogoutUser } from '@/openapi/auth/auth';
import { useRouter } from 'next/navigation';
import { useState } from 'react';

export function LogoutButton() {
  const router = useRouter();
  const [isSigningOut, setIsSigningOut] = useState(false);

  const { mutate: logout } = useAuthLogoutLogoutUser({
    mutation: {
      onSuccess: () => {
        router.push('/');
        router.refresh();
      },
      onError: (error) => {
        console.error('Logout failed:', error);
        router.push('/');
        router.refresh();
      },
      onSettled: () => {
        setIsSigningOut(false);
      },
    },
  });

  const handleSignOut = () => {
    setIsSigningOut(true);
    logout();
  };

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleSignOut}
      disabled={isSigningOut}
    >
      {isSigningOut ? 'Signing out...' : 'Sign out'}
    </Button>
  );
}
