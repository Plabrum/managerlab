'use client';

import { use } from 'react';
import { ObjectActions, ObjectChildList } from '@/components/object-detail';
import { CampaignFields } from '@/components/campaign-detail';
import { useCampaignsIdGetCampaignSuspense } from '@/openapi/campaigns/campaigns';
import { PageTopBar } from '@/components/page-topbar';
import { ActionGroupType, ObjectTypes } from '@/openapi/managerLab.schemas';
import { useAuth } from '@/components/providers/auth-provider';
import { ObjectDetailTabs } from '@/components/object-detail-tabs';
import { TabsContent } from '@/components/ui/tabs';
import { ActivityFeed } from '@/components/activity/activity-feed';

export default function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { user } = useAuth();

  const { data, refetch } = useCampaignsIdGetCampaignSuspense(id);

  return (
    <PageTopBar
      title={data.name}
      state={data.state}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.campaign_actions}
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
              <CampaignFields campaign={data} />
            </div>

            {/* Deliverables Section */}
            <ObjectChildList
              objectType={ObjectTypes.deliverables}
              filterColumn="campaign_id"
              filterValue={id}
              title="Deliverables"
              displayFields={['platforms', 'posting_date', 'deliverable_type']}
            />
          </div>
        </TabsContent>

        <TabsContent value="activity">
          <ActivityFeed
            threadableType={ObjectTypes.campaigns}
            threadableId={id}
            currentUserId={user.id as string}
          />
        </TabsContent>
      </ObjectDetailTabs>
    </PageTopBar>
  );
}
