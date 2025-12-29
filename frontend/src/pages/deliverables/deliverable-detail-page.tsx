import { useParams } from '@tanstack/react-router';
import { ActivityFeed } from '@/components/activity/activity-feed';
import {
  DeliverableFields,
  DeliverableMediaApproval,
} from '@/components/deliverable-detail';
import { ObjectActions } from '@/components/object-detail';
import { ObjectDetailTabs } from '@/components/object-detail-tabs';
import { PageTopBar } from '@/components/page-topbar';
import { useAuth } from '@/components/providers/auth-provider';
import { TabsContent } from '@/components/ui/tabs';
import { ActionGroupType, ObjectTypes } from '@/openapi/ariveAPI.schemas';
import { useDeliverablesIdGetDeliverableSuspense } from '@/openapi/deliverables/deliverables';

export function DeliverableDetailPage() {
  const { id } = useParams({ from: '/_authenticated/deliverables/$id' });
  const { data, refetch } = useDeliverablesIdGetDeliverableSuspense(id);
  const { user } = useAuth();

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
