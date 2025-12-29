import { useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useAuthLogoutLogoutUser } from '@/openapi/auth/auth';

export function LogoutButton() {
  const navigate = useNavigate();
  const [isSigningOut, setIsSigningOut] = useState(false);

  const { mutate: logout } = useAuthLogoutLogoutUser({
    mutation: {
      onSuccess: () => {
        navigate({ to: '/' });
      },
      onError: (error) => {
        console.error('Logout failed:', error);
        navigate({ to: '/' });
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
