import { useParams } from '@tanstack/react-router';
import { ActivityFeed } from '@/components/activity/activity-feed';
import { BrandFields } from '@/components/brand-detail';
import { ObjectActions } from '@/components/object-detail';
import { ObjectDetailTabs } from '@/components/object-detail-tabs';
import { PageTopBar } from '@/components/page-topbar';
import { useAuth } from '@/components/providers/auth-provider';
import { TabsContent } from '@/components/ui/tabs';
import { ActionGroupType, ObjectTypes } from '@/openapi/ariveAPI.schemas';
import { useBrandsIdGetBrandSuspense } from '@/openapi/brands/brands';

export function BrandDetailPage() {
  const { id } = useParams({ from: '/_authenticated/brands/$id' });
  const { data, refetch } = useBrandsIdGetBrandSuspense(id);
  const { user } = useAuth();

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
