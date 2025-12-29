import { useParams } from '@tanstack/react-router';
import { ActivityFeed } from '@/components/activity/activity-feed';
import { CampaignFields } from '@/components/campaign-detail';
import { ObjectActions, ObjectChildList } from '@/components/object-detail';
import { ObjectDetailTabs } from '@/components/object-detail-tabs';
import { PageTopBar } from '@/components/page-topbar';
import { useAuth } from '@/components/providers/auth-provider';
import { TabsContent } from '@/components/ui/tabs';
import { useEditAction } from '@/hooks/use-edit-action';
import { ActionGroupType, ObjectTypes } from '@/openapi/ariveAPI.schemas';
import { useCampaignsIdGetCampaignSuspense } from '@/openapi/campaigns/campaigns';

export function CampaignDetailPage() {
  const { id } = useParams({ from: '/_authenticated/campaigns/$id' });
  const { data, refetch } = useCampaignsIdGetCampaignSuspense(id);
  const { user } = useAuth();

  // URL parameter-based edit mode with permission checking
  const { isEditMode, openEdit, closeEdit } = useEditAction({
    actions: data.actions || [],
  });

  return (
    <PageTopBar
      title={data.name}
      state={data.state}
      actions={
        <ObjectActions
          data={data}
          actionGroup={ActionGroupType.campaign_actions}
          onRefetch={refetch}
          editMode={{
            isOpen: isEditMode,
            onOpen: openEdit,
            onClose: closeEdit,
          }}
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
              parentActions={data.actions}
              parentObjectId={id}
              title="Deliverables"
              displayFields={['platforms', 'posting_date', 'deliverable_type']}
              onActionComplete={refetch}
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
