import { useParams } from '@tanstack/react-router';
import { PageTopBar } from '@/components/page-topbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useUsersUserIdGetUserSuspense } from '@/openapi/users/users';

export function UserDetailPage() {
  const { id } = useParams({ strict: false });
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
