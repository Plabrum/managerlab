import { createRootRoute } from '@tanstack/react-router';
import { NotFoundPage } from '@/components/not-found-page';
import { RootLayout } from '@/layouts/root-layout';
import { ErrorPage } from '@/pages/error-page';

export const rootRoute = createRootRoute({
  component: RootLayout,
  notFoundComponent: NotFoundPage,
  errorComponent: ErrorPage,
});
