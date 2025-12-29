import { useParams } from '@tanstack/react-router';
import { PageTopBar } from '@/components/page-topbar';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useBrandsContactsIdGetBrandContactSuspense } from '@/openapi/brands/brands';

export function BrandContactDetailPage() {
  const { id } = useParams({ from: '/_authenticated/brandcontacts/$id' });
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
              <div className="text-muted-foreground text-sm font-medium">
                First Name
              </div>
              <p className="text-sm">{data.first_name}</p>
            </div>
            <div>
              <div className="text-muted-foreground text-sm font-medium">
                Last Name
              </div>
              <p className="text-sm">{data.last_name}</p>
            </div>
            {data.email && (
              <div>
                <div className="text-muted-foreground text-sm font-medium">
                  Email
                </div>
                <p className="text-sm">{data.email}</p>
              </div>
            )}
            {data.phone && (
              <div>
                <div className="text-muted-foreground text-sm font-medium">
                  Phone
                </div>
                <p className="text-sm">{data.phone}</p>
              </div>
            )}
            {data.notes && (
              <div>
                <div className="text-muted-foreground text-sm font-medium">
                  Notes
                </div>
                <p className="text-sm">{data.notes}</p>
              </div>
            )}
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
