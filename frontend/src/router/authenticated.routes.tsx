import { createRoute, lazyRouteComponent } from '@tanstack/react-router';
import { z } from 'zod';
import { authenticatedLayoutRoute } from './layout.routes';

// Common search schema for detail pages
const detailSearchSchema = z.object({
  edit: z.boolean().optional(),
  tab: z.enum(['summary', 'activity']).optional().default('summary'),
});

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
  component: lazyRouteComponent(
    () => import('@/pages/dashboard/dashboard-list-page'),
    'DashboardPage'
  ),
});

export const dashboardDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/dashboard/$id',
  component: lazyRouteComponent(
    () => import('@/pages/dashboard/dashboard-detail-page'),
    'DashboardDetailPage'
  ),
  validateSearch: detailSearchSchema,
});

// ============================================================================
// Campaigns Routes
// ============================================================================
export const campaignsIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/campaigns',
  component: lazyRouteComponent(
    () => import('@/pages/campaigns/campaigns-list-page'),
    'CampaignsPage'
  ),
});

export const campaignDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/campaigns/$id',
  component: lazyRouteComponent(
    () => import('@/pages/campaigns/campaign-detail-page'),
    'CampaignDetailPage'
  ),
  validateSearch: detailSearchSchema,
});

// ============================================================================
// Brands Routes
// ============================================================================
export const brandsIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/brands',
  component: lazyRouteComponent(
    () => import('@/pages/brands/brands-list-page'),
    'BrandsPage'
  ),
});

export const brandDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/brands/$id',
  component: lazyRouteComponent(
    () => import('@/pages/brands/brand-detail-page'),
    'BrandDetailPage'
  ),
  validateSearch: detailSearchSchema,
});

// ============================================================================
// Brand Contacts Routes
// ============================================================================
export const brandcontactsIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/brandcontacts',
  component: lazyRouteComponent(
    () => import('@/pages/brandcontacts/brandcontacts-list-page'),
    'BrandContactsPage'
  ),
});

export const brandcontactDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/brandcontacts/$id',
  component: lazyRouteComponent(
    () => import('@/pages/brandcontacts/brandcontact-detail-page'),
    'BrandContactDetailPage'
  ),
  validateSearch: detailSearchSchema,
});

// ============================================================================
// Deliverables Routes
// ============================================================================
export const deliverablesIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/deliverables',
  component: lazyRouteComponent(
    () => import('@/pages/deliverables/deliverables-list-page'),
    'DeliverablesPage'
  ),
});

export const deliverableDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/deliverables/$id',
  component: lazyRouteComponent(
    () => import('@/pages/deliverables/deliverable-detail-page'),
    'DeliverableDetailPage'
  ),
  validateSearch: detailSearchSchema,
});

// ============================================================================
// Invoices Routes
// ============================================================================
export const invoicesIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/invoices',
  component: lazyRouteComponent(
    () => import('@/pages/invoices/invoices-list-page'),
    'InvoicesPage'
  ),
});

export const invoiceDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/invoices/$id',
  component: lazyRouteComponent(
    () => import('@/pages/invoices/invoice-detail-page'),
    'InvoiceDetailPage'
  ),
  validateSearch: detailSearchSchema,
});

// ============================================================================
// Media Routes
// ============================================================================
export const mediaIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/media',
  component: lazyRouteComponent(
    () => import('@/pages/media/media-list-page'),
    'MediaPage'
  ),
});

export const mediaDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/media/$id',
  component: lazyRouteComponent(
    () => import('@/pages/media/media-detail-page'),
    'MediaDetailPage'
  ),
  validateSearch: detailSearchSchema,
});

// ============================================================================
// Roster Routes
// ============================================================================
export const rosterIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/roster',
  component: lazyRouteComponent(
    () => import('@/pages/roster/roster-list-page'),
    'RosterPage'
  ),
});

export const rosterDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/roster/$id',
  component: lazyRouteComponent(
    () => import('@/pages/roster/roster-detail-page'),
    'RosterDetailPage'
  ),
  validateSearch: detailSearchSchema,
});

// ============================================================================
// Users Routes
// ============================================================================
export const usersIndexRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/users',
  component: lazyRouteComponent(
    () => import('@/pages/users/users-list-page'),
    'UsersPage'
  ),
});

export const userDetailRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/users/$id',
  component: lazyRouteComponent(
    () => import('@/pages/users/user-detail-page'),
    'UserDetailPage'
  ),
  validateSearch: detailSearchSchema,
});

// ============================================================================
// Settings Routes
// ============================================================================
export const settingsTeamRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/settings/team/$id',
  component: lazyRouteComponent(
    () => import('@/pages/settings/team-settings-page'),
    'TeamSettingsPage'
  ),
});

export const settingsUserRoute = createRoute({
  getParentRoute: () => authenticatedLayoutRoute,
  path: '/settings/user/$id',
  component: lazyRouteComponent(
    () => import('@/pages/settings/user-settings-page'),
    'UserSettingsPage'
  ),
});
