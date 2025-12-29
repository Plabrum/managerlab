import { createRoute } from '@tanstack/react-router';
import { AuthenticatedLayout } from '@/layouts/authenticated-layout';
import { PublicLayout } from '@/layouts/public-layout';
import { requireAuth } from '@/lib/auth-loader';
import { rootRoute } from './root.route';

// ============================================================================
// Public Layout Route (no authentication required)
// ============================================================================
export const publicLayoutRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: '_public',
  component: PublicLayout,
});

// ============================================================================
// Authenticated Layout Route (requires authentication)
//
// Auth data is aggressively cached (5 minutes) in the loader, so this
// typically doesn't show a loading state after the first navigation.
// Page-specific skeletons (in child routes) handle loading states for page data.
// ============================================================================
export const authenticatedLayoutRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: '_authenticated',
  loader: async ({ location }) => requireAuth(location),
  component: () => {
    const data = authenticatedLayoutRoute.useLoaderData();
    return <AuthenticatedLayout user={data.user} teams={data.teams} />;
  },
});
