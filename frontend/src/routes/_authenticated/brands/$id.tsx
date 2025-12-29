import { createFileRoute } from '@tanstack/react-router';
import { z } from 'zod';
import ErrorPage from '@/routes/_public/error';
import { ActivityFeed } from '@/components/activity/activity-feed';
import { BrandFields } from '@/components/brand-detail';
import { ObjectActions } from '@/components/object-detail';
import { ObjectDetailTabs } from '@/components/object-detail-tabs';
import { PageTopBar } from '@/components/page-topbar';
import { useAuth } from '@/components/providers/auth-provider';
import { TabsContent } from '@/components/ui/tabs';
import { ActionGroupType, ObjectTypes } from '@/openapi/ariveAPI.schemas';
import { useBrandsIdGetBrandSuspense } from '@/openapi/brands/brands';

const searchSchema = z.object({
  edit: z.boolean().optional(),
  tab: z.enum(['summary', 'activity']).optional().default('summary'),
});

export const Route = createFileRoute('/_authenticated/brands/$id')({
  component: BrandDetailPage,
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

function BrandDetailPage() {
  const { id } = Route.useParams();
  const { user } = useAuth();

  const { data, refetch } = useBrandsIdGetBrandSuspense(id);

  return (
    <PageTopBar
      title={data.name}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.brand_actions}
          onRefetch={refetch}
        />
      }
    >
      <ObjectDetailTabs
        tabs={[
          { value: 'summary', label: 'Summary' },
          {
            value: 'activity',
            label: 'Activity',
            unreadCount: data.thread?.unread_count,
          },
        ]}
        defaultTab="summary"
      >
        <TabsContent value="summary" className="space-y-6">
          <div className="space-y-6">
            {/* Two Column Grid */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* Left Column - Fields */}
              <BrandFields brand={data} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="activity">
          <ActivityFeed
            threadableType={ObjectTypes.brands}
            threadableId={id}
            currentUserId={user.id as string}
          />
        </TabsContent>
      </ObjectDetailTabs>
    </PageTopBar>
  );
}
