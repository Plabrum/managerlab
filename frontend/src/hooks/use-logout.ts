import { useNavigate } from '@tanstack/react-router';
import { queryClient } from '@/lib/tanstack-query-provider';
import { useAuthLogoutLogoutUser } from '@/openapi/auth/auth';

/**
 * Shared logout hook that handles:
 * - Calling the logout API endpoint
 * - Clearing the React Query cache
 * - Navigating to the home page
 */
export function useLogout() {
  const navigate = useNavigate();

  const { mutate: logout, isPending } = useAuthLogoutLogoutUser({
    mutation: {
      onSuccess: () => {
        // Clear all cached queries on logout
        queryClient.clear();
        navigate({ to: '/', replace: true });
      },
      onError: (error) => {
        console.error('Logout failed:', error);
        // Clear cache and navigate even on error
        queryClient.clear();
        navigate({ to: '/', replace: true });
      },
    },
  });

  return {
    logout,
    isLoggingOut: isPending,
  };
}
