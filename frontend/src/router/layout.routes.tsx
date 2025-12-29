import { createRoute } from '@tanstack/react-router';
import { rootRoute } from './root.route';
import { AuthLoading } from '@/components/auth-loading';
import { AuthenticatedLayout } from '@/layouts/authenticated-layout';
import { PublicLayout } from '@/layouts/public-layout';
import { requireAuth } from '@/lib/auth-loader';

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
// ============================================================================
export const authenticatedLayoutRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: '_authenticated',
  loader: async ({ location }) => requireAuth(location),
  pendingComponent: AuthLoading,
  component: () => {
    const data = authenticatedLayoutRoute.useLoaderData();
    return <AuthenticatedLayout user={data.user} teams={data.teams} />;
  },
});
