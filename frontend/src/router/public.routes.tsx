import {
  createRoute,
  lazyRouteComponent,
  redirect,
} from '@tanstack/react-router';
import { deleteCookie } from '@/lib/cookies';
import { queryClient } from '@/lib/tanstack-query-provider';
import { getUsersCurrentUserGetCurrentUserQueryOptions } from '@/openapi/users/users';
import { publicLayoutRoute } from './layout.routes';
import { rootRoute } from './root.route';

// ============================================================================
// Home Route (/) - Attached directly to root, not public layout
// ============================================================================
export const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: lazyRouteComponent(() => import('@/pages/home-page'), 'HomePage'),
  loader: async () => {
    // Check if user is authenticated by calling the API
    // The session cookie (HttpOnly) is sent automatically with the request
    // This query is cached with session lifetime (Infinity) so it's fast
    const user = await queryClient
      .fetchQuery({
        ...getUsersCurrentUserGetCurrentUserQueryOptions(),
        retry: false,
      })
      .catch(() => null);

    // If user is authenticated, redirect to dashboard
    if (user) {
      throw redirect({ to: '/dashboard', replace: true });
    }

    // Otherwise, show the landing page
    return null;
  },
});

// ============================================================================
// Public Auth Routes
// ============================================================================
export const authIndexRoute = createRoute({
  getParentRoute: () => publicLayoutRoute,
  path: '/auth',
  component: lazyRouteComponent(
    () => import('@/pages/auth/auth-page'),
    'AuthContent'
  ),
});

export const authExpireRoute = createRoute({
  getParentRoute: () => publicLayoutRoute,
  path: '/auth/expire',
  beforeLoad: () => {
    // Clear session cookie on client side
    deleteCookie('session');
    throw redirect({ to: '/auth', replace: true });
  },
});

export const magicLinkVerifyRoute = createRoute({
  getParentRoute: () => publicLayoutRoute,
  path: '/auth/magic-link/verify',
  component: lazyRouteComponent(
    () => import('@/pages/auth/magic-link-verify-page'),
    'MagicLinkVerifyPage'
  ),
  validateSearch: (search: Record<string, unknown>) => ({
    token: (search.token as string) || undefined,
  }),
});

// ============================================================================
// Other Public Routes
// ============================================================================
export const landingRoute = createRoute({
  getParentRoute: () => publicLayoutRoute,
  path: '/landing',
  component: lazyRouteComponent(
    () => import('@/pages/landing-page'),
    'Landing'
  ),
});

export const errorRoute = createRoute({
  getParentRoute: () => publicLayoutRoute,
  path: '/error',
  component: lazyRouteComponent(
    () => import('@/pages/error-page'),
    'ErrorPage'
  ),
});

export const inviteAcceptRoute = createRoute({
  getParentRoute: () => publicLayoutRoute,
  path: '/invite/accept',
  component: lazyRouteComponent(
    () => import('@/pages/invite-accept-page'),
    'InviteAcceptPage'
  ),
  validateSearch: (search: Record<string, unknown>) => ({
    token: (search.token as string) || undefined,
  }),
});
