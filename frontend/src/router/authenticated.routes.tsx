import { createRoute, lazyRouteComponent } from '@tanstack/react-router';
import { RouteError } from '@/components/route-error';
import { PageSkeleton } from '@/components/skeletons';
import { authenticatedLayoutRoute } from './layout.routes';

// ============================================================================
// Onboarding
// ============================================================================
export const onboardingRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/onboarding',
  component: lazyRouteComponent(
    () => import('@/pages/onboarding-page'),
    'OnboardingPage'
  ),
});

// ============================================================================
// Dashboard Routes
// ============================================================================
export const dashboardIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/dashboard',
  pendingComponent: PageSkeleton,
  component: lazyRouteComponent(
    () => import('@/pages/dashboard/dashboard-list-page'),
    'DashboardPage'
  ),
});

export const dashboardDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/dashboard/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/dashboard/dashboard-detail-page'),
    'DashboardDetailPage'
  ),
});

// ============================================================================
// Campaigns Routes
// ============================================================================
export const campaignsIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/campaigns',
  pendingComponent: PageSkeleton,
  component: lazyRouteComponent(
    () => import('@/pages/campaigns/campaigns-list-page'),
    'CampaignsPage'
  ),
});

export const campaignDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/campaigns/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/campaigns/campaign-detail-page'),
    'CampaignDetailPage'
  ),
});

// ============================================================================
// Brands Routes
// ============================================================================
export const brandsIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/brands',
  pendingComponent: PageSkeleton,
  component: lazyRouteComponent(
    () => import('@/pages/brands/brands-list-page'),
    'BrandsPage'
  ),
});

export const brandDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/brands/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/brands/brand-detail-page'),
    'BrandDetailPage'
  ),
});

// ============================================================================
// Brand Contacts Routes
// ============================================================================
export const brandcontactsIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/brandcontacts',
  pendingComponent: PageSkeleton,
  component: lazyRouteComponent(
    () => import('@/pages/brandcontacts/brandcontacts-list-page'),
    'BrandContactsPage'
  ),
});

export const brandcontactDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/brandcontacts/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/brandcontacts/brandcontact-detail-page'),
    'BrandContactDetailPage'
  ),
});

// ============================================================================
// Deliverables Routes
// ============================================================================
export const deliverablesIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/deliverables',
  pendingComponent: PageSkeleton,
  component: lazyRouteComponent(
    () => import('@/pages/deliverables/deliverables-list-page'),
    'DeliverablesPage'
  ),
});

export const deliverableDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/deliverables/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/deliverables/deliverable-detail-page'),
    'DeliverableDetailPage'
  ),
});

// ============================================================================
// Invoices Routes
// ============================================================================
export const invoicesIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/invoices',
  pendingComponent: PageSkeleton,
  component: lazyRouteComponent(
    () => import('@/pages/invoices/invoices-list-page'),
    'InvoicesPage'
  ),
});

export const invoiceDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/invoices/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/invoices/invoice-detail-page'),
    'InvoiceDetailPage'
  ),
});

// ============================================================================
// Media Routes
// ============================================================================
export const mediaIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/media',
  pendingComponent: PageSkeleton,
  component: lazyRouteComponent(
    () => import('@/pages/media/media-list-page'),
    'MediaPage'
  ),
});

export const mediaDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/media/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/media/media-detail-page'),
    'MediaDetailPage'
  ),
});

// ============================================================================
// Roster Routes
// ============================================================================
export const rosterIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/roster',
  pendingComponent: PageSkeleton,
  component: lazyRouteComponent(
    () => import('@/pages/roster/roster-list-page'),
    'RosterPage'
  ),
});

export const rosterDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/roster/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/roster/roster-detail-page'),
    'RosterDetailPage'
  ),
});

// ============================================================================
// Users Routes
// ============================================================================
export const usersIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/users',
  pendingComponent: PageSkeleton,
  component: lazyRouteComponent(
    () => import('@/pages/users/users-list-page'),
    'UsersPage'
  ),
});

export const userDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/users/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/users/user-detail-page'),
    'UserDetailPage'
  ),
});

// ============================================================================
// Settings Routes
// ============================================================================
export const settingsTeamRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/settings/team/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/settings/team-settings-page'),
    'TeamSettingsPage'
  ),
});

export const settingsUserRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/settings/user/$id',
  pendingComponent: PageSkeleton,
  errorComponent: RouteError,
  component: lazyRouteComponent(
    () => import('@/pages/settings/user-settings-page'),
    'UserSettingsPage'
  ),
});
