import { Button } from '@/components/ui/button';
import { useLogout } from '@/hooks/use-logout';

export function LogoutButton() {
  const { logout, isLoggingOut } = useLogout();

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={() => logout()}
      disabled={isLoggingOut}
    >
      {isLoggingOut ? 'Signing out...' : 'Sign out'}
    </Button>
  );
}
