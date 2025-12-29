import {
  createRoute,
  lazyRouteComponent,
  redirect,
} from '@tanstack/react-router';
import { z } from 'zod';
import { publicLayoutRoute } from './layout.routes';
import { rootRoute } from './root.route';

// ============================================================================
// Home Route (/) - Attached directly to root, not public layout
// ============================================================================
export const homeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: lazyRouteComponent(() => import('@/pages/home-page'), 'HomePage'),
  beforeLoad: () => {
    // Check for session cookie
    const hasSession =
      document.cookie.includes('session=') &&
      !document.cookie.includes('session=null') &&
      !document.cookie.includes('session=;');

    if (hasSession) {
      throw redirect({ to: '/dashboard', replace: true });
    }
  },
});

// ============================================================================
// Public Auth Routes
// ============================================================================
const authSearchSchema = z.object({
  'sign-up': z.string().optional(),
});

export const authIndexRoute = createRoute({
  getParentRoute: () => publicLayoutRoute,
  path: '/auth',
  component: lazyRouteComponent(
    () => import('@/pages/auth/auth-page'),
    'AuthContent'
  ),
  validateSearch: authSearchSchema,
});

export const authExpireRoute = createRoute({
  getParentRoute: () => publicLayoutRoute,
  path: '/auth/expire',
  beforeLoad: () => {
    // Clear session cookie on client side
    document.cookie =
      'session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Lax';
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
});
