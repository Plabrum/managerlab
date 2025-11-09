'use client';

import { use } from 'react';
import { ObjectActions } from '@/components/object-detail';
import { BrandFields } from '@/components/brand-detail';
import { useBrandsIdGetBrandSuspense } from '@/openapi/brands/brands';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType, ObjectTypes } from '@/openapi/ariveAPI.schemas';
import { useAuth } from '@/components/providers/auth-provider';
import { ObjectDetailTabs } from '@/components/object-detail-tabs';
import { TabsContent } from '@/components/ui/tabs';
import { ActivityFeed } from '@/components/activity/activity-feed';

export default function BrandDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
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
