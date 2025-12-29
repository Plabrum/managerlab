import { redirect } from '@tanstack/react-router';
import { teamsListTeams } from '@/openapi/teams/teams';
import { usersCurrentUserGetCurrentUser } from '@/openapi/users/users';

/**
 * Clear the session cookie when logging out or on auth errors
 */
export function clearSession() {
  document.cookie =
    'session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax';
}

/**
 * Require authentication for a route.
 * Fetches user and teams data, handles errors, and redirects as needed.
 *
 * @param location - Current route location
 * @returns User and teams data
 * @throws Redirect if authentication fails or onboarding is needed
 */
export async function requireAuth(location: { pathname: string }) {
  try {
    // Fetch user and teams in parallel
    const [user, teams] = await Promise.all([
      usersCurrentUserGetCurrentUser(),
      teamsListTeams(),
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
