import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import ErrorPage from '@/routes/_public/error';
import { PageTopBar } from '@/components/page-topbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useUsersUserIdGetUserSuspense } from '@/openapi/users/users';

const searchSchema = z.object({
  edit: z.boolean().optional(),
  tab: z.enum(['summary', 'activity']).optional().default('summary'),
});

export const Route = createFileRoute('/_authenticated/users/$id')({
  component: UserDetailPage,
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

function UserDetailPage() {
  const { id } = Route.useParams();

  const { data } = useUsersUserIdGetUserSuspense(Number(id));

  return (
    <PageTopBar title={data.name} state={data.state}>
      <div className="container mx-auto space-y-6 p-6">
        <Card>
          <CardHeader>
            <CardTitle>User Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-muted-foreground text-sm font-medium">
                Email
              </label>
              <p className="text-sm">{data.email}</p>
            </div>
            <div>
              <label className="text-muted-foreground text-sm font-medium">
                Email Verified
              </label>
              <p className="text-sm">{data.email_verified ? 'Yes' : 'No'}</p>
            </div>
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
