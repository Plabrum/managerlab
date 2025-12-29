import { createRouter } from '@tanstack/react-router';
import {
  onboardingRoute,
  dashboardIndexRoute,
  dashboardDetailRoute,
  campaignsIndexRoute,
  campaignDetailRoute,
  brandsIndexRoute,
  brandDetailRoute,
  brandcontactsIndexRoute,
  brandcontactDetailRoute,
  deliverablesIndexRoute,
  deliverableDetailRoute,
  invoicesIndexRoute,
  invoiceDetailRoute,
  mediaIndexRoute,
  mediaDetailRoute,
  rosterIndexRoute,
  rosterDetailRoute,
  usersIndexRoute,
  userDetailRoute,
  settingsTeamRoute,
  settingsUserRoute,
} from './authenticated.routes';
import { publicLayoutRoute, authenticatedLayoutRoute } from './layout.routes';
import {
  homeRoute,
  authIndexRoute,
  authExpireRoute,
  magicLinkVerifyRoute,
  landingRoute,
  errorRoute,
  inviteAcceptRoute,
} from './public.routes';
import { rootRoute } from './root.route';

// ============================================================================
// Route Tree Assembly
// ============================================================================
export const routeTree = rootRoute.addChildren([
  // Home route (directly under root)
  homeRoute,

  // Public routes (under public layout)
  publicLayoutRoute.addChildren([
    authIndexRoute,
    authExpireRoute,
    magicLinkVerifyRoute,
    landingRoute,
    errorRoute,
    inviteAcceptRoute,
  ]),

  // Authenticated routes (under authenticated layout)
  authenticatedLayoutRoute.addChildren([
    onboardingRoute,
    dashboardIndexRoute,
    dashboardDetailRoute,
    campaignsIndexRoute,
    campaignDetailRoute,
    brandsIndexRoute,
    brandDetailRoute,
    brandcontactsIndexRoute,
    brandcontactDetailRoute,
    deliverablesIndexRoute,
    deliverableDetailRoute,
    invoicesIndexRoute,
    invoiceDetailRoute,
    mediaIndexRoute,
    mediaDetailRoute,
    rosterIndexRoute,
    rosterDetailRoute,
    usersIndexRoute,
    userDetailRoute,
    settingsTeamRoute,
    settingsUserRoute,
  ]),
]);

// ============================================================================
// Router Instance
// ============================================================================
export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
});

// ============================================================================
// TypeScript Type Registration
// ============================================================================
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
