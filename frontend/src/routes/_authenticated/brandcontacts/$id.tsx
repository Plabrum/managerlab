import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import { PageTopBar } from '@/components/page-topbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useBrandsContactsIdGetBrandContactSuspense } from '@/openapi/brands/brands';
import ErrorPage from '@/routes/_public/error';

const searchSchema = z.object({
  edit: z.boolean().optional(),
  tab: z.enum(['summary', 'activity']).optional().default('summary'),
});

export const Route = createFileRoute('/_authenticated/brandcontacts/$id')({
  component: BrandContactDetailPage,
  validateSearch: searchSchema,
  errorComponent: ({ error }) => {
    if (
      error &&
      typeof error === 'object' &&
      'status' in error &&
      error.status === 404
    ) {
      return <ErrorPage />;
    }
    throw error;
  },
});

function BrandContactDetailPage() {
  // ✅ Type-safe params - no path needed!
  const { id } = Route.useParams();

  const { data } = useBrandsContactsIdGetBrandContactSuspense(id);

  return (
    <PageTopBar title={`${data.first_name} ${data.last_name}`}>
      <div className="container mx-auto space-y-6 p-6">
        <Card>
          <CardHeader>
            <CardTitle>Contact Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-muted-foreground text-sm font-medium">
                First Name
              </label>
              <p className="text-sm">{data.first_name}</p>
            </div>
            <div>
              <label className="text-muted-foreground text-sm font-medium">
                Last Name
              </label>
              <p className="text-sm">{data.last_name}</p>
            </div>
            {data.email && (
              <div>
                <label className="text-muted-foreground text-sm font-medium">
                  Email
                </label>
                <p className="text-sm">{data.email}</p>
              </div>
            )}
            {data.phone && (
              <div>
                <label className="text-muted-foreground text-sm font-medium">
                  Phone
                </label>
                <p className="text-sm">{data.phone}</p>
              </div>
            )}
            {data.notes && (
              <div>
                <label className="text-muted-foreground text-sm font-medium">
                  Notes
                </label>
                <p className="text-sm">{data.notes}</p>
              </div>
            )}
            <div>
              <label className="text-muted-foreground text-sm font-medium">
                Created At
              </label>
              <p className="text-sm">
                {new Date(data.created_at).toLocaleDateString()}
              </p>
            </div>
            <div>
              <label className="text-muted-foreground text-sm font-medium">
                Updated At
              </label>
              <p className="text-sm">
                {new Date(data.updated_at).toLocaleDateString()}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageTopBar>
  );
}
