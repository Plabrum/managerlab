import { useParams } from '@tanstack/react-router';
import { PageTopBar } from '@/components/page-topbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useUsersUserIdGetUserSuspense } from '@/openapi/users/users';

export function UserDetailPage() {
  const { id } = useParams({ from: '/_authenticated/users/$id' });
  const { data } = useUsersUserIdGetUserSuspense(id);

  return (
    <PageTopBar title={data.name} state={data.state}>
      <div className="container mx-auto space-y-6 p-6">
        <Card>
          <CardHeader>
            <CardTitle>User Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-muted-foreground text-sm font-medium">
                Email
              </div>
              <p className="text-sm">{data.email}</p>
            </div>
            <div>
              <div className="text-muted-foreground text-sm font-medium">
                Email Verified
              </div>
              <p className="text-sm">{data.email_verified ? 'Yes' : 'No'}</p>
            </div>
            <div>
              <div className="text-muted-foreground text-sm font-medium">
                Created At
              </div>
              <p className="text-sm">
                {new Date(data.created_at).toLocaleDateString()}
              </p>
            </div>
            <div>
              <div className="text-muted-foreground text-sm font-medium">
                Updated At
              </div>
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
