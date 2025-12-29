import { redirect } from '@tanstack/react-router';
import { getTeamsListTeamsQueryOptions } from '@/openapi/teams/teams';
import { getUsersCurrentUserGetCurrentUserQueryOptions } from '@/openapi/users/users';
import { queryClient } from './tanstack-query-provider';

/**
 * Clear the session cookie when logging out or on auth errors
 */
export function clearSession() {
  const isSecure = window.location.protocol === 'https:';
  const secureFlag = isSecure ? ' Secure;' : '';
  document.cookie = `session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;${secureFlag} SameSite=Lax`;
}

/**
 * Require authentication for a route.
 * Fetches user and teams data, handles errors, and redirects as needed.
 *
 * Uses React Query with aggressive caching (5 minutes staleTime) to avoid
 * re-fetching auth data on every route navigation.
 *
 * @param location - Current route location
 * @returns User and teams data
 * @throws Redirect if authentication fails or onboarding is needed
 */
export async function requireAuth(location: { pathname: string }) {
  try {
    // Fetch user and teams using React Query with aggressive caching
    // This ensures we only fetch auth data once per session, not on every route change
    const [user, teams] = await Promise.all([
      queryClient.ensureQueryData({
        ...getUsersCurrentUserGetCurrentUserQueryOptions(),
        staleTime: 5 * 60 * 1000, // Cache for 5 minutes
      }),
      queryClient.ensureQueryData({
        ...getTeamsListTeamsQueryOptions(),
        staleTime: 5 * 60 * 1000, // Cache for 5 minutes
      }),
    ]);

    // Redirect to onboarding if user has no teams (unless already on onboarding)
    if (teams.length === 0 && !location.pathname.includes('/onboarding')) {
      throw redirect({ to: '/onboarding', replace: true });
    }

    return { user, teams };
  } catch (error) {
    // Handle authentication errors
    if (error && typeof error === 'object' && 'status' in error) {
      const status = (error as { status: number }).status;
      if (status === 401) {
        clearSession();
        throw redirect({ to: '/auth', replace: true });
      }
    }

    // Handle other errors (including redirects being re-thrown)
    throw error;
  }
}
