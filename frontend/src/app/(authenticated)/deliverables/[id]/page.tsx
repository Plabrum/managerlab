'use client';

import { use } from 'react';
import { useDeliverablesIdGetDeliverableSuspense } from '@/openapi/deliverables/deliverables';
import { PageTopBar } from '@/components/page-topbar';
import { ObjectActions } from '@/components/object-detail';
import { useAuth } from '@/components/providers/auth-provider';
import { ActionGroupType, ObjectTypes } from '@/openapi/managerLab.schemas';
import { ObjectDetailTabs } from '@/components/object-detail-tabs';
import { TabsContent } from '@/components/ui/tabs';
import { ActivityFeed } from '@/components/activity/activity-feed';
import {
  DeliverableFields,
  DeliverableMediaApproval,
} from '@/components/deliverable-detail';

export default function DeliverableDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { user } = useAuth();

  // Type-safe deliverable with relations and actions
  const { data, refetch } = useDeliverablesIdGetDeliverableSuspense(id);

  return (
    <PageTopBar
      title={data.title}
      state={data.state}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.deliverable_actions}
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
          { value: 'media-approval', label: 'Media Approval' },
        ]}
        defaultTab="summary"
      >
        <TabsContent value="summary" className="space-y-6">
          <div className="space-y-6">
            {/* Two Column Grid */}
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* Left Column - Fields */}
              <DeliverableFields deliverable={data} />
            </div>
          </div>
        </TabsContent>

        <TabsContent value="activity">
          <ActivityFeed
            threadableType={ObjectTypes.deliverables}
            threadableId={id}
            currentUserId={user.id as string}
          />
        </TabsContent>

        <TabsContent value="media-approval" className="space-y-6">
          <DeliverableMediaApproval deliverable={data} onRefetch={refetch} />
        </TabsContent>
      </ObjectDetailTabs>
    </PageTopBar>
  );
}
